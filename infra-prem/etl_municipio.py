#!/usr/bin/env python3
"""
ETL IBGE -> PostGIS (tabela db_msterritorializacao.tb_municipio)

Hierarquia respeitada:  tb_pais <- tb_estado (co_uf) <- tb_municipio (co_uf)
  -> FK tb_municipio.co_uf -> tb_estado.co_uf
  -> CHECK: os 2 primeiros dígitos do código IBGE do município = co_uf
  -> o ETL exige que os estados já estejam em tb_estado (rode etl_pais.py e etl_estado.py antes).

Extract:
  - API de Localidades v1: /localidades/municipios (microrregião, mesorregião, região imediata/intermediária)
  - API de Malhas v4/v3:   /malhas/estados/{UF}?intrarregiao=municipio (uma chamada por UF) e,
                           se faltar, /malhas/municipios/{codigo} (município a município)
Load:
  - upsert idempotente (ON CONFLICT co_municipio), UF a UF, em uma única transação
  - as geometrias são processadas por UF para limitar o uso de memória
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

import etl_pais as base  # sessão HTTP com retry, helpers de GeoJSON e configuração comum

log = logging.getLogger("etl_municipio")

SCHEMA = base.SCHEMA
TABLE = "tb_municipio"
TABLE_ESTADO = "tb_estado"
MIN_MUNICIPIOS = int(os.getenv("MIN_MUNICIPIOS", "5500"))  # o Brasil tem 5.570 municípios
URL_MUNICIPIOS = f"{base.IBGE_BASE}/v1/localidades/municipios"
FK_ESTADO = "fk_tb_municipio_tb_estado"

DDL = [
    """
    CREATE TABLE IF NOT EXISTS {schema}.{table} (
        co_municipio             integer      PRIMARY KEY,
        no_municipio             text         NOT NULL,
        co_uf                    smallint     NOT NULL,
        co_microrregiao          integer,
        no_microrregiao          text,
        co_mesorregiao           integer,
        no_mesorregiao           text,
        co_regiao_imediata       integer,
        no_regiao_imediata       text,
        co_regiao_intermediaria  integer,
        no_regiao_intermediaria  text,
        geom                     geometry(MultiPolygon, 4326),
        no_fonte_geom            text,
        dt_carga                 timestamptz  NOT NULL DEFAULT now(),
        CONSTRAINT {ck_uf} CHECK (co_municipio / 100000 = co_uf),
        CONSTRAINT {fk_estado} FOREIGN KEY (co_uf)
            REFERENCES {schema}.{tb_estado} (co_uf)
            ON UPDATE CASCADE ON DELETE RESTRICT
    )
    """,
    "CREATE INDEX IF NOT EXISTS {ix_uf} ON {schema}.{table} (co_uf)",
    "CREATE INDEX IF NOT EXISTS {ix_geom} ON {schema}.{table} USING gist (geom)",
]

UPSERT = """
INSERT INTO {schema}.{table} (
    co_municipio, no_municipio, co_uf,
    co_microrregiao, no_microrregiao, co_mesorregiao, no_mesorregiao,
    co_regiao_imediata, no_regiao_imediata, co_regiao_intermediaria, no_regiao_intermediaria,
    geom, no_fonte_geom, dt_carga
) VALUES (
    %(co_municipio)s, %(no_municipio)s, %(co_uf)s,
    %(co_microrregiao)s, %(no_microrregiao)s, %(co_mesorregiao)s, %(no_mesorregiao)s,
    %(co_regiao_imediata)s, %(no_regiao_imediata)s, %(co_regiao_intermediaria)s, %(no_regiao_intermediaria)s,
    ST_Multi(ST_CollectionExtract(
        ST_MakeValid(ST_SetSRID(ST_GeomFromGeoJSON(%(geom)s::text), 4326)), 3)),
    %(no_fonte_geom)s,
    now()
)
ON CONFLICT (co_municipio) DO UPDATE SET
    no_municipio            = EXCLUDED.no_municipio,
    co_uf                   = EXCLUDED.co_uf,
    co_microrregiao         = EXCLUDED.co_microrregiao,
    no_microrregiao         = EXCLUDED.no_microrregiao,
    co_mesorregiao          = EXCLUDED.co_mesorregiao,
    no_mesorregiao          = EXCLUDED.no_mesorregiao,
    co_regiao_imediata      = EXCLUDED.co_regiao_imediata,
    no_regiao_imediata      = EXCLUDED.no_regiao_imediata,
    co_regiao_intermediaria = EXCLUDED.co_regiao_intermediaria,
    no_regiao_intermediaria = EXCLUDED.no_regiao_intermediaria,
    geom                    = COALESCE(EXCLUDED.geom, {schema}.{table}.geom),
    no_fonte_geom           = CASE WHEN EXCLUDED.geom IS NOT NULL THEN EXCLUDED.no_fonte_geom
                                   ELSE {schema}.{table}.no_fonte_geom END,
    dt_carga                = now()
"""


# --------------------------------------------------------------------------- #
# Extract
# --------------------------------------------------------------------------- #
def extract_municipios(s: requests.Session) -> list[dict[str, Any]]:
    log.info("Extraindo municípios: %s", URL_MUNICIPIOS)
    r = s.get(URL_MUNICIPIOS, timeout=(10, 120))
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list):
        raise RuntimeError("Resposta inesperada da API de Localidades (esperava lista)")
    log.info("Localidades: %d municípios", len(data))
    return data


def _params(extra: dict[str, str] | None = None) -> dict[str, str]:
    p = {"formato": base.GEOJSON, "qualidade": base.MALHA_QUALIDADE}
    if extra:
        p.update(extra)
    return p


def _uniao(geoms: list[dict]) -> dict:
    return geoms[0] if len(geoms) == 1 else {"type": "GeometryCollection", "geometries": geoms}


def extract_malha_uf_lote(s: requests.Session, co_uf: int) -> tuple[str | None, dict[int, dict]]:
    """Todos os municípios de uma UF: /malhas/estados/{UF}?intrarregiao=municipio (codarea = código do município)."""
    for versao in ("v4", "v3"):
        r = s.get(f"{base.IBGE_BASE}/{versao}/malhas/estados/{co_uf}",
                  params=_params({"intrarregiao": "municipio"}), timeout=(10, 300))
        if not r.ok:
            log.warning("  UF %s malha em lote %s -> HTTP %s %s", co_uf, versao, r.status_code, base._snippet(r))
            continue
        fc = base._json(r)
        por_mun: dict[int, list[dict]] = {}
        if isinstance(fc, dict):
            for f in fc.get("features", []):
                code = str((f.get("properties") or {}).get("codarea", "")).strip()
                if code.isdigit() and f.get("geometry"):
                    por_mun.setdefault(int(code), []).append(f["geometry"])
        if por_mun:
            return versao, {k: _uniao(v) for k, v in por_mun.items()}
        log.warning("  UF %s malha em lote %s sem features reconhecidas: %s", co_uf, versao, base._snippet(r))
    return None, {}


def extract_malha_municipio(s: requests.Session, co_mun: int) -> tuple[str | None, dict | None]:
    """Fallback município a município: /malhas/municipios/{codigo}."""
    for versao in ("v4", "v3"):
        r = s.get(f"{base.IBGE_BASE}/{versao}/malhas/municipios/{co_mun}", params=_params(), timeout=(10, 120))
        if r.status_code in (400, 404):
            continue
        r.raise_for_status()
        geoms = base._geometrias(base._json(r))
        if geoms:
            return versao, _uniao(geoms)
    return None, None


# --------------------------------------------------------------------------- #
# Transform
# --------------------------------------------------------------------------- #
def _int(v: Any) -> int | None:
    try:
        return int(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def _nome(obj: Any) -> str | None:
    n = obj.get("nome") if isinstance(obj, dict) else None
    return n.strip() if isinstance(n, str) and n.strip() else None


def transform(raw: dict[str, Any]) -> dict[str, Any] | None:
    co = _int(raw.get("id"))
    nome = _nome(raw)
    if co is None or not nome or not (1_000_000 <= co <= 9_999_999):
        return None
    co_uf = co // 100000  # os 2 primeiros dígitos do código IBGE são a UF

    micro = raw.get("microrregiao") or {}          # pode ser nulo em municípios recentes
    meso = micro.get("mesorregiao") or {}
    imed = raw.get("regiao-imediata") or {}
    inter = imed.get("regiao-intermediaria") or {}

    uf_aninhada = _int(((inter.get("UF") or meso.get("UF") or {}).get("id")))
    if uf_aninhada is not None and uf_aninhada != co_uf:
        log.warning("UF inconsistente em %s (%s): código=%s, hierarquia=%s", nome, co, co_uf, uf_aninhada)

    return {
        "co_municipio": co,
        "no_municipio": nome,
        "co_uf": co_uf,
        "co_microrregiao": _int(micro.get("id")),
        "no_microrregiao": _nome(micro),
        "co_mesorregiao": _int(meso.get("id")),
        "no_mesorregiao": _nome(meso),
        "co_regiao_imediata": _int(imed.get("id")),
        "no_regiao_imediata": _nome(imed),
        "co_regiao_intermediaria": _int(inter.get("id")),
        "no_regiao_intermediaria": _nome(inter),
        "geom": None,
        "no_fonte_geom": None,
    }


def obter_geometrias_uf(s: requests.Session, co_uf: int, lista: list[dict]) -> int:
    """Preenche geom/no_fonte_geom dos municípios de uma UF. Retorna quantos ficaram sem geometria."""
    versao, lote = extract_malha_uf_lote(s, co_uf)
    for row in lista:
        g = lote.get(row["co_municipio"])
        if g:
            row["geom"] = json.dumps(g)
            row["no_fonte_geom"] = f"IBGE Malhas {versao} (qualidade={base.MALHA_QUALIDADE}, intrarregiao=municipio)"
    del lote

    faltando = [r for r in lista if r["geom"] is None]
    if faltando:
        log.info("  UF %s: buscando %d município(s) individualmente", co_uf, len(faltando))
        seguidas = 0
        for row in faltando:
            v, g = extract_malha_municipio(s, row["co_municipio"])
            if g:
                row["geom"] = json.dumps(g)
                row["no_fonte_geom"] = f"IBGE Malhas {v} (qualidade={base.MALHA_QUALIDADE})"
                seguidas = 0
            else:
                seguidas += 1
                if seguidas >= 5:
                    log.error("  UF %s: 5 falhas seguidas na malha individual; interrompendo esta UF", co_uf)
                    break
            time.sleep(base.MALHA_PAUSA)
    return sum(1 for r in lista if r["geom"] is None)


# --------------------------------------------------------------------------- #
# Load
# --------------------------------------------------------------------------- #
def _conninfo() -> str:
    return psycopg.conninfo.make_conninfo(
        host=os.getenv("POSTGRES_HOST", "postgis-rds-msterritorializacao"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.getenv("POSTGRES_DB", "db_msterritorializacao"),
        connect_timeout=15,
        application_name="etl_municipio",
    )


def run(s: requests.Session, rows: list[dict]) -> None:
    ident = dict(
        schema=sql.Identifier(SCHEMA),
        table=sql.Identifier(TABLE),
        tb_estado=sql.Identifier(TABLE_ESTADO),
        fk_estado=sql.Identifier(FK_ESTADO),
        ck_uf=sql.Identifier(f"ck_{TABLE}_co_uf"),
        ix_uf=sql.Identifier(f"ix_{TABLE}_co_uf"),
        ix_geom=sql.Identifier(f"ix_{TABLE}_geom"),
    )
    por_uf: dict[int, list[dict]] = {}
    for r in rows:
        por_uf.setdefault(r["co_uf"], []).append(r)

    sem_total = 0
    with psycopg.connect(_conninfo()) as conn:  # commit no sucesso, rollback em erro
        with conn.cursor() as cur:
            # --- pai da hierarquia: tb_estado precisa existir e conter todas as UFs dos municípios
            cur.execute("SELECT to_regclass(%s)", (f'"{SCHEMA}"."{TABLE_ESTADO}"',))
            if cur.fetchone()[0] is None:
                raise RuntimeError(f"{SCHEMA}.{TABLE_ESTADO} não existe; execute etl_pais.py e etl_estado.py antes")
            cur.execute(sql.SQL("SELECT co_uf FROM {schema}.{tb_estado}").format(**ident))
            existentes = {r[0] for r in cur.fetchall()}
            faltam = sorted(set(por_uf) - existentes)
            if faltam:
                raise RuntimeError(f"UFs ausentes em {SCHEMA}.{TABLE_ESTADO}: {faltam}; execute etl_estado.py antes")
            log.info("Estados pai verificados: %d UFs", len(por_uf))

            # --- DDL
            for stmt in DDL:
                cur.execute(sql.SQL(stmt).format(**ident))
            cur.execute("SELECT 1 FROM pg_constraint WHERE conname = %s AND conrelid = to_regclass(%s)",
                        (FK_ESTADO, f'"{SCHEMA}"."{TABLE}"'))
            if cur.fetchone() is None:  # tabela pré-existente sem a FK
                log.info("Criando FK %s", FK_ESTADO)
                cur.execute(sql.SQL(
                    "ALTER TABLE {schema}.{table} ADD CONSTRAINT {fk_estado} FOREIGN KEY (co_uf) "
                    "REFERENCES {schema}.{tb_estado} (co_uf) ON UPDATE CASCADE ON DELETE RESTRICT").format(**ident))

            # --- extração das malhas + carga, UF a UF (memória limitada)
            upsert = sql.SQL(UPSERT).format(**ident)
            for i, (co_uf, lista) in enumerate(sorted(por_uf.items()), 1):
                sem = obter_geometrias_uf(s, co_uf, lista)
                sem_total += sem
                cur.executemany(upsert, lista)
                log.info("UF %s (%d/%d): %d municípios carregados, %d sem geometria",
                         co_uf, i, len(por_uf), len(lista), sem)
                for r in lista:  # libera memória
                    r["geom"] = None
                time.sleep(base.MALHA_PAUSA)

            if sem_total == len(rows) and not base.ALLOW_SEM_GEOM:
                raise RuntimeError("Nenhuma geometria obtida; carga revertida (ALLOW_SEM_GEOM=1 carrega só atributos)")

            cur.execute(sql.SQL("SELECT count(*), count(geom) FROM {schema}.{table}").format(**ident))
            total, com_geom = cur.fetchone()
    log.info("Carga concluída: %d linhas processadas | tabela: %d linhas, %d com geometria | sem geometria nesta carga: %d",
             len(rows), total, com_geom, sem_total)


# --------------------------------------------------------------------------- #
def main() -> int:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    t0 = time.time()
    try:
        s = base.make_session()
        rows, vistos = [], set()
        for raw in extract_municipios(s):
            t = transform(raw)
            if t is None:
                log.warning("Registro ignorado (dados incompletos): %s", raw)
                continue
            if t["co_municipio"] in vistos:
                continue
            vistos.add(t["co_municipio"])
            rows.append(t)
        if len(rows) < MIN_MUNICIPIOS:
            raise RuntimeError(f"Apenas {len(rows)} municípios extraídos (mínimo {MIN_MUNICIPIOS}); abortando")
        run(s, rows)
    except Exception:
        log.exception("ETL falhou")
        return 1
    log.info("ETL finalizado em %.1fs", time.time() - t0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
