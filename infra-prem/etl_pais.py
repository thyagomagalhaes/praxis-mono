#!/usr/bin/env python3
"""
ETL IBGE -> PostGIS (tabela db_msterritorializacao.tb_pais)

Extract:
  - API de Localidades v1: /localidades/paises  (atributos, M49, ISO, regiões)
  - API de Malhas v4:      /malhas/paises       (geometria GeoJSON)
Transform:
  - normaliza atributos e associa a geometria ao país (M49 / ISO alpha-2 / alpha-3)
Load:
  - upsert idempotente (ON CONFLICT co_m49) em uma única transação
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
from typing import Any

import psycopg
import requests
from psycopg import sql
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

log = logging.getLogger("etl_pais")

# --------------------------------------------------------------------------- #
# Configuração
# --------------------------------------------------------------------------- #
IBGE_BASE = os.getenv("IBGE_BASE_URL", "https://servicodados.ibge.gov.br/api").rstrip("/")
URL_LOCALIDADES = f"{IBGE_BASE}/v1/localidades/paises"
URL_MALHAS = f"{IBGE_BASE}/v4/malhas/paises"
MALHA_QUALIDADE = os.getenv("IBGE_MALHA_QUALIDADE", "intermediaria")
MALHA_LOTE = os.getenv("IBGE_MALHA_LOTE", "0") == "1"  # endpoint em lote (404 na API v4 atual) - desligado
MALHA_URLS = [
    u.strip().rstrip("/")
    for u in os.getenv("IBGE_MALHA_URLS", f"{URL_MALHAS},{IBGE_BASE}/v3/malhas/paises").split(",")
    if u.strip()
]
MALHA_PAUSA = float(os.getenv("IBGE_MALHA_PAUSA", "0.15"))  # segundos entre requisições
MALHA_MAX_FALHAS_SEGUIDAS = int(os.getenv("IBGE_MALHA_MAX_FALHAS_SEGUIDAS", "15"))
ALLOW_SEM_GEOM = os.getenv("ALLOW_SEM_GEOM", "0") == "1"
# A API de malhas do IBGE só disponibiliza, no nível de país, a malha do Brasil (id "BR").
# Se o IBGE passar a oferecer outros países, basta ampliar a lista (ex.: "BR,AR,CL").
NE_HABILITADO = os.getenv("NE_HABILITADO", "1") == "1"  # complementa geometrias com Natural Earth
NE_RESOLUCAO = os.getenv("NE_RESOLUCAO", "50m")  # 110m | 50m | 10m
NE_URL = os.getenv(
    "NE_URL",
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
    f"ne_{NE_RESOLUCAO}_admin_0_countries.geojson",
)
NE_ARQUIVO = os.getenv("NE_ARQUIVO")  # caminho local de um GeoJSON do Natural Earth (tem prioridade sobre a URL)
FONTE_IBGE = f"IBGE Malhas v4 (qualidade={MALHA_QUALIDADE})"
FONTE_NE = f"Natural Earth admin_0_countries {NE_RESOLUCAO} (dominio publico)"
MALHA_PAISES = {x.strip().upper() for x in os.getenv("IBGE_MALHA_PAISES", "BR").split(",") if x.strip()}
MIN_PAISES = int(os.getenv("MIN_PAISES", "150"))  # trava de sanidade

SCHEMA = os.getenv("DB_SCHEMA", "db_msterritorializacao")
TABLE = "tb_pais"

DDL = [
    "CREATE EXTENSION IF NOT EXISTS postgis",
    "CREATE SCHEMA IF NOT EXISTS {schema}",
    """
    CREATE TABLE IF NOT EXISTS {schema}.{table} (
        co_m49                      smallint     PRIMARY KEY,
        co_iso_alpha2               char(2),
        co_iso_alpha3               char(3),
        no_pais                     text         NOT NULL,
        co_regiao_m49               smallint,
        no_regiao                   text,
        co_subregiao_m49            smallint,
        no_subregiao                text,
        co_regiao_intermediaria_m49 smallint,
        no_regiao_intermediaria     text,
        geom                        geometry(MultiPolygon, 4326),
        no_fonte_geom               text,
        dt_carga                    timestamptz  NOT NULL DEFAULT now()
    )
    """,
    "ALTER TABLE {schema}.{table} ADD COLUMN IF NOT EXISTS no_fonte_geom text",
    "CREATE INDEX IF NOT EXISTS {ix_geom} ON {schema}.{table} USING gist (geom)",
    "CREATE UNIQUE INDEX IF NOT EXISTS {ix_iso2} ON {schema}.{table} (co_iso_alpha2) WHERE co_iso_alpha2 IS NOT NULL",
]

UPSERT = """
INSERT INTO {schema}.{table} (
    co_m49, co_iso_alpha2, co_iso_alpha3, no_pais,
    co_regiao_m49, no_regiao, co_subregiao_m49, no_subregiao,
    co_regiao_intermediaria_m49, no_regiao_intermediaria, geom, no_fonte_geom, dt_carga
) VALUES (
    %(co_m49)s, %(co_iso_alpha2)s, %(co_iso_alpha3)s, %(no_pais)s,
    %(co_regiao_m49)s, %(no_regiao)s, %(co_subregiao_m49)s, %(no_subregiao)s,
    %(co_regiao_intermediaria_m49)s, %(no_regiao_intermediaria)s,
    ST_Multi(ST_CollectionExtract(
        ST_MakeValid(ST_SetSRID(ST_GeomFromGeoJSON(%(geom)s::text), 4326)), 3)),
    %(no_fonte_geom)s,
    now()
)
ON CONFLICT (co_m49) DO UPDATE SET
    co_iso_alpha2               = EXCLUDED.co_iso_alpha2,
    co_iso_alpha3               = EXCLUDED.co_iso_alpha3,
    no_pais                     = EXCLUDED.no_pais,
    co_regiao_m49               = EXCLUDED.co_regiao_m49,
    no_regiao                   = EXCLUDED.no_regiao,
    co_subregiao_m49            = EXCLUDED.co_subregiao_m49,
    no_subregiao                = EXCLUDED.no_subregiao,
    co_regiao_intermediaria_m49 = EXCLUDED.co_regiao_intermediaria_m49,
    no_regiao_intermediaria     = EXCLUDED.no_regiao_intermediaria,
    geom                        = COALESCE(EXCLUDED.geom, {schema}.{table}.geom),
    no_fonte_geom               = CASE WHEN EXCLUDED.geom IS NOT NULL THEN EXCLUDED.no_fonte_geom
                                       ELSE {schema}.{table}.no_fonte_geom END,
    dt_carga                    = now()
"""


# --------------------------------------------------------------------------- #
# Extract
# --------------------------------------------------------------------------- #
def make_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update({"Accept": "application/json", "User-Agent": "etl-pais-msterritorializacao/1.0"})
    return s


def extract_localidades(s: requests.Session) -> list[dict[str, Any]]:
    log.info("Extraindo localidades: %s", URL_LOCALIDADES)
    r = s.get(URL_LOCALIDADES, timeout=(10, 60))
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list):
        raise RuntimeError("Resposta inesperada da API de Localidades (esperava lista)")
    log.info("Localidades: %d países", len(data))
    return data


GEOJSON = "application/vnd.geo+json"
_TIPOS_GEO = {"FeatureCollection", "Feature", "Polygon", "MultiPolygon", "GeometryCollection"}

# Variações de parâmetros testadas na sondagem (a API de malhas é sensível a eles).
VARIANTES = {
    "enc+qualidade": lambda u: (u, {"formato": GEOJSON, "qualidade": MALHA_QUALIDADE}),
    "enc": lambda u: (u, {"formato": GEOJSON}),
    "raw+qualidade": lambda u: (f"{u}?formato={GEOJSON}&qualidade={MALHA_QUALIDADE}", None),
    "raw": lambda u: (f"{u}?formato={GEOJSON}", None),
}


def _geometrias(obj: Any) -> list[dict]:
    """Extrai geometrias de FeatureCollection / Feature / Geometry (ignora TopoJSON etc.)."""
    if not isinstance(obj, dict) or obj.get("type") not in _TIPOS_GEO:
        return []
    t = obj["type"]
    if t == "FeatureCollection":
        return [f["geometry"] for f in obj.get("features", []) if f.get("geometry")]
    if t == "Feature":
        return [obj["geometry"]] if obj.get("geometry") else []
    return [obj]


def _json(r: requests.Response) -> Any:
    try:
        return r.json()
    except ValueError:
        return None


def _snippet(r: requests.Response) -> str:
    return r.text[:200].replace("\n", " ").strip()


def _get_malha(s: requests.Session, base: str, ident: str, variante: str) -> requests.Response:
    url, params = VARIANTES[variante](f"{base}/{ident}")
    return s.get(url, params=params, timeout=(10, 120))


def extract_malha_lote(s: requests.Session) -> dict[str, dict]:
    """Malha de todos os países em uma chamada (opcional; o endpoint v4 atual responde 404)."""
    log.info("Extraindo malha (lote): %s", URL_MALHAS)
    url, params = VARIANTES["enc+qualidade"](URL_MALHAS)
    r = s.get(url, params=params, timeout=(10, 300))
    r.raise_for_status()
    out: dict[str, dict] = {}
    for f in (_json(r) or {}).get("features", []):
        code = str((f.get("properties") or {}).get("codarea", "")).strip().upper()
        if code and f.get("geometry"):
            out[code] = f["geometry"]
    log.info("Malha (lote): %d geometrias", len(out))
    return out


def _ids_pais(row: dict) -> list[str]:
    return [x for x in (row["co_iso_alpha2"], row["co_iso_alpha3"], f"{row['co_m49']:03d}") if x]


def descobrir_combo(s: requests.Session, rows: list[dict]) -> tuple[str, str] | None:
    """Sonda (base, variante de parâmetros) que funciona, testando com o Brasil."""
    alvo = next((r for r in rows if r["co_iso_alpha2"] == "BR"), rows[0])
    log.info("Sondando a API de malhas com %s (bases=%s)", alvo["no_pais"], MALHA_URLS)
    for base in MALHA_URLS:
        for variante in VARIANTES:
            for ident in _ids_pais(alvo):
                r = _get_malha(s, base, ident, variante)
                ok = r.status_code == 200 and bool(_geometrias(_json(r)))
                log.info("  %-4s %-14s id=%-4s -> HTTP %s %s",
                         base.split("/api/")[-1][:2], variante, ident, r.status_code,
                         "OK (GeoJSON)" if ok else _snippet(r))
                if ok:
                    log.info("Combinação escolhida: base=%s variante=%s", base, variante)
                    return base, variante
                time.sleep(0.2)
    return None


def extract_malha_pais(s: requests.Session, ids: list[str], combo: tuple[str, str],
                       tentativas: list[str] | None = None) -> dict | None:
    base, variante = combo
    for ident in ids:
        r = _get_malha(s, base, ident, variante)
        if tentativas is not None:
            tentativas.append(f"HTTP {r.status_code} {r.url} {'' if r.ok else _snippet(r)}")
        if r.status_code in (400, 404):
            continue
        r.raise_for_status()
        geoms = _geometrias(_json(r))
        if len(geoms) == 1:
            return geoms[0]
        if geoms:
            return {"type": "GeometryCollection", "geometries": geoms}
    return None


# --------------------------------------------------------------------------- #
# Transform
# --------------------------------------------------------------------------- #
def _m49(obj: Any) -> int | None:
    v = ((obj or {}).get("id") or {}).get("M49") if isinstance(obj, dict) else None
    try:
        return int(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def _iso(id_: dict, n: str) -> str | None:
    for k, v in (id_ or {}).items():
        if k.upper().endswith(f"ALPHA-{n}") and v:
            return str(v).strip().upper()
    return None


def transform(raw: dict[str, Any]) -> dict[str, Any]:
    id_ = raw.get("id") or {}
    sub = raw.get("sub-regiao") or {}
    reg = sub.get("regiao") or raw.get("regiao") or {}
    ri = raw.get("regiao-intermediaria") or {}
    try:
        m49 = int(id_.get("M49"))
    except (TypeError, ValueError):
        m49 = None
    return {
        "co_m49": m49,
        "co_iso_alpha2": _iso(id_, "2"),
        "co_iso_alpha3": _iso(id_, "3"),
        "no_pais": (raw.get("nome") or "").strip(),
        "co_regiao_m49": _m49(reg),
        "no_regiao": reg.get("nome"),
        "co_subregiao_m49": _m49(sub),
        "no_subregiao": sub.get("nome"),
        "co_regiao_intermediaria_m49": _m49(ri),
        "no_regiao_intermediaria": ri.get("nome") if isinstance(ri, dict) else None,
        "geom": None,
        "no_fonte_geom": None,
    }


def _ne_num(v: Any) -> int | None:
    try:
        n = int(float(str(v)))
    except (TypeError, ValueError):
        return None
    return n if n > 0 else None  # o Natural Earth usa -99 / -099 para "sem código"


def _ne_txt(v: Any) -> str | None:
    v = str(v or "").strip().upper()
    return v if v and v not in ("-99", "N/A") else None


def extract_natural_earth(s: requests.Session) -> dict[str, dict]:
    """Índice {'N:<M49>' | 'A3:<ISO3>' | 'A2:<ISO2>': geometria} a partir do admin_0_countries."""
    if NE_ARQUIVO:
        log.info("Lendo Natural Earth de arquivo: %s", NE_ARQUIVO)
        with open(NE_ARQUIVO, encoding="utf-8") as fh:
            fc = json.load(fh)
    else:
        log.info("Baixando Natural Earth: %s", NE_URL)
        r = s.get(NE_URL, timeout=(10, 300))
        r.raise_for_status()
        log.info("Natural Earth: %.1f MB", len(r.content) / 1e6)
        fc = r.json()
    if fc.get("type") != "FeatureCollection":
        raise RuntimeError("Arquivo do Natural Earth inesperado (esperava FeatureCollection)")

    idx: dict[str, dict] = {}
    n = 0
    for f in fc.get("features", []):
        geom = f.get("geometry")
        if not geom:
            continue
        n += 1
        pr = {str(k).upper(): v for k, v in (f.get("properties") or {}).items()}
        for k in ("ISO_N3_EH", "ISO_N3", "UN_A3"):
            if (v := _ne_num(pr.get(k))) is not None:
                idx.setdefault(f"N:{v}", geom)
        for k in ("ISO_A3_EH", "ISO_A3", "ADM0_ISO", "ADM0_A3"):
            if v := _ne_txt(pr.get(k)):
                idx.setdefault(f"A3:{v}", geom)
        for k in ("ISO_A2_EH", "ISO_A2"):
            if v := _ne_txt(pr.get(k)):
                idx.setdefault(f"A2:{v}", geom)
    log.info("Natural Earth: %d feições, %d chaves indexadas", n, len(idx))
    return idx


def aplicar_natural_earth(rows: list[dict], idx: dict[str, dict]) -> int:
    """Preenche geom dos países ainda sem geometria (casa por M49, depois ISO3, depois ISO2)."""
    aplicados = 0
    for row in rows:
        if row["geom"] is not None:
            continue
        chaves = [f"N:{row['co_m49']}", f"A3:{row['co_iso_alpha3']}", f"A2:{row['co_iso_alpha2']}"]
        geom = next((idx[k] for k in chaves if k in idx), None)
        if geom:
            row["geom"] = json.dumps(geom)
            row["no_fonte_geom"] = FONTE_NE
            aplicados += 1
    return aplicados


def attach_geometries(s: requests.Session, rows: list[dict], lote: dict[str, dict]) -> None:
    faltando: list[dict] = []
    for row in rows:
        keys = [f"{row['co_m49']:03d}", str(row["co_m49"]), row["co_iso_alpha2"] or "", row["co_iso_alpha3"] or ""]
        geom = next((lote[k] for k in keys if k and k in lote), None)
        if geom:
            row["geom"] = json.dumps(geom)
            row["no_fonte_geom"] = FONTE_IBGE
        else:
            faltando.append(row)

    sem_api = [r for r in faltando if (r["co_iso_alpha2"] or "") not in MALHA_PAISES]
    if sem_api:
        log.info("%d países sem malha disponível na API do IBGE (geom NULL); malha pedida só para: %s",
                 len(sem_api), ", ".join(sorted(MALHA_PAISES)))
    faltando = [r for r in faltando if (r["co_iso_alpha2"] or "") in MALHA_PAISES]

    if faltando:
        combo = descobrir_combo(s, faltando)
        if combo is None:
            msg = "API de malhas rejeitou todas as variações testadas (veja as linhas 'HTTP ...' acima)"
            if not ALLOW_SEM_GEOM:
                raise RuntimeError(msg + "; abortando antes da carga (ALLOW_SEM_GEOM=1 carrega só atributos)")
            log.error(msg)
        else:
            log.info("Buscando malha país a país: %d países", len(faltando))
            seguidas = 0
            for i, row in enumerate(faltando, 1):
                tentativas: list[str] = []
                geom = extract_malha_pais(s, _ids_pais(row), combo, tentativas)
                if geom:
                    row["geom"] = json.dumps(geom)
                    row["no_fonte_geom"] = FONTE_IBGE
                    seguidas = 0
                else:
                    seguidas += 1
                    if seguidas <= 3:
                        log.warning("Sem malha para %s:\n  %s", row["no_pais"], "\n  ".join(tentativas))
                    if seguidas >= MALHA_MAX_FALHAS_SEGUIDAS:
                        log.error("%d falhas seguidas; interrompendo a busca de malhas", seguidas)
                        break
                if i % 25 == 0:
                    log.info("Malhas: %d/%d processados", i, len(faltando))
                time.sleep(MALHA_PAUSA)

    if NE_HABILITADO and any(r["geom"] is None for r in rows):
        n = aplicar_natural_earth(rows, extract_natural_earth(s))
        log.info("Geometrias preenchidas via Natural Earth: %d", n)

    sem = [r["no_pais"] for r in rows if r["geom"] is None]
    log.info("Países com geometria: %d | sem geometria: %d", len(rows) - len(sem), len(sem))
    if sem:
        log.warning("Sem geometria (geom NULL): %d países: %s", len(sem), ", ".join(sorted(sem)))
    if len(sem) == len(rows) and not ALLOW_SEM_GEOM:
        raise RuntimeError("Nenhuma geometria obtida; abortando antes da carga (ALLOW_SEM_GEOM=1 carrega só atributos)")


# --------------------------------------------------------------------------- #
# Load
# --------------------------------------------------------------------------- #
def load(rows: list[dict]) -> None:
    ident = dict(
        schema=sql.Identifier(SCHEMA),
        table=sql.Identifier(TABLE),
        ix_geom=sql.Identifier(f"ix_{TABLE}_geom"),
        ix_iso2=sql.Identifier(f"ux_{TABLE}_iso2"),
    )
    conninfo = psycopg.conninfo.make_conninfo(
        host=os.getenv("POSTGRES_HOST", "postgis-rds-msterritorializacao"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.getenv("POSTGRES_DB", "db_msterritorializacao"),
        connect_timeout=15,
        application_name="etl_pais",
    )
    with psycopg.connect(conninfo) as conn:  # commit no sucesso, rollback em erro
        with conn.cursor() as cur:
            for stmt in DDL:
                cur.execute(sql.SQL(stmt).format(**ident))
            cur.executemany(sql.SQL(UPSERT).format(**ident), rows)
            cur.execute(
                sql.SQL("SELECT count(*), count(geom) FROM {schema}.{table}").format(**ident)
            )
            total, com_geom = cur.fetchone()
    log.info("Carga concluída: %d linhas processadas | tabela: %d linhas, %d com geometria",
             len(rows), total, com_geom)


# --------------------------------------------------------------------------- #
def main() -> int:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    t0 = time.time()
    try:
        s = make_session()
        raw = extract_localidades(s)
        rows, vistos = [], set()
        for r in raw:
            t = transform(r)
            if t["co_m49"] is None or not t["no_pais"]:
                log.warning("Registro ignorado (sem M49/nome): %s", r)
                continue
            if t["co_m49"] in vistos:
                continue
            vistos.add(t["co_m49"])
            rows.append(t)
        if len(rows) < MIN_PAISES:
            raise RuntimeError(f"Apenas {len(rows)} países extraídos (mínimo {MIN_PAISES}); abortando")

        attach_geometries(s, rows, extract_malha_lote(s) if MALHA_LOTE else {})
        load(rows)
    except Exception:
        log.exception("ETL falhou")
        return 1
    log.info("ETL finalizado em %.1fs", time.time() - t0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
