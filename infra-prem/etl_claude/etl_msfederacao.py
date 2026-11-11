#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
 ETL GEOGRÁFICO MUNDIAL  ->  PostGIS  (db_msfederacao)
 Fontes : REST Countries v3.1 | CountryStateCity (CSC) | Overpass (OSM)
 Apoio  : QGIS (PyQGIS) para validação geométrica e projeto de QA visual
 Tabelas: tb_pais -> tb_estado -> tb_cidade   (PK/FK em UUIDv7)
===============================================================================
 ESTE ARQUIVO CONTÉM, EM UM SÓ LUGAR:
   1. Dependências Python ........ REQUIREMENTS_TXT
   2. Variáveis de ambiente ....... ENV_TEMPLATE  (+ classe Cfg)
   3. DDL das tabelas/relações .... SQL_DDL
   4. Índices GiST e B-Tree ....... SQL_INDICES
   5. Código do ETL e etapa QGIS

 USO RÁPIDO
   python etl_msfederacao.py init-files      # gera requirements.txt, .env.example, schema.sql
   pip install -r requirements.txt
   cp .env.example .env   (edite DB_*, CSC_API_KEY ...)
   python etl_msfederacao.py run             # schema -> países -> estados -> cidades -> índices -> QGIS

 COMANDOS
   print-sql | print-requirements | print-env | init-files
   schema | paises | estados | cidades | indices | qgis | run
   Opção: --paises BR,PT,US   (limita a execução; útil para testes)

 OBSERVAÇÕES IMPORTANTES
   * REST Countries fornece gentílicos apenas em inglês (eng) e francês (fra).
   * CSC e Overpass NÃO fornecem gentílicos/naturalidades de estados e cidades
     em português. Use o CSV opcional GENTILICOS_CSV (colunas:
     nivel[pais|estado|cidade], iso2, cod_estado, nome, gentilico_masc,
     gentilico_fem). Tags OSM "demonym:pt"/"demonym" são aproveitadas se existirem.
   * Todas as respostas HTTP são cacheadas em CACHE_DIR: o pipeline é retomável.
   * Cargas são idempotentes (UPSERT por chave natural; o UUIDv7 original é mantido).
===============================================================================
"""

# =============================================================================
# 1. DEPENDÊNCIAS PYTHON  (Python >= 3.10)
#    QGIS/PyQGIS NÃO vem do pip: instale o QGIS e rode a etapa "qgis" com o
#    Python que o acompanha (ver QGIS_PREFIX_PATH).
# =============================================================================
REQUIREMENTS_TXT = """\
requests>=2.31
psycopg2-binary>=2.9
shapely>=2.0
python-dotenv>=1.0
tqdm>=4.66
"""

# =============================================================================
# 2. VARIÁVEIS DE AMBIENTE  (copie para .env)
# =============================================================================
ENV_TEMPLATE = """\
# --- Banco (container PostGIS do docker compose; porta publicada no host) ---
DB_HOST=localhost
DB_PORT=5432
DB_NAME=db_msfederacao
DB_USER=postgres
DB_PASSWORD=troque_esta_senha

# --- CountryStateCity ---
CSC_API_KEY=coloque_sua_chave_aqui
CSC_BASE_URL=https://api.countrystatecity.in/v1
CSC_SLEEP=0.2
CSC_STATE_DETAILS=true

# --- REST Countries ---
REST_COUNTRIES_URL=https://restcountries.com/v3.1

# --- Overpass (OSM). Para carga mundial prefira uma instância própria ---
USE_OVERPASS=true
OVERPASS_URL=https://overpass-api.de/api/interpreter
OVERPASS_TIMEOUT=300
OVERPASS_SLEEP=2
OVERPASS_PLACE_TYPES=city,town,village,municipality
SIMPLIFY_TOLERANCE=0.001

# --- HTTP / cache ---
HTTP_RETRIES=5
HTTP_TIMEOUT=360
CACHE_DIR=./.cache_etl

# --- Gentílicos pt-BR (opcional) ---
GENTILICOS_CSV=./gentilicos_pt.csv

# --- Filtro de países (ISO2 separados por vírgula; vazio = mundo todo) ---
COUNTRIES=

# --- QGIS (etapa de validação/QA) ---
QGIS_ENABLED=false
QGIS_PREFIX_PATH=/usr
QGIS_PROJECT_PATH=./msfederacao.qgz

LOG_LEVEL=INFO
"""

# =============================================================================
# 3. DDL  (UUIDv7 + tabelas + relações hierárquicas)
# =============================================================================
SQL_DDL = r"""
CREATE EXTENSION IF NOT EXISTS postgis;

-- UUIDv7 (RFC 9562): 48 bits de timestamp em ms + aleatório. Ordenável no tempo,
-- o que reduz fragmentação em B-Tree. (No PostgreSQL 18+ existe uuidv7() nativo.)
CREATE OR REPLACE FUNCTION fn_uuid_v7() RETURNS uuid
LANGUAGE sql VOLATILE PARALLEL SAFE AS $$
  SELECT encode(
    set_bit(
      set_bit(
        overlay(uuid_send(gen_random_uuid())
                PLACING substring(int8send(floor(extract(epoch FROM clock_timestamp()) * 1000)::bigint) FROM 3)
                FROM 1 FOR 6),
        52, 1),
      53, 1),
    'hex')::uuid;
$$;

-- ---------------------------------------------------------------------------
-- 1) tb_pais
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tb_pais (
    id_pais                 uuid         NOT NULL DEFAULT fn_uuid_v7(),
    cod_iso2                char(2)      NOT NULL,
    cod_iso3                char(3),
    cod_numerico            varchar(3),
    cod_cioc                varchar(3),
    nome_comum              varchar(200) NOT NULL,
    nome_oficial            varchar(300),
    nome_pt                 varchar(200),
    nome_nativo             jsonb,
    capital                 varchar(200),
    regiao                  varchar(100),
    sub_regiao              varchar(100),
    latitude                numeric(10,7),
    longitude               numeric(10,7),
    populacao               bigint,
    area_km2                numeric(16,2),
    ddi                     varchar(20),
    moedas                  jsonb,
    idiomas                 jsonb,
    fusos_horarios          jsonb,
    tld                     text[],
    bandeira_png            text,
    bandeira_svg            text,
    independente            boolean,
    membro_onu              boolean,
    -- nacionalidades / gentílicos
    nacionalidade_masc_en   varchar(150),
    nacionalidade_fem_en    varchar(150),
    nacionalidade_masc_fr   varchar(150),
    nacionalidade_fem_fr    varchar(150),
    nacionalidade_masc_pt   varchar(150),
    nacionalidade_fem_pt    varchar(150),
    id_csc                  integer,
    osm_relation_id         bigint,
    geom_centroide          geometry(Point, 4326),
    geom_limite             geometry(MultiPolygon, 4326),
    dt_criacao              timestamptz  NOT NULL DEFAULT now(),
    dt_atualizacao          timestamptz  NOT NULL DEFAULT now(),
    CONSTRAINT pk_pais      PRIMARY KEY (id_pais),
    CONSTRAINT uq_pais_iso2 UNIQUE (cod_iso2),
    CONSTRAINT uq_pais_iso3 UNIQUE (cod_iso3),
    CONSTRAINT uq_pais_csc  UNIQUE (id_csc)
);

-- ---------------------------------------------------------------------------
-- 2) tb_estado   (filho de tb_pais)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tb_estado (
    id_estado               uuid         NOT NULL DEFAULT fn_uuid_v7(),
    id_pais                 uuid         NOT NULL,
    cod_estado              varchar(20)  NOT NULL,
    iso3166_2               varchar(25),
    nome                    varchar(250) NOT NULL,
    tipo                    varchar(100),
    latitude                numeric(10,7),
    longitude               numeric(10,7),
    -- naturalidade / gentílico
    gentilico_masc          varchar(150),
    gentilico_fem           varchar(150),
    gentilico_fonte         varchar(20),
    id_csc                  integer,
    osm_relation_id         bigint,
    geom_centroide          geometry(Point, 4326),
    geom_limite             geometry(MultiPolygon, 4326),
    dt_criacao              timestamptz  NOT NULL DEFAULT now(),
    dt_atualizacao          timestamptz  NOT NULL DEFAULT now(),
    CONSTRAINT pk_estado          PRIMARY KEY (id_estado),
    CONSTRAINT fk_estado_pais     FOREIGN KEY (id_pais) REFERENCES tb_pais (id_pais)
                                  ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT uq_estado_pais_cod UNIQUE (id_pais, cod_estado),
    CONSTRAINT uq_estado_csc      UNIQUE (id_csc),
    -- alvo da FK composta de tb_cidade (garante coerência cidade-estado-país)
    CONSTRAINT uq_estado_id_pais  UNIQUE (id_estado, id_pais)
);

-- ---------------------------------------------------------------------------
-- 3) tb_cidade   (filho de tb_estado e tb_pais)
--    id_estado é NULL apenas para países sem divisão estadual no CSC.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tb_cidade (
    id_cidade               uuid         NOT NULL DEFAULT fn_uuid_v7(),
    id_estado               uuid,
    id_pais                 uuid         NOT NULL,
    nome                    varchar(250) NOT NULL,
    nome_normalizado        varchar(250) NOT NULL,
    tipo_local              varchar(30),
    latitude                numeric(10,7),
    longitude               numeric(10,7),
    populacao               bigint,
    wikidata_id             varchar(20),
    osm_id                  bigint,
    -- naturalidade / gentílico
    gentilico_masc          varchar(150),
    gentilico_fem           varchar(150),
    gentilico_fonte         varchar(20),
    id_csc                  integer      NOT NULL,
    geom                    geometry(Point, 4326),
    dt_criacao              timestamptz  NOT NULL DEFAULT now(),
    dt_atualizacao          timestamptz  NOT NULL DEFAULT now(),
    CONSTRAINT pk_cidade        PRIMARY KEY (id_cidade),
    CONSTRAINT fk_cidade_pais   FOREIGN KEY (id_pais) REFERENCES tb_pais (id_pais)
                                ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_cidade_estado FOREIGN KEY (id_estado, id_pais)
                                REFERENCES tb_estado (id_estado, id_pais)
                                ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT uq_cidade_csc    UNIQUE (id_csc)
);
"""

# =============================================================================
# 4. ÍNDICES  (GiST espaciais + B-Tree para FKs UUIDv7 e buscas)
# =============================================================================
SQL_INDICES = r"""
-- ---- GiST (espaciais) -----------------------------------------------------
CREATE INDEX IF NOT EXISTS gix_pais_geom_limite      ON tb_pais   USING GIST (geom_limite);
CREATE INDEX IF NOT EXISTS gix_pais_geom_centroide   ON tb_pais   USING GIST (geom_centroide);
CREATE INDEX IF NOT EXISTS gix_estado_geom_limite    ON tb_estado USING GIST (geom_limite);
CREATE INDEX IF NOT EXISTS gix_estado_geom_centroide ON tb_estado USING GIST (geom_centroide);
CREATE INDEX IF NOT EXISTS gix_cidade_geom           ON tb_cidade USING GIST (geom);

-- ---- B-Tree (FKs UUIDv7; o Postgres não indexa FKs automaticamente) ------
CREATE INDEX IF NOT EXISTS ix_estado_id_pais         ON tb_estado USING BTREE (id_pais);
CREATE INDEX IF NOT EXISTS ix_cidade_id_pais         ON tb_cidade USING BTREE (id_pais);
CREATE INDEX IF NOT EXISTS ix_cidade_id_estado       ON tb_cidade USING BTREE (id_estado);

-- ---- B-Tree de apoio a consultas hierárquicas por nome --------------------
CREATE INDEX IF NOT EXISTS ix_estado_pais_nome       ON tb_estado USING BTREE (id_pais, nome);
CREATE INDEX IF NOT EXISTS ix_cidade_estado_nome     ON tb_cidade USING BTREE (id_estado, nome_normalizado);
CREATE INDEX IF NOT EXISTS ix_pais_nome_comum        ON tb_pais   USING BTREE (nome_comum);

ANALYZE tb_pais;
ANALYZE tb_estado;
ANALYZE tb_cidade;
"""

# Correção de geometrias após a carga (complementa a validação do QGIS)
SQL_POS_CARGA = r"""
UPDATE tb_pais   SET geom_limite = ST_Multi(ST_CollectionExtract(ST_MakeValid(geom_limite), 3))
 WHERE geom_limite IS NOT NULL AND NOT ST_IsValid(geom_limite);
UPDATE tb_estado SET geom_limite = ST_Multi(ST_CollectionExtract(ST_MakeValid(geom_limite), 3))
 WHERE geom_limite IS NOT NULL AND NOT ST_IsValid(geom_limite);
"""

# =============================================================================
# 5. CÓDIGO DO ETL
# =============================================================================
import argparse
import csv
import hashlib
import json
import logging
import os
import re
import secrets
import sys
import time
import unicodedata
import uuid
from pathlib import Path

try:
    import requests
    import psycopg2
    from psycopg2.extras import Json, execute_values, register_uuid
    from shapely import to_wkt
    from shapely.geometry import LineString, MultiPolygon, Polygon
    from shapely.ops import polygonize, unary_union
    from shapely.validation import make_valid
    from tqdm import tqdm
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    DEPS_OK, _DEPS_ERR = True, None
except ImportError as _e:  # permite usar init-files/print-* sem dependências
    DEPS_OK, _DEPS_ERR = False, _e


def _bool(v: str) -> bool:
    return str(v).strip().lower() in ("1", "true", "t", "yes", "y", "sim")


class Cfg:
    """Lê as variáveis de ambiente (ver ENV_TEMPLATE)."""
    def __init__(self):
        g = os.getenv
        self.DB_HOST = g("DB_HOST", "localhost")
        self.DB_PORT = int(g("DB_PORT", "5432"))
        self.DB_NAME = g("DB_NAME", "db_msfederacao")
        self.DB_USER = g("DB_USER", "postgres")
        self.DB_PASSWORD = g("DB_PASSWORD", "")
        self.CSC_API_KEY = g("CSC_API_KEY", "")
        self.CSC_BASE_URL = g("CSC_BASE_URL", "https://api.countrystatecity.in/v1").rstrip("/")
        self.CSC_SLEEP = float(g("CSC_SLEEP", "0.2"))
        self.CSC_STATE_DETAILS = _bool(g("CSC_STATE_DETAILS", "true"))
        self.RC_URL = g("REST_COUNTRIES_URL", "https://restcountries.com/v3.1").rstrip("/")
        self.USE_OVERPASS = _bool(g("USE_OVERPASS", "true"))
        self.OVERPASS_URL = g("OVERPASS_URL", "https://overpass-api.de/api/interpreter")
        self.OVERPASS_TIMEOUT = int(g("OVERPASS_TIMEOUT", "300"))
        self.OVERPASS_SLEEP = float(g("OVERPASS_SLEEP", "2"))
        self.PLACE_TYPES = [t.strip() for t in g("OVERPASS_PLACE_TYPES", "city,town,village,municipality").split(",") if t.strip()]
        self.SIMPLIFY = float(g("SIMPLIFY_TOLERANCE", "0.001"))
        self.HTTP_RETRIES = int(g("HTTP_RETRIES", "5"))
        self.HTTP_TIMEOUT = int(g("HTTP_TIMEOUT", "360"))
        self.CACHE_DIR = Path(g("CACHE_DIR", "./.cache_etl"))
        self.GENTILICOS_CSV = g("GENTILICOS_CSV", "./gentilicos_pt.csv")
        self.COUNTRIES = [c.strip().upper() for c in g("COUNTRIES", "").split(",") if c.strip()]
        self.QGIS_ENABLED = _bool(g("QGIS_ENABLED", "false"))
        self.QGIS_PREFIX = g("QGIS_PREFIX_PATH", "/usr")
        self.QGIS_PROJECT = g("QGIS_PROJECT_PATH", "./msfederacao.qgz")
        self.LOG_LEVEL = g("LOG_LEVEL", "INFO").upper()


cfg = Cfg()
logging.basicConfig(level=getattr(logging, cfg.LOG_LEVEL, logging.INFO),
                    format="%(asctime)s %(levelname)-7s %(message)s")
log = logging.getLogger("etl")

# ----------------------------- UUIDv7 (Python) ------------------------------
_last_ms, _last_seq = 0, 0


def uuid7() -> uuid.UUID:
    """UUIDv7 monotônico (RFC 9562): 48b timestamp ms | ver 7 | 12b seq | var | 62b random."""
    global _last_ms, _last_seq
    ms = time.time_ns() // 1_000_000
    if ms <= _last_ms:
        ms = _last_ms
        _last_seq += 1
        if _last_seq > 0xFFF:
            ms += 1
            _last_seq = secrets.randbits(8)
    else:
        _last_seq = secrets.randbits(8)
    _last_ms = ms
    value = ((ms & ((1 << 48) - 1)) << 80) | (0x7 << 76) | (_last_seq << 64) \
        | (0b10 << 62) | secrets.randbits(62)
    return uuid.UUID(int=value)


# ----------------------------- utilidades -----------------------------------
def norm(s) -> str:
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).casefold()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def _f(v):
    try:
        return float(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _i(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def point_wkt(lon, lat):
    return f"POINT({lon} {lat})" if lon is not None and lat is not None else None


# ----------------------------- HTTP com cache -------------------------------
_session = None


def _sess():
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers["User-Agent"] = "etl-msfederacao/1.0 (+geodata pipeline)"
    return _session


def cached_request(method, url, *, params=None, headers=None, data=None,
                   sleep=0.0, ok_404=False):
    """Requisição JSON com cache em disco, retry e backoff. Retorna o JSON."""
    cfg.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = json.dumps([method, url, params, data], sort_keys=True, default=str)
    path = cfg.CACHE_DIR / (hashlib.sha1(key.encode()).hexdigest() + ".json")
    if path.exists():
        return json.loads(path.read_text("utf-8"))
    last = None
    for attempt in range(1, cfg.HTTP_RETRIES + 1):
        try:
            r = _sess().request(method, url, params=params, headers=headers,
                                data=data, timeout=cfg.HTTP_TIMEOUT)
            if ok_404 and r.status_code == 404:
                return None
            if r.status_code in (429, 502, 503, 504):
                ra = r.headers.get("Retry-After", "")
                wait = int(ra) if ra.isdigit() else 5 * 2 ** attempt
                log.warning("HTTP %s em %s; aguardando %ss", r.status_code, url, wait)
                time.sleep(wait)
                continue
            r.raise_for_status()
            js = r.json()
            path.write_text(json.dumps(js, ensure_ascii=False), "utf-8")
            if sleep:
                time.sleep(sleep)
            return js
        except (requests.RequestException, ValueError) as e:
            last = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Falha em {url}: {last}")


def csc(path):
    if not cfg.CSC_API_KEY:
        raise SystemExit("CSC_API_KEY não definida.")
    js = cached_request("GET", cfg.CSC_BASE_URL + path,
                        headers={"X-CSCAPI-KEY": cfg.CSC_API_KEY},
                        sleep=cfg.CSC_SLEEP, ok_404=True)
    return js if js is not None else []


# ----------------------------- Overpass / geometria -------------------------
def overpass(query):
    js = cached_request("POST", cfg.OVERPASS_URL, data={"data": query},
                        sleep=cfg.OVERPASS_SLEEP)
    remark = (js or {}).get("remark", "")
    if "runtime error" in remark or "timed out" in remark:
        # remove o cache para permitir nova tentativa depois
        key = json.dumps(["POST", cfg.OVERPASS_URL, {"data": query}], sort_keys=True, default=str)
        (cfg.CACHE_DIR / (hashlib.sha1(key.encode()).hexdigest() + ".json")).unlink(missing_ok=True)
        raise RuntimeError(f"Overpass: {remark}")
    return js.get("elements", [])


def _esc(s):
    return str(s).replace("\\", "\\\\").replace('"', '\\"')


def q_country(iso2):
    return (f'[out:json][timeout:{cfg.OVERPASS_TIMEOUT}];'
            f'relation["boundary"="administrative"]["admin_level"="2"]["ISO3166-1"="{_esc(iso2)}"];out geom;')


def q_state(iso3166_2):
    return (f'[out:json][timeout:{cfg.OVERPASS_TIMEOUT}];'
            f'relation["boundary"="administrative"]["ISO3166-2"="{_esc(iso3166_2)}"];out geom;')


def q_state_by_name(iso2, nome):
    return (f'[out:json][timeout:{cfg.OVERPASS_TIMEOUT}];'
            f'area["ISO3166-1"="{_esc(iso2)}"]["admin_level"="2"]->.c;'
            f'relation(area.c)["boundary"="administrative"]["name"="{_esc(nome)}"];out geom;')


def q_places(rel_id):
    types = "|".join(cfg.PLACE_TYPES)
    return (f'[out:json][timeout:{cfg.OVERPASS_TIMEOUT}];'
            f'area(id:{3600000000 + int(rel_id)})->.a;'
            f'node(area.a)["place"~"^({types})$"]["name"];out body;')


def best_relation(elements):
    rels = [e for e in elements if e.get("type") == "relation" and e.get("members")]
    return max(rels, key=lambda e: len(e["members"])) if rels else None


def _polys(g):
    if g is None or g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    return [p for sub in getattr(g, "geoms", []) for p in _polys(sub)]


def relation_to_geom(rel):
    """Monta MultiPolygon a partir dos ways (outer/inner) de uma relação OSM (out geom)."""
    outers, inners = [], []
    for m in rel.get("members", []):
        if m.get("type") != "way" or not m.get("geometry"):
            continue
        pts = [(p["lon"], p["lat"]) for p in m["geometry"]]
        if len(pts) < 2:
            continue
        (inners if m.get("role") == "inner" else outers).append(LineString(pts))
    if not outers:
        return None
    outer = unary_union(list(polygonize(unary_union(outers))))
    if outer.is_empty:
        return None
    if inners:
        hole = unary_union(list(polygonize(unary_union(inners))))
        if not hole.is_empty:
            outer = outer.difference(hole)
    geom = make_valid(outer)
    if cfg.SIMPLIFY > 0:
        geom = geom.simplify(cfg.SIMPLIFY, preserve_topology=True)
    polys = _polys(geom)
    return MultiPolygon(polys) if polys else None


def geom_wkt(g):
    return to_wkt(g, rounding_precision=6) if g is not None else None


# ----------------------------- gentílicos (CSV) -----------------------------
def load_gentilicos(path):
    d = {}
    if not path or not Path(path).exists():
        log.info("CSV de gentílicos pt não encontrado (%s); colunas _pt ficarão nulas.", path)
        return d
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            nivel = (r.get("nivel") or "").strip().lower()
            iso = (r.get("iso2") or "").strip().upper()
            est = (r.get("cod_estado") or "").strip().upper()
            nome = norm(r.get("nome"))
            key = (("pais", iso) if nivel == "pais" else
                   ("estado", iso, est) if nivel == "estado" else
                   ("cidade", iso, est, nome))
            d[key] = ((r.get("gentilico_masc") or "").strip() or None,
                      (r.get("gentilico_fem") or "").strip() or None)
    log.info("Gentílicos carregados do CSV: %d", len(d))
    return d


# ----------------------------- banco de dados -------------------------------
def connect():
    register_uuid()
    return psycopg2.connect(host=cfg.DB_HOST, port=cfg.DB_PORT, dbname=cfg.DB_NAME,
                            user=cfg.DB_USER, password=cfg.DB_PASSWORD)


def run_sql(conn, sql, what):
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    log.info("OK: %s", what)


def upsert(conn, table, pk, conflict, cols, rows, *, geom_cols=(), json_cols=()):
    """UPSERT em lote. Mantém o UUID existente; COALESCE preserva valores já carregados."""
    if not rows:
        return 0
    seen, uniq = set(), []
    for r in rows:  # evita "cannot affect row a second time"
        k = tuple(r.get(c) for c in conflict)
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    all_cols = [pk] + cols
    tpl = "(" + ",".join(
        "%s" if c == pk else
        "ST_GeomFromText(%s::text,4326)" if c in geom_cols else "%s"
        for c in all_cols) + ")"
    values = []
    for r in uniq:
        row = [uuid7()]
        for c in cols:
            v = r.get(c)
            row.append(Json(v) if (c in json_cols and v is not None) else v)
        values.append(tuple(row))
    upd = ", ".join(f"{c}=COALESCE(EXCLUDED.{c}, {table}.{c})" for c in cols if c not in conflict)
    sql = (f"INSERT INTO {table} ({','.join(all_cols)}) VALUES %s "
           f"ON CONFLICT ({','.join(conflict)}) DO UPDATE SET {upd}, dt_atualizacao = now()")
    with conn.cursor() as cur:
        execute_values(cur, sql, values, template=tpl, page_size=1000)
    conn.commit()
    return len(uniq)


# =============================================================================
# ETAPA: PAÍSES  (REST Countries + CSC + Overpass)
# =============================================================================
RC_BATCHES = [  # a API v3.1 aceita no máximo 10 campos por requisição em /all
    "name,cca2,cca3,ccn3,demonyms,capital,region,subregion,latlng,population",
    "cca2,area,idd,currencies,languages,flags,tld,translations,timezones,unMember",
    "cca2,independent,cioc",
]
PAIS_COLS = ["cod_iso2", "cod_iso3", "cod_numerico", "cod_cioc", "nome_comum", "nome_oficial",
             "nome_pt", "nome_nativo", "capital", "regiao", "sub_regiao", "latitude", "longitude",
             "populacao", "area_km2", "ddi", "moedas", "idiomas", "fusos_horarios", "tld",
             "bandeira_png", "bandeira_svg", "independente", "membro_onu",
             "nacionalidade_masc_en", "nacionalidade_fem_en", "nacionalidade_masc_fr",
             "nacionalidade_fem_fr", "nacionalidade_masc_pt", "nacionalidade_fem_pt",
             "id_csc", "osm_relation_id", "geom_centroide", "geom_limite"]


def etl_paises(conn, gent):
    log.info("=== PAÍSES ===")
    rc = {}
    for fields in RC_BATCHES:
        data = cached_request("GET", f"{cfg.RC_URL}/all", params={"fields": fields})
        for c in data:
            rc.setdefault(c["cca2"], {}).update(c)
    csc_by = {c.get("iso2"): c for c in csc("/countries") if c.get("iso2")}
    isos = sorted(set(rc) | set(csc_by))
    if cfg.COUNTRIES:
        isos = [i for i in isos if i in cfg.COUNTRIES]
    log.info("Países a processar: %d", len(isos))

    rows = []
    for iso in tqdm(isos, desc="países"):
        r, k = rc.get(iso, {}), csc_by.get(iso, {})
        nm = r.get("name", {})
        dem = r.get("demonyms", {})
        ll = r.get("latlng") or []
        lat = ll[0] if len(ll) == 2 else _f(k.get("latitude"))
        lon = ll[1] if len(ll) == 2 else _f(k.get("longitude"))
        idd = r.get("idd") or {}
        root, suf = idd.get("root") or "", idd.get("suffixes") or []
        ddi = root + suf[0] if (root and len(suf) == 1) else root or (
            "+" + str(k["phonecode"]).lstrip("+") if k.get("phonecode") else None)
        flags = r.get("flags") or {}
        g = gent.get(("pais", iso), (None, None))

        rel = geom = None
        if cfg.USE_OVERPASS:
            try:
                rel = best_relation(overpass(q_country(iso)))
                geom = relation_to_geom(rel) if rel else None
            except Exception as e:
                log.warning("Overpass país %s: %s", iso, e)

        rows.append(dict(
            cod_iso2=iso, cod_iso3=r.get("cca3") or k.get("iso3"),
            cod_numerico=r.get("ccn3") or k.get("numeric_code"), cod_cioc=r.get("cioc"),
            nome_comum=nm.get("common") or k.get("name") or iso,
            nome_oficial=nm.get("official"),
            nome_pt=((r.get("translations") or {}).get("por") or {}).get("common"),
            nome_nativo=nm.get("nativeName"),
            capital=(r.get("capital") or [k.get("capital")])[0],
            regiao=r.get("region") or k.get("region"),
            sub_regiao=r.get("subregion") or k.get("subregion"),
            latitude=lat, longitude=lon, populacao=_i(r.get("population")),
            area_km2=_f(r.get("area")), ddi=ddi,
            moedas=r.get("currencies"), idiomas=r.get("languages"),
            fusos_horarios=r.get("timezones") or k.get("timezones"),
            tld=r.get("tld"), bandeira_png=flags.get("png"), bandeira_svg=flags.get("svg"),
            independente=r.get("independent"), membro_onu=r.get("unMember"),
            nacionalidade_masc_en=(dem.get("eng") or {}).get("m"),
            nacionalidade_fem_en=(dem.get("eng") or {}).get("f"),
            nacionalidade_masc_fr=(dem.get("fra") or {}).get("m"),
            nacionalidade_fem_fr=(dem.get("fra") or {}).get("f"),
            nacionalidade_masc_pt=g[0], nacionalidade_fem_pt=g[1],
            id_csc=_i(k.get("id")), osm_relation_id=rel["id"] if rel else None,
            geom_centroide=point_wkt(lon, lat), geom_limite=geom_wkt(geom)))

    n = upsert(conn, "tb_pais", "id_pais", ["cod_iso2"], PAIS_COLS, rows,
               geom_cols=("geom_centroide", "geom_limite"),
               json_cols=("nome_nativo", "moedas", "idiomas", "fusos_horarios"))
    log.info("tb_pais: %d registros processados", n)


# =============================================================================
# ETAPA: ESTADOS  (CSC + Overpass)
# =============================================================================
ESTADO_COLS = ["id_pais", "cod_estado", "iso3166_2", "nome", "tipo", "latitude", "longitude",
               "gentilico_masc", "gentilico_fem", "gentilico_fonte", "id_csc",
               "osm_relation_id", "geom_centroide", "geom_limite"]


def _paises_db(conn):
    with conn.cursor() as cur:
        if cfg.COUNTRIES:
            cur.execute("SELECT id_pais, cod_iso2 FROM tb_pais WHERE cod_iso2 = ANY(%s) ORDER BY 2",
                        (cfg.COUNTRIES,))
        else:
            cur.execute("SELECT id_pais, cod_iso2 FROM tb_pais ORDER BY 2")
        return cur.fetchall()


def etl_estados(conn, gent):
    log.info("=== ESTADOS ===")
    total = 0
    for id_pais, iso in tqdm(_paises_db(conn), desc="estados"):
        rows = []
        for s in csc(f"/countries/{iso}/states"):
            code = str(s.get("iso2") or s["id"]).upper()
            det = {}
            if cfg.CSC_STATE_DETAILS and s.get("iso2"):
                d = csc(f"/countries/{iso}/states/{s['iso2']}")
                det = d if isinstance(d, dict) else {}
            nome = s["name"]
            lat, lon = _f(det.get("latitude")), _f(det.get("longitude"))
            iso_2 = f"{iso}-{code}"

            rel = geom = None
            if cfg.USE_OVERPASS:
                try:
                    rel = best_relation(overpass(q_state(iso_2))) \
                        or best_relation(overpass(q_state_by_name(iso, nome)))
                    geom = relation_to_geom(rel) if rel else None
                except Exception as e:
                    log.warning("Overpass estado %s: %s", iso_2, e)
            if (lat is None or lon is None) and geom is not None:
                rp = geom.representative_point()
                lon, lat = round(rp.x, 7), round(rp.y, 7)
            g = gent.get(("estado", iso, code), (None, None))
            rows.append(dict(
                id_pais=id_pais, cod_estado=code, iso3166_2=iso_2, nome=nome,
                tipo=det.get("type"), latitude=lat, longitude=lon,
                gentilico_masc=g[0], gentilico_fem=g[1],
                gentilico_fonte="csv" if (g[0] or g[1]) else None,
                id_csc=_i(s.get("id")), osm_relation_id=rel["id"] if rel else None,
                geom_centroide=point_wkt(lon, lat), geom_limite=geom_wkt(geom)))
        total += upsert(conn, "tb_estado", "id_estado", ["id_pais", "cod_estado"], ESTADO_COLS,
                        rows, geom_cols=("geom_centroide", "geom_limite"))
    log.info("tb_estado: %d registros processados", total)


# =============================================================================
# ETAPA: CIDADES  (CSC + Overpass)
# =============================================================================
CIDADE_COLS = ["id_estado", "id_pais", "nome", "nome_normalizado", "tipo_local", "latitude",
               "longitude", "populacao", "wikidata_id", "osm_id", "gentilico_masc",
               "gentilico_fem", "gentilico_fonte", "id_csc", "geom"]
_RANK = {"city": 0, "town": 1, "municipality": 2, "village": 3, "hamlet": 4}


def _index_places(rel_id):
    """Overpass: nós place=* da área -> dicionário nome_normalizado -> melhor nó."""
    idx = {}
    if not (cfg.USE_OVERPASS and rel_id):
        return idx
    try:
        for el in overpass(q_places(rel_id)):
            tags = el.get("tags", {})
            for nm in {tags.get("name"), tags.get("name:pt"), tags.get("name:en")}:
                if not nm:
                    continue
                k = norm(nm)
                cur = idx.get(k)
                if cur is None or _RANK.get(tags.get("place"), 9) < _RANK.get(cur["tags"].get("place"), 9):
                    idx[k] = el
    except Exception as e:
        log.warning("Overpass cidades (relation %s): %s", rel_id, e)
    return idx


def _cidades_rows(cities, iso, cod_estado, id_estado, id_pais, rel_id, gent):
    idx = _index_places(rel_id)
    rows = []
    for c in cities:
        nome = c["name"]
        nn = norm(nome)
        el = idx.get(nn)
        tags = el.get("tags", {}) if el else {}
        lat = el.get("lat") if el else None
        lon = el.get("lon") if el else None
        if lat is None or lon is None:
            lat, lon = _f(c.get("latitude")), _f(c.get("longitude"))
        g = gent.get(("cidade", iso, cod_estado, nn))
        fonte = "csv" if g else None
        if not g:
            osm_g = tags.get("demonym:pt") or tags.get("demonym")
            g, fonte = ((osm_g, None), "osm") if osm_g else ((None, None), None)
        rows.append(dict(
            id_estado=id_estado, id_pais=id_pais, nome=nome, nome_normalizado=nn,
            tipo_local=tags.get("place"), latitude=lat, longitude=lon,
            populacao=_i(tags.get("population")), wikidata_id=tags.get("wikidata"),
            osm_id=el.get("id") if el else None, gentilico_masc=g[0], gentilico_fem=g[1],
            gentilico_fonte=fonte, id_csc=_i(c["id"]), geom=point_wkt(lon, lat)))
    return rows


def etl_cidades(conn, gent):
    log.info("=== CIDADES ===")
    total = 0
    filtro = "WHERE p.cod_iso2 = ANY(%s)" if cfg.COUNTRIES else ""
    args = (cfg.COUNTRIES,) if cfg.COUNTRIES else None
    with conn.cursor() as cur:
        cur.execute(f"""SELECT e.id_estado, e.id_pais, p.cod_iso2, e.cod_estado, e.osm_relation_id
                          FROM tb_estado e JOIN tb_pais p USING (id_pais) {filtro}
                         ORDER BY p.cod_iso2, e.cod_estado""", args)
        estados = cur.fetchall()
        cur.execute(f"""SELECT p.id_pais, p.cod_iso2, p.osm_relation_id FROM tb_pais p
                         {filtro + ' AND' if filtro else 'WHERE'}
                         NOT EXISTS (SELECT 1 FROM tb_estado e WHERE e.id_pais = p.id_pais)
                         ORDER BY p.cod_iso2""", args)
        sem_estado = cur.fetchall()

    for id_estado, id_pais, iso, cod, rel_id in tqdm(estados, desc="cidades/estado"):
        cities = csc(f"/countries/{iso}/states/{cod}/cities")
        rows = _cidades_rows(cities, iso, cod, id_estado, id_pais, rel_id, gent)
        total += upsert(conn, "tb_cidade", "id_cidade", ["id_csc"], CIDADE_COLS, rows,
                        geom_cols=("geom",))

    for id_pais, iso, rel_id in tqdm(sem_estado, desc="cidades/país sem estados"):
        cities = csc(f"/countries/{iso}/cities")
        rows = _cidades_rows(cities, iso, "", None, id_pais, rel_id, gent)
        total += upsert(conn, "tb_cidade", "id_cidade", ["id_csc"], CIDADE_COLS, rows,
                        geom_cols=("geom",))
    log.info("tb_cidade: %d registros processados", total)


# =============================================================================
# ETAPA: QGIS  (validação geométrica + projeto .qgz para QA visual)
#   Execute com o Python do QGIS (ex.: python3 do sistema com qgis instalado,
#   ou OSGeo4W Shell no Windows). Defina QGIS_ENABLED=true.
# =============================================================================
def etl_qgis(conn=None):
    if not cfg.QGIS_ENABLED:
        log.info("Etapa QGIS desabilitada (QGIS_ENABLED=false).")
        return
    try:
        from qgis.core import (QgsApplication, QgsCoordinateReferenceSystem,
                               QgsDataSourceUri, QgsProject, QgsVectorLayer)
    except ImportError:
        log.error("PyQGIS indisponível neste interpretador. Rode `python etl_msfederacao.py qgis` "
                  "com o Python do QGIS e ajuste QGIS_PREFIX_PATH.")
        return
    QgsApplication.setPrefixPath(cfg.QGIS_PREFIX, True)
    app = QgsApplication([], False)
    app.initQgis()
    sys.path.append(os.path.join(cfg.QGIS_PREFIX, "share", "qgis", "python", "plugins"))
    sys.path.append(os.path.join(cfg.QGIS_PREFIX, "python", "plugins"))
    import processing
    from processing.core.Processing import Processing
    Processing.initialize()

    project = QgsProject.instance()
    project.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
    camadas = [("tb_pais", "geom_limite", "id_pais"), ("tb_estado", "geom_limite", "id_estado"),
               ("tb_cidade", "geom", "id_cidade")]
    for tabela, geomcol, pk in camadas:
        uri = QgsDataSourceUri()
        # atenção: as credenciais ficam gravadas no .qgz; use-o apenas localmente
        uri.setConnection(cfg.DB_HOST, str(cfg.DB_PORT), cfg.DB_NAME, cfg.DB_USER, cfg.DB_PASSWORD)
        uri.setDataSource("public", tabela, geomcol, "", pk)
        layer = QgsVectorLayer(uri.uri(False), tabela, "postgres")
        if not layer.isValid():
            log.error("Camada inválida no QGIS: %s", tabela)
            continue
        project.addMapLayer(layer)
        res = processing.run("qgis:checkvalidity", {
            "INPUT_LAYER": layer, "METHOD": 2,  # 2 = GEOS
            "VALID_OUTPUT": "memory:", "INVALID_OUTPUT": "memory:", "ERROR_OUTPUT": "memory:"})
        log.info("QGIS %-10s feições=%s | válidas=%s | inválidas=%s",
                 tabela, layer.featureCount(), res.get("VALID_COUNT"), res.get("INVALID_COUNT"))
    project.write(cfg.QGIS_PROJECT)
    log.info("Projeto QGIS gravado em %s", cfg.QGIS_PROJECT)
    app.exitQgis()


# =============================================================================
# 6. CLI
# =============================================================================
def _write_setup_files(directory):
    d = Path(directory)
    d.mkdir(parents=True, exist_ok=True)
    (d / "requirements.txt").write_text(REQUIREMENTS_TXT, "utf-8")
    (d / ".env.example").write_text(ENV_TEMPLATE, "utf-8")
    (d / "schema.sql").write_text(SQL_DDL + "\n" + SQL_INDICES, "utf-8")
    print(f"Gerados em {d.resolve()}: requirements.txt, .env.example, schema.sql")


def main():
    ap = argparse.ArgumentParser(description="ETL geográfico mundial -> PostGIS (db_msfederacao)")
    ap.add_argument("comando", choices=["init-files", "print-sql", "print-requirements", "print-env",
                                        "schema", "paises", "estados", "cidades", "indices",
                                        "qgis", "run"])
    ap.add_argument("--dir", default=".", help="destino do init-files")
    ap.add_argument("--paises", help="lista ISO2 (ex.: BR,PT,US); sobrescreve COUNTRIES")
    a = ap.parse_args()

    if a.comando == "init-files":
        return _write_setup_files(a.dir)
    if a.comando == "print-sql":
        return print(SQL_DDL + "\n" + SQL_INDICES)
    if a.comando == "print-requirements":
        return print(REQUIREMENTS_TXT)
    if a.comando == "print-env":
        return print(ENV_TEMPLATE)

    if not DEPS_OK:
        raise SystemExit(f"Dependências ausentes ({_DEPS_ERR}). Rode: pip install -r requirements.txt")
    if a.paises:
        cfg.COUNTRIES = [c.strip().upper() for c in a.paises.split(",") if c.strip()]

    gent = load_gentilicos(cfg.GENTILICOS_CSV)
    conn = connect()
    try:
        if a.comando in ("schema", "run"):
            run_sql(conn, SQL_DDL, "DDL (extensão, fn_uuid_v7, tb_pais, tb_estado, tb_cidade)")
        if a.comando in ("paises", "run"):
            etl_paises(conn, gent)
        if a.comando in ("estados", "run"):
            etl_estados(conn, gent)
        if a.comando in ("cidades", "run"):
            etl_cidades(conn, gent)
        if a.comando in ("run",):
            run_sql(conn, SQL_POS_CARGA, "correção de geometrias (ST_MakeValid)")
        if a.comando in ("indices", "run"):
            run_sql(conn, SQL_INDICES, "índices GiST e B-Tree + ANALYZE")
        if a.comando in ("qgis", "run"):
            etl_qgis(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
