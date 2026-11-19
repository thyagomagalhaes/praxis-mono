#!/usr/bin/env python3
"""
ETL IBGE -> PostGIS (tabela db_msterritorializacao.tb_bairro)

ATENÇÃO À FONTE: o IBGE NÃO publica bairros nas APIs de Localidades nem de Malhas.
Os bairros existem como arquivo geoespacial (Censo 2022 - Arquivo geoespacial de Bairros).
Este ETL baixa o Shapefile oficial (BR_bairros_CD2022.zip) e o carrega no banco.

Hierarquia respeitada:  tb_pais <- tb_estado <- tb_municipio <- tb_bairro
  -> FK tb_bairro.co_municipio -> tb_municipio.co_municipio
  -> CHECK: os 7 primeiros dígitos do geocódigo do bairro (10 dígitos) = co_municipio
  -> o ETL exige que tb_municipio já esteja carregada (rode pais -> estado -> municipio antes).

Observações:
  - Só existem bairros nos municípios que têm bairros instituídos em lei (cerca de 17,5 mil no país).
  - A leitura é em duas passagens e a carga em lotes, para caber no limite de memória do container.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import tempfile
import time
import zipfile
from collections import Counter
from contextlib import contextmanager
from typing import Any, Callable, Iterator

import psycopg
import requests
import shapefile  # pyshp
from psycopg import sql

import etl_pais as base  # configuração e sessão HTTP comuns

log = logging.getLogger("etl_bairro")

SCHEMA = base.SCHEMA
TABLE = "tb_bairro"
TABLE_MUNICIPIO = "tb_municipio"
FK_MUNICIPIO = "fk_tb_bairro_tb_municipio"

BAIRROS_URL = os.getenv(
    "BAIRROS_URL",
    "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/"
    "malha_com_atributos/bairros/shp/BR/BR_bairros_CD2022.zip",
)
BAIRROS_ARQUIVO = os.getenv("BAIRROS_ARQUIVO")              # zip local (tem prioridade sobre a URL)
BAIRROS_ORFAOS = os.getenv("BAIRROS_ORFAOS", "abortar")     # abortar | ignorar (bairro cujo município não está em tb_municipio)
MIN_BAIRROS = int(os.getenv("MIN_BAIRROS", "15000"))        # o Censo 2022 tem ~17,5 mil bairros
LOTE = int(os.getenv("BAIRROS_LOTE", "500"))
FONTE = "IBGE Censo 2022 - Arquivo geoespacial de Bairros (BR_bairros_CD2022)"

DDL = [
    """
    CREATE TABLE IF NOT EXISTS {schema}.{table} (
        co_bairro               bigint        PRIMARY KEY,
        no_bairro               text          NOT NULL,
        co_municipio            integer       NOT NULL,
        co_distrito             bigint,
        no_distrito             text,
        co_subdistrito          bigint,
        no_subdistrito          text,
        co_concentracao_urbana  text,
        no_concentracao_urbana  text,
        nu_area_km2             numeric(14,4),
        geom                    geometry(MultiPolygon, 4326),
        no_fonte_geom           text,
        dt_carga                timestamptz   NOT NULL DEFAULT now(),
        CONSTRAINT {ck_mun} CHECK (co_bairro / 1000 = co_municipio),
        CONSTRAINT {fk_mun} FOREIGN KEY (co_municipio)
            REFERENCES {schema}.{tb_municipio} (co_municipio)
            ON UPDATE CASCADE ON DELETE RESTRICT
    )
    """,
    "CREATE INDEX IF NOT EXISTS {ix_mun} ON {schema}.{table} (co_municipio)",
    "CREATE INDEX IF NOT EXISTS {ix_geom} ON {schema}.{table} USING gist (geom)",
]

UPSERT = """
INSERT INTO {schema}.{table} (
    co_bairro, no_bairro, co_municipio, co_distrito, no_distrito, co_subdistrito, no_subdistrito,
    co_concentracao_urbana, no_concentracao_urbana, nu_area_km2, geom, no_fonte_geom, dt_carga
) VALUES (
    %(co_bairro)s, %(no_bairro)s, %(co_municipio)s, %(co_distrito)s, %(no_distrito)s,
    %(co_subdistrito)s, %(no_subdistrito)s, %(co_concentracao_urbana)s, %(no_concentracao_urbana)s,
    %(nu_area_km2)s,
    ST_Multi(ST_CollectionExtract(
        ST_MakeValid(ST_SetSRID(ST_GeomFromGeoJSON(%(geom)s::text), 4326)), 3)),
    %(no_fonte_geom)s,
    now()
)
ON CONFLICT (co_bairro) DO UPDATE SET
    no_bairro              = EXCLUDED.no_bairro,
    co_municipio           = EXCLUDED.co_municipio,
    co_distrito            = EXCLUDED.co_distrito,
    no_distrito            = EXCLUDED.no_distrito,
    co_subdistrito         = EXCLUDED.co_subdistrito,
    no_subdistrito         = EXCLUDED.no_subdistrito,
    co_concentracao_urbana = EXCLUDED.co_concentracao_urbana,
    no_concentracao_urbana = EXCLUDED.no_concentracao_urbana,
    nu_area_km2            = EXCLUDED.nu_area_km2,
    geom                   = COALESCE(EXCLUDED.geom, {schema}.{table}.geom),
    no_fonte_geom          = CASE WHEN EXCLUDED.geom IS NOT NULL THEN EXCLUDED.no_fonte_geom
                                  ELSE {schema}.{table}.no_fonte_geom END,
    dt_carga               = now()
"""


# --------------------------------------------------------------------------- #
# Extract: download + leitura do Shapefile
# --------------------------------------------------------------------------- #
@contextmanager
def obter_shapefile(s: requests.Session) -> Iterator[str]:
    """Baixa (ou abre) o zip, extrai shp/shx/dbf/prj/cpg para um diretório temporário e devolve o caminho sem extensão."""
    with tempfile.TemporaryDirectory(prefix="bairros_") as tmp:
        if BAIRROS_ARQUIVO:
            zip_path = BAIRROS_ARQUIVO
            log.info("Usando arquivo local: %s", zip_path)
        else:
            zip_path = os.path.join(tmp, "bairros.zip")
            log.info("Baixando bairros: %s", BAIRROS_URL)
            with s.get(BAIRROS_URL, stream=True, timeout=(10, 600), headers={"Accept": "*/*"}) as r:
                r.raise_for_status()
                total = 0
                with open(zip_path, "wb") as fh:
                    for chunk in r.iter_content(chunk_size=1 << 20):
                        fh.write(chunk)
                        total += len(chunk)
            log.info("Download concluído: %.1f MB", total / 1e6)

        destino = os.path.join(tmp, "bairros")
        achou_shp = False
        with zipfile.ZipFile(zip_path) as zf:
            for info in zf.infolist():
                ext = os.path.splitext(info.filename)[1].lower()
                if ext in (".shp", ".shx", ".dbf", ".prj", ".cpg"):
                    with zf.open(info) as src, open(destino + ext, "wb") as dst:  # nome fixo: sem path traversal
                        while chunk := src.read(1 << 20):
                            dst.write(chunk)
                    achou_shp = achou_shp or ext == ".shp"
        if not achou_shp:
            raise RuntimeError("O zip não contém um .shp")
        yield destino


def checar_crs(prefixo: str) -> None:
    """O ETL não reprojeta: exige coordenadas geográficas (graus). SIRGAS 2000 é gravado como SRID 4326."""
    prj = prefixo + ".prj"
    if not os.path.exists(prj):
        log.warning("Arquivo .prj ausente; assumindo coordenadas geográficas SIRGAS 2000")
        return
    wkt = open(prj, encoding="utf-8", errors="replace").read()
    if "PROJCS" in wkt.upper():
        raise RuntimeError("Shapefile em sistema projetado; este ETL espera coordenadas geográficas (graus)")
    log.info("CRS do arquivo: %s", wkt[:80].replace("\n", " "))


def abrir_reader(prefixo: str) -> "shapefile.Reader":
    enc = "utf-8"
    cpg = prefixo + ".cpg"
    if os.path.exists(cpg):
        txt = open(cpg, encoding="ascii", errors="ignore").read().strip()
        if txt:
            enc = f"cp{txt}" if txt.isdigit() else txt
    log.info("Encoding do DBF: %s", enc)
    return shapefile.Reader(prefixo, encoding=enc, encodingErrors="replace")


# --------------------------------------------------------------------------- #
# Transform
# --------------------------------------------------------------------------- #
def _int(v: Any) -> int | None:
    try:
        return int(float(str(v).strip())) if v is not None and str(v).strip() != "" else None
    except (TypeError, ValueError):
        return None


def _txt(v: Any) -> str | None:
    t = str(v).strip() if v is not None else ""
    return t or None


def _num(v: Any) -> float | None:
    try:
        return float(v) if v is not None and str(v).strip() != "" else None
    except (TypeError, ValueError):
        return None


def parse_registro(d: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    """Converte um registro do DBF. Retorna (linha, None) ou (None, motivo_da_rejeição)."""
    cb = _int(d.get("CD_BAIRRO"))
    cm = _int(d.get("CD_MUN"))
    nome = _txt(d.get("NM_BAIRRO"))
    if cb is None or not nome:
        return None, "sem_codigo_ou_nome"

    if cb >= 1_000_000_000:               # geocódigo completo de 10 dígitos (7 do município + 3 do bairro)
        co_bairro, co_mun = cb, cb // 1000
        if cm is not None and cm != co_mun:
            return None, "municipio_inconsistente"
    elif cm is not None and cb < 1000:    # arquivo traz só o sufixo do bairro
        co_bairro, co_mun = cm * 1000 + cb, cm
    else:
        return None, "codigo_invalido"

    return {
        "co_bairro": co_bairro,
        "no_bairro": nome,
        "co_municipio": co_mun,
        "co_distrito": _int(d.get("CD_DIST")),
        "no_distrito": _txt(d.get("NM_DIST")),
        "co_subdistrito": _int(d.get("CD_SUBDIST")),
        "no_subdistrito": _txt(d.get("NM_SUBDIST")),
        "co_concentracao_urbana": _txt(d.get("CD_CONCURB")),
        "no_concentracao_urbana": _txt(d.get("NM_CONCURB")),
        "nu_area_km2": _num(d.get("AREA_KM2")),
        "geom": None,
        "no_fonte_geom": FONTE,
    }, None


def ler_atributos(rd: Any) -> tuple[list[dict | None], Counter]:
    """1ª passagem (só DBF, sem geometrias). A lista fica alinhada com as feições do .shp."""
    campos = [str(f[0]).upper() for f in rd.fields if f[0] != "DeletionFlag"]
    log.info("Campos do arquivo: %s", ", ".join(campos))
    if "CD_BAIRRO" not in campos or "NM_BAIRRO" not in campos:
        raise RuntimeError(f"Campos CD_BAIRRO/NM_BAIRRO ausentes; campos disponíveis: {campos}")
    attrs: list[dict | None] = []
    motivos: Counter = Counter()
    for rec in rd.iterRecords():
        d = {str(k).upper(): v for k, v in rec.as_dict().items()}
        row, motivo = parse_registro(d)
        attrs.append(row)
        if motivo:
            motivos[motivo] += 1
    return attrs, motivos


def transmitir(rd: Any, attrs: list[dict | None], gravar: Callable[[list[dict]], None]) -> dict[str, int]:
    """2ª passagem: lê as geometrias em streaming e entrega lotes prontos para gravar.
    Geocódigos repetidos no arquivo (feições multiparte) têm as geometrias reunidas."""
    cont = Counter(r["co_bairro"] for r in attrs if r)
    repetidos = {c for c, n in cont.items() if n > 1}
    if repetidos:
        log.info("%d geocódigos aparecem em mais de uma feição; geometrias serão reunidas", len(repetidos))

    lote: list[dict] = []
    reunir: dict[int, tuple[dict, list[dict]]] = {}
    stats = {"gravados": 0, "sem_geometria": 0}

    def _emitir(row: dict) -> None:
        lote.append(row)
        if len(lote) >= LOTE:
            gravar(lote[:])
            stats["gravados"] += len(lote)
            lote.clear()

    for i, shp in enumerate(rd.iterShapes()):
        row = attrs[i] if i < len(attrs) else None
        if row is None:
            continue
        geom = None if shp.shapeType == 0 else shp.__geo_interface__
        if row["co_bairro"] in repetidos:
            item = reunir.setdefault(row["co_bairro"], (row, []))
            if geom:
                item[1].append(geom)
            continue
        if geom is None:
            stats["sem_geometria"] += 1
        row["geom"] = json.dumps(geom, separators=(",", ":")) if geom else None
        _emitir(row)

    for row, geoms in reunir.values():
        g = None if not geoms else (geoms[0] if len(geoms) == 1 else {"type": "GeometryCollection", "geometries": geoms})
        if g is None:
            stats["sem_geometria"] += 1
        row["geom"] = json.dumps(g, separators=(",", ":")) if g else None
        _emitir(row)

    if lote:
        gravar(lote[:])
        stats["gravados"] += len(lote)
    return stats


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
        application_name="etl_bairro",
    )


def run(rd: Any, attrs: list[dict | None]) -> None:
    ident = dict(
        schema=sql.Identifier(SCHEMA),
        table=sql.Identifier(TABLE),
        tb_municipio=sql.Identifier(TABLE_MUNICIPIO),
        fk_mun=sql.Identifier(FK_MUNICIPIO),
        ck_mun=sql.Identifier(f"ck_{TABLE}_co_municipio"),
        ix_mun=sql.Identifier(f"ix_{TABLE}_co_municipio"),
        ix_geom=sql.Identifier(f"ix_{TABLE}_geom"),
    )
    with psycopg.connect(_conninfo()) as conn:  # commit no sucesso, rollback em erro
        with conn.cursor() as cur:
            # --- pai da hierarquia: tb_municipio precisa existir e conter os municípios dos bairros
            cur.execute("SELECT to_regclass(%s)", (f'"{SCHEMA}"."{TABLE_MUNICIPIO}"',))
            if cur.fetchone()[0] is None:
                raise RuntimeError(f"{SCHEMA}.{TABLE_MUNICIPIO} não existe; execute etl_pais, etl_estado e etl_municipio antes")
            cur.execute(sql.SQL("SELECT co_municipio FROM {schema}.{tb_municipio}").format(**ident))
            existentes = {r[0] for r in cur.fetchall()}
            orfaos = sorted({r["co_municipio"] for r in attrs if r and r["co_municipio"] not in existentes})
            if orfaos:
                if BAIRROS_ORFAOS != "ignorar":
                    raise RuntimeError(
                        f"{len(orfaos)} município(s) dos bairros ausentes em {SCHEMA}.{TABLE_MUNICIPIO}: {orfaos[:10]}... "
                        "(BAIRROS_ORFAOS=ignorar descarta esses bairros)")
                n = 0
                for i, r in enumerate(attrs):
                    if r and r["co_municipio"] not in existentes:
                        attrs[i] = None
                        n += 1
                log.warning("%d bairros ignorados por município inexistente em tb_municipio: %s", n, orfaos[:10])

            # --- DDL
            for stmt in DDL:
                cur.execute(sql.SQL(stmt).format(**ident))
            cur.execute("SELECT 1 FROM pg_constraint WHERE conname = %s AND conrelid = to_regclass(%s)",
                        (FK_MUNICIPIO, f'"{SCHEMA}"."{TABLE}"'))
            if cur.fetchone() is None:  # tabela pré-existente sem a FK
                log.info("Criando FK %s", FK_MUNICIPIO)
                cur.execute(sql.SQL(
                    "ALTER TABLE {schema}.{table} ADD CONSTRAINT {fk_mun} FOREIGN KEY (co_municipio) "
                    "REFERENCES {schema}.{tb_municipio} (co_municipio) ON UPDATE CASCADE ON DELETE RESTRICT").format(**ident))

            # --- carga em lotes (geometrias lidas em streaming)
            upsert = sql.SQL(UPSERT).format(**ident)
            progresso = {"n": 0}

            def gravar(lote: list[dict]) -> None:
                cur.executemany(upsert, lote)
                progresso["n"] += len(lote)
                if progresso["n"] % (LOTE * 10) < LOTE:
                    log.info("  %d bairros gravados...", progresso["n"])

            stats = transmitir(rd, attrs, gravar)
            if stats["gravados"] > 0 and stats["sem_geometria"] == stats["gravados"] and not base.ALLOW_SEM_GEOM:
                raise RuntimeError("Nenhuma geometria lida; carga revertida (ALLOW_SEM_GEOM=1 carrega só atributos)")

            cur.execute(sql.SQL(
                "SELECT count(*), count(geom), count(DISTINCT co_municipio) FROM {schema}.{table}").format(**ident))
            total, com_geom, n_mun = cur.fetchone()
    log.info("Carga concluída: %d bairros gravados (%d sem geometria) | tabela: %d linhas, %d com geometria, %d municípios",
             stats["gravados"], stats["sem_geometria"], total, com_geom, n_mun)


# --------------------------------------------------------------------------- #
def main() -> int:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    t0 = time.time()
    try:
        s = base.make_session()
        with obter_shapefile(s) as prefixo:
            checar_crs(prefixo)
            rd = abrir_reader(prefixo)
            attrs, motivos = ler_atributos(rd)
            validos = sum(1 for r in attrs if r)
            log.info("Feições: %d | válidas: %d | rejeitadas: %s", len(attrs), validos, dict(motivos) or "0")
            if validos < MIN_BAIRROS:
                raise RuntimeError(f"Apenas {validos} bairros válidos (mínimo {MIN_BAIRROS}); abortando")
            run(rd, attrs)
            rd.close()
    except Exception:
        log.exception("ETL falhou")
        return 1
    log.info("ETL finalizado em %.1fs", time.time() - t0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
