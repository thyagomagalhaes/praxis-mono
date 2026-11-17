#!/usr/bin/env python3
"""
ETL IBGE -> PostGIS (tabela db_msterritorializacao.tb_estado)

Hierarquia respeitada:  tb_pais (co_m49)  <-- FK --  tb_estado (co_pais_m49)
  -> o ETL exige que o país pai (Brasil, M49=76) já exista em tb_pais (rode etl_pais.py antes).

Extract:
  - API de Localidades v1: /localidades/estados (id, sigla, nome, região)
  - API de Malhas v4/v3:   /malhas/paises/BR?intrarregiao=UF (lote) e, se faltar,
                           /malhas/estados/{codigo} (UF a UF)
Load:
  - upsert idempotente (ON CONFLICT co_uf) em uma única transação
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

import etl_pais as base  # reaproveita sessão HTTP com retry, helpers de GeoJSON e configuração comum

log = logging.getLogger("etl_estado")

SCHEMA = base.SCHEMA
TABLE = "tb_estado"
TABLE_PAIS = "tb_pais"
PAIS_M49 = int(os.getenv("PAIS_M49", "76"))          # 76 = Brasil (código M49 / ISO numérico)
MIN_ESTADOS = int(os.getenv("MIN_ESTADOS", "27"))    # 26 estados + DF
URL_ESTADOS = f"{base.IBGE_BASE}/v1/localidades/estados"
FK_PAIS = "fk_tb_estado_tb_pais"

DDL = [
    """
    CREATE TABLE IF NOT EXISTS {schema}.{table} (
        co_uf          smallint     PRIMARY KEY,
        sg_uf          char(2)      NOT NULL,
        no_estado      text         NOT NULL,
        co_pais_m49    smallint     NOT NULL DEFAULT {pais},
        co_regiao      smallint     NOT NULL,
        sg_regiao      varchar(2),
        no_regiao      text         NOT NULL,
        geom           geometry(MultiPolygon, 4326),
        no_fonte_geom  text,
        dt_carga       timestamptz  NOT NULL DEFAULT now(),
        CONSTRAINT {uq_sg} UNIQUE (sg_uf),
        CONSTRAINT {fk_pais} FOREIGN KEY (co_pais_m49)
            REFERENCES {schema}.{tb_pais} (co_m49)
            ON UPDATE CASCADE ON DELETE RESTRICT
    )
    """,
    "CREATE INDEX IF NOT EXISTS {ix_pais} ON {schema}.{table} (co_pais_m49)",
    "CREATE INDEX IF NOT EXISTS {ix_regiao} ON {schema}.{table} (co_regiao)",
    "CREATE INDEX IF NOT EXISTS {ix_geom} ON {schema}.{table} USING gist (geom)",
]

UPSERT = """
INSERT INTO {schema}.{table} (
    co_uf, sg_uf, no_estado, co_pais_m49, co_regiao, sg_regiao, no_regiao,
    geom, no_fonte_geom, dt_carga
) VALUES (
    %(co_uf)s, %(sg_uf)s, %(no_estado)s, %(co_pais_m49)s, %(co_regiao)s, %(sg_regiao)s, %(no_regiao)s,
    ST_Multi(ST_CollectionExtract(
        ST_MakeValid(ST_SetSRID(ST_GeomFromGeoJSON(%(geom)s::text), 4326)), 3)),
    %(no_fonte_geom)s,
    now()
)
ON CONFLICT (co_uf) DO UPDATE SET
    sg_uf         = EXCLUDED.sg_uf,
    no_estado     = EXCLUDED.no_estado,
    co_pais_m49   = EXCLUDED.co_pais_m49,
    co_regiao     = EXCLUDED.co_regiao,
    sg_regiao     = EXCLUDED.sg_regiao,
    no_regiao     = EXCLUDED.no_regiao,
    geom          = COALESCE(EXCLUDED.geom, {schema}.{table}.geom),
    no_fonte_geom = CASE WHEN EXCLUDED.geom IS NOT NULL THEN EXCLUDED.no_fonte_geom
                         ELSE {schema}.{table}.no_fonte_geom END,
    dt_carga      = now()
"""


# --------------------------------------------------------------------------- #
# Extract
# --------------------------------------------------------------------------- #
def extract_estados(s: requests.Session) -> list[dict[str, Any]]:
    log.info("Extraindo estados: %s", URL_ESTADOS)
    r = s.get(URL_ESTADOS, timeout=(10, 60))
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list):
        raise RuntimeError("Resposta inesperada da API de Localidades (esperava lista)")
    log.info("Localidades: %d estados", len(data))
    return data


def _params(extra: dict[str, str] | None = None) -> dict[str, str]:
    p = {"formato": base.GEOJSON, "qualidade": base.MALHA_QUALIDADE}
    if extra:
        p.update(extra)
    return p


def _uniao(geoms: list[dict]) -> dict:
    return geoms[0] if len(geoms) == 1 else {"type": "GeometryCollection", "geometries": geoms}


def extract_malha_lote(s: requests.Session) -> tuple[str | None, dict[int, dict]]:
    """Todas as UFs em uma chamada: /malhas/paises/BR?intrarregiao=UF (properties.codarea = código da UF)."""
    for versao in ("v4", "v3"):
        url = f"{base.IBGE_BASE}/{versao}/malhas/paises/BR"
        r = s.get(url, params=_params({"intrarregiao": "UF"}), timeout=(10, 300))
        log.info("Malha em lote %s -> HTTP %s", r.url, r.status_code)
        if not r.ok:
            log.warning("  resposta: %s", base._snippet(r))
            continue
        fc = base._json(r)
        por_uf: dict[int, list[dict]] = {}
        if isinstance(fc, dict):
            for f in fc.get("features", []):
                code = str((f.get("properties") or {}).get("codarea", "")).strip()
                if code.isdigit() and f.get("geometry"):
                    por_uf.setdefault(int(code), []).append(f["geometry"])
        if por_uf:
            log.info("Malha em lote (%s): %d UFs", versao, len(por_uf))
            return versao, {k: _uniao(v) for k, v in por_uf.items()}
        log.warning("  resposta sem features reconhecidas (%s)", base._snippet(r))
    return None, {}


def extract_malha_uf(s: requests.Session, co_uf: int) -> tuple[str | None, dict | None]:
    """Fallback UF a UF: /malhas/estados/{codigo}."""
    for versao in ("v4", "v3"):
        r = s.get(f"{base.IBGE_BASE}/{versao}/malhas/estados/{co_uf}", params=_params(), timeout=(10, 120))
        if r.status_code in (400, 404):
            log.warning("  UF %s %s -> HTTP %s %s", co_uf, versao, r.status_code, base._snippet(r))
            continue
        r.raise_for_status()
        geoms = base._geometrias(base._json(r))
        if geoms:
            return versao, _uniao(geoms)
    return None, None


# --------------------------------------------------------------------------- #
# Transform
# --------------------------------------------------------------------------- #
def transform(raw: dict[str, Any]) -> dict[str, Any] | None:
    reg = raw.get("regiao") or {}
    try:
        co_uf = int(raw["id"])
        co_regiao = int(reg["id"])
    except (KeyError, TypeError, ValueError):
        return None
    sg = (raw.get("sigla") or "").strip().upper()
    nome = (raw.get("nome") or "").strip()
    if len(sg) != 2 or not nome or not (reg.get("nome") or "").strip():
        return None
    return {
        "co_uf": co_uf,
        "sg_uf": sg,
        "no_estado": nome,
        "co_pais_m49": PAIS_M49,
        "co_regiao": co_regiao,
        "sg_regiao": (reg.get("sigla") or None),
        "no_regiao": reg["nome"].strip(),
        "geom": None,
        "no_fonte_geom": None,
    }


def attach_geometries(s: requests.Session, rows: list[dict]) -> None:
    fonte = lambda v: f"IBGE Malhas {v} (qualidade={base.MALHA_QUALIDADE}, intrarregiao=UF)"
    versao, lote = extract_malha_lote(s)
    for row in rows:
        if row["co_uf"] in lote:
            row["geom"] = json.dumps(lote[row["co_uf"]])
            row["no_fonte_geom"] = fonte(versao)

    faltando = [r for r in rows if r["geom"] is None]
    if faltando:
        log.info("Buscando malha UF a UF para %d estados", len(faltando))
        seguidas = 0
        for row in faltando:
            v, geom = extract_malha_uf(s, row["co_uf"])
            if geom:
                row["geom"] = json.dumps(geom)
                row["no_fonte_geom"] = f"IBGE Malhas {v} (qualidade={base.MALHA_QUALIDADE})"
                seguidas = 0
            else:
                seguidas += 1
                if seguidas >= 5:
                    log.error("5 falhas seguidas na malha UF a UF; interrompendo")
                    break
            time.sleep(base.MALHA_PAUSA)

    sem = [r["sg_uf"] for r in rows if r["geom"] is None]
    log.info("Estados com geometria: %d | sem geometria: %d", len(rows) - len(sem), len(sem))
    if sem:
        log.warning("Sem geometria (geom NULL): %s", ", ".join(sorted(sem)))
    if len(sem) == len(rows) and not base.ALLOW_SEM_GEOM:
        raise RuntimeError("Nenhuma geometria obtida; abortando antes da carga (ALLOW_SEM_GEOM=1 carrega só atributos)")


# --------------------------------------------------------------------------- #
# Load
# --------------------------------------------------------------------------- #
def load(rows: list[dict]) -> None:
    ident = dict(
        schema=sql.Identifier(SCHEMA),
        table=sql.Identifier(TABLE),
        tb_pais=sql.Identifier(TABLE_PAIS),
        pais=sql.Literal(PAIS_M49),
        fk_pais=sql.Identifier(FK_PAIS),
        uq_sg=sql.Identifier(f"uq_{TABLE}_sg_uf"),
        ix_pais=sql.Identifier(f"ix_{TABLE}_co_pais_m49"),
        ix_regiao=sql.Identifier(f"ix_{TABLE}_co_regiao"),
        ix_geom=sql.Identifier(f"ix_{TABLE}_geom"),
    )
    conninfo = psycopg.conninfo.make_conninfo(
        host=os.getenv("POSTGRES_HOST", "postgis-rds-msterritorializacao"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.getenv("POSTGRES_DB", "db_msterritorializacao"),
        connect_timeout=15,
        application_name="etl_estado",
    )
    with psycopg.connect(conninfo) as conn:  # commit no sucesso, rollback em erro
        with conn.cursor() as cur:
            # --- pai da hierarquia: tb_pais precisa existir e conter o Brasil
            cur.execute("SELECT to_regclass(%s)", (f'"{SCHEMA}"."{TABLE_PAIS}"',))
            if cur.fetchone()[0] is None:
                raise RuntimeError(f"{SCHEMA}.{TABLE_PAIS} não existe; execute etl_pais.py antes")
            cur.execute(sql.SQL("SELECT no_pais FROM {schema}.{tb_pais} WHERE co_m49 = %s").format(**ident), (PAIS_M49,))
            pai = cur.fetchone()
            if not pai:
                raise RuntimeError(f"País M49={PAIS_M49} não encontrado em {SCHEMA}.{TABLE_PAIS}; execute etl_pais.py antes")
            log.info("País pai: %s (M49=%s)", pai[0], PAIS_M49)

            # --- DDL
            for stmt in DDL:
                cur.execute(sql.SQL(stmt).format(**ident))
            # tabela pré-existente sem a FK: adiciona
            cur.execute("SELECT 1 FROM pg_constraint WHERE conname = %s AND conrelid = to_regclass(%s)",
                        (FK_PAIS, f'"{SCHEMA}"."{TABLE}"'))
            if cur.fetchone() is None:
                log.info("Criando FK %s", FK_PAIS)
                cur.execute(sql.SQL(
                    "ALTER TABLE {schema}.{table} ADD CONSTRAINT {fk_pais} FOREIGN KEY (co_pais_m49) "
                    "REFERENCES {schema}.{tb_pais} (co_m49) ON UPDATE CASCADE ON DELETE RESTRICT").format(**ident))

            # --- carga
            cur.executemany(sql.SQL(UPSERT).format(**ident), rows)
            cur.execute(sql.SQL("SELECT count(*), count(geom) FROM {schema}.{table}").format(**ident))
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
        s = base.make_session()
        rows, vistos = [], set()
        for raw in extract_estados(s):
            t = transform(raw)
            if t is None:
                log.warning("Registro ignorado (dados incompletos): %s", raw)
                continue
            if t["co_uf"] in vistos:
                continue
            vistos.add(t["co_uf"])
            rows.append(t)
        if len(rows) < MIN_ESTADOS:
            raise RuntimeError(f"Apenas {len(rows)} estados extraídos (mínimo {MIN_ESTADOS}); abortando")
        attach_geometries(s, rows)
        load(rows)
    except Exception:
        log.exception("ETL falhou")
        return 1
    log.info("ETL finalizado em %.1fs", time.time() - t0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
