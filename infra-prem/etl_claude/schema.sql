
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
