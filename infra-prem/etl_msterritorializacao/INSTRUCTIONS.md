# PIPELINE ETL - MSTERRITORIALIZAÇÃO

## Visao Geral

Este repositório contém o **pipeline ETL** para carga a partir da **API de Localidade e de Malhas do IBGE** bem como a *normalização* das base final para compatibilidade com a *db_msterritorializacao*  

---

## Requisitos

- psycopg[binary]>=3.2,<4
- requests>=2.32,<3
- pyshp>=2.3,<4

---

## Rodando o ETL

```
cd infra-prem
```

1. País:

```
docker compose --env-file .env.fsw -f docker-compose.fsw.yml -f docker-compose.etl-msterritorializacao.yml --profile etl run --rm --no-deps --build etl-pais
```
2. Estado:  

```
docker compose --env-file .env.fsw -f docker-compose.fsw.yml -f docker-compose.etl-msterritorializacao.yml   --profile etl run --rm --no-deps --build etl-estado
```

3. Município:

```
docker compose --env-file .env.fsw -f docker-compose.fsw.yml -f docker-compose.etl-msterritorializacao.yml   --profile etl run --rm --no-deps --build etl-municipio
```

4. Bairro:

```
docker compose --env-file .env.fsw -f docker-compose.fsw.yml -f docker-compose.etl-msterritorializacao.yml --profile etl run --rm --no-deps --build etl-bairro
```

- Quando concluído pipeline, o resultado final dos **DDLs das tabelas** são:

```

CREATE TABLE db_msterritorializacao.tb_pais (
    co_m49                       smallint     PRIMARY KEY,
    co_iso_alpha2                char(2),
    co_iso_alpha3                char(3),
    no_pais                      text         NOT NULL,
    co_regiao_m49                smallint,
    no_regiao                    text,
    co_subregiao_m49             smallint,
    no_subregiao                 text,
    co_regiao_intermediaria_m49  smallint,
    no_regiao_intermediaria      text,
    geom                         geometry(MultiPolygon, 4326),
    no_fonte_geom                text,
    dt_carga                     timestamptz  NOT NULL DEFAULT now()
);

CREATE INDEX ix_tb_pais_geom ON db_msterritorializacao.tb_pais USING gist (geom);
CREATE UNIQUE INDEX ux_tb_pais_iso2 ON db_msterritorializacao.tb_pais (co_iso_alpha2) WHERE co_iso_alpha2 IS NOT NULL;


CREATE TABLE db_msterritorializacao.tb_estado (
	co_uf int2 NOT NULL,
	sg_uf bpchar(2) NOT NULL,
	no_estado text NOT NULL,
	co_pais_m49 int2 DEFAULT 76 NOT NULL,
	co_regiao int2 NOT NULL,
	sg_regiao varchar(2) NULL,
	no_regiao text NOT NULL,
	geom public.geometry(multipolygon, 4326) NULL,
	no_fonte_geom text NULL,
	dt_carga timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT tb_estado_co_pais_m49_not_null NOT NULL co_pais_m49,
	CONSTRAINT tb_estado_co_regiao_not_null NOT NULL co_regiao,
	CONSTRAINT tb_estado_co_uf_not_null NOT NULL co_uf,
	CONSTRAINT tb_estado_dt_carga_not_null NOT NULL dt_carga,
	CONSTRAINT tb_estado_no_estado_not_null NOT NULL no_estado,
	CONSTRAINT tb_estado_no_regiao_not_null NOT NULL no_regiao,
	CONSTRAINT tb_estado_pkey PRIMARY KEY (co_uf),
	CONSTRAINT tb_estado_sg_uf_not_null NOT NULL sg_uf,
	CONSTRAINT uq_tb_estado_sg_uf UNIQUE (sg_uf),
	CONSTRAINT fk_tb_estado_tb_pais FOREIGN KEY (co_pais_m49) REFERENCES db_msterritorializacao.tb_pais(codigo_pais_onu) ON DELETE RESTRICT ON UPDATE CASCADE
);
CREATE INDEX ix_tb_estado_co_pais_m49 ON db_msterritorializacao.tb_estado USING btree (co_pais_m49);
CREATE INDEX ix_tb_estado_co_regiao ON db_msterritorializacao.tb_estado USING btree (co_regiao);
CREATE INDEX ix_tb_estado_geom ON db_msterritorializacao.tb_estado USING gist (geom);

CREATE TABLE db_msterritorializacao.tb_municipio (
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

    CONSTRAINT ck_tb_municipio_co_uf CHECK (co_municipio / 100000 = co_uf),
    CONSTRAINT fk_tb_municipio_tb_estado FOREIGN KEY (co_uf)
        REFERENCES db_msterritorializacao.tb_estado (co_uf)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX ix_tb_municipio_co_uf ON db_msterritorializacao.tb_municipio (co_uf);
CREATE INDEX ix_tb_municipio_geom  ON db_msterritorializacao.tb_municipio USING gist (geom);


CREATE TABLE db_msterritorializacao.tb_bairro (
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

    CONSTRAINT ck_tb_bairro_co_municipio CHECK (co_bairro / 1000 = co_municipio),
    CONSTRAINT fk_tb_bairro_tb_municipio FOREIGN KEY (co_municipio)
        REFERENCES db_msterritorializacao.tb_municipio (co_municipio)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX ix_tb_bairro_co_municipio ON db_msterritorializacao.tb_bairro (co_municipio);
CREATE INDEX ix_tb_bairro_geom ON db_msterritorializacao.tb_bairro USING gist (geom);


```

## Normalizando a base de dados

- Como o ETL traz a estrutura nativa de DDLs das APIs do IBGE; precisamos ajustá-las as necessidades do negócio 

### Atualização das colunas/campos das tabelas:

1. Altera db_msterritorializacao.tb_pais: 

```
-- Renomeia as colunas
ALTER TABLE db_msterritorializacao.tb_pais RENAME COLUMN co_m49 TO codigo_pais_onu;
ALTER TABLE db_msterritorializacao.tb_pais RENAME COLUMN co_iso_alpha2 TO sigla_pais_alfa2;
ALTER TABLE db_msterritorializacao.tb_pais RENAME COLUMN co_iso_alpha3 TO sigla_pais_alfa3;
ALTER TABLE db_msterritorializacao.tb_pais RENAME COLUMN no_pais TO nome_pais_pt;
ALTER TABLE db_msterritorializacao.tb_pais RENAME COLUMN co_regiao_m49 TO codigo_regiao_onu;
ALTER TABLE db_msterritorializacao.tb_pais RENAME COLUMN no_regiao TO nome_regiao_onu;
ALTER TABLE db_msterritorializacao.tb_pais RENAME COLUMN co_subregiao_m49 TO codigo_subregiao_onu;
ALTER TABLE db_msterritorializacao.tb_pais RENAME COLUMN no_subregiao TO nome_subregiao_onu;
ALTER TABLE db_msterritorializacao.tb_pais RENAME COLUMN co_regiao_intermediaria_m49 TO codigo_regiao_intermediaria_onu;
ALTER TABLE db_msterritorializacao.tb_pais RENAME COLUMN no_regiao_intermediaria TO nome_regiao_intermediaria_onu;
ALTER TABLE db_msterritorializacao.tb_pais RENAME COLUMN geom TO geometria_pais;
ALTER TABLE db_msterritorializacao.tb_pais RENAME COLUMN no_fonte_geom TO origem_geometria_pais;
ALTER TABLE db_msterritorializacao.tb_pais RENAME COLUMN dt_carga TO data_carga_pipeline_etl_pais;

-- Índices, para os nomes continuarem coerentes com as colunas
ALTER INDEX db_msterritorializacao.ix_tb_pais_geom RENAME TO ix_tb_pais_geometria_pais;
ALTER INDEX db_msterritorializacao.ux_tb_pais_iso2 RENAME TO ux_tb_pais_sigla_pais_alfa2;
```
2. Altera db_msterritorializacao.tb_estado: 

```
-- Colunas de tb_estado
ALTER TABLE db_msterritorializacao.tb_estado RENAME COLUMN co_uf TO codigo_estado_ibge;
ALTER TABLE db_msterritorializacao.tb_estado RENAME COLUMN sg_uf TO sigla_estado;
ALTER TABLE db_msterritorializacao.tb_estado RENAME COLUMN no_estado TO nome_estado;
ALTER TABLE db_msterritorializacao.tb_estado RENAME COLUMN co_pais_m49 TO codigo_pais_onu;
ALTER TABLE db_msterritorializacao.tb_estado RENAME COLUMN co_regiao TO codigo_regiao_ibge;
ALTER TABLE db_msterritorializacao.tb_estado RENAME COLUMN sg_regiao TO sigla_regiao;
ALTER TABLE db_msterritorializacao.tb_estado RENAME COLUMN no_regiao TO nome_regiao;
ALTER TABLE db_msterritorializacao.tb_estado RENAME COLUMN geom TO geometria_estado;
ALTER TABLE db_msterritorializacao.tb_estado RENAME COLUMN no_fonte_geom TO origem_geometria_estado;
ALTER TABLE db_msterritorializacao.tb_estado RENAME COLUMN dt_carga TO data_carga_pipeline_etl_estado;

-- Índices
ALTER INDEX db_msterritorializacao.ix_tb_estado_co_pais_m49 RENAME TO ix_tb_estado_codigo_pais_onu;
ALTER INDEX db_msterritorializacao.ix_tb_estado_co_regiao RENAME TO ix_tb_estado_codigo_regiao_ibge;
ALTER INDEX db_msterritorializacao.ix_tb_estado_geom RENAME TO ix_tb_estado_geometria_estado;

-- Constraint UNIQUE da sigla (renomeia também o índice que a sustenta)
ALTER TABLE db_msterritorializacao.tb_estado RENAME CONSTRAINT uq_tb_estado_sg_uf TO uq_tb_estado_sigla_estado;
```
3. Altera db_msterritorializacao.tb_municipio:

```
-- Colunas de tb_municipio
ALTER TABLE db_msterritorializacao.tb_municipio RENAME COLUMN co_municipio TO codigo_municipio_ibge;
ALTER TABLE db_msterritorializacao.tb_municipio RENAME COLUMN no_municipio TO nome_municipio_ibge;
ALTER TABLE db_msterritorializacao.tb_municipio RENAME COLUMN co_uf TO codigo_estado_ibge;
ALTER TABLE db_msterritorializacao.tb_municipio RENAME COLUMN co_microrregiao TO codigo_microrregiao_ibge;
ALTER TABLE db_msterritorializacao.tb_municipio RENAME COLUMN no_microrregiao TO nome_microrregiao_ibge;
ALTER TABLE db_msterritorializacao.tb_municipio RENAME COLUMN co_mesorregiao TO codigo_mesorregiao_ibge;
ALTER TABLE db_msterritorializacao.tb_municipio RENAME COLUMN no_mesorregiao TO nome_mesorregiao_ibge;
ALTER TABLE db_msterritorializacao.tb_municipio RENAME COLUMN co_regiao_imediata TO codigo_regiao_imediata_ibge;
ALTER TABLE db_msterritorializacao.tb_municipio RENAME COLUMN no_regiao_imediata TO nome_regiao_imediata_ibge;
ALTER TABLE db_msterritorializacao.tb_municipio RENAME COLUMN co_regiao_intermediaria TO codigo_regiao_intermediaria_ibge;
ALTER TABLE db_msterritorializacao.tb_municipio RENAME COLUMN no_regiao_intermediaria TO nome_regiao_intermediaria_ibge;
ALTER TABLE db_msterritorializacao.tb_municipio RENAME COLUMN geom TO geometria_municipio;
ALTER TABLE db_msterritorializacao.tb_municipio RENAME COLUMN no_fonte_geom TO origem_geometria_municipio;
ALTER TABLE db_msterritorializacao.tb_municipio RENAME COLUMN dt_carga TO data_carga_pipeline_etl_municipio;

-- Índices
ALTER INDEX db_msterritorializacao.ix_tb_municipio_co_uf RENAME TO ix_tb_municipio_codigo_estado_ibge;
ALTER INDEX db_msterritorializacao.ix_tb_municipio_geom  RENAME TO ix_tb_municipio_geometria_municipio;

-- Constraint CHECK (o nome ainda cita a coluna antiga)
ALTER TABLE db_msterritorializacao.tb_municipio RENAME CONSTRAINT ck_tb_municipio_co_uf TO ck_tb_municipio_codigo_estado_ibge;
```

4. Altera db_msterritorializacao.tb_bairro:

```
-- Colunas de tb_bairro
ALTER TABLE db_msterritorializacao.tb_bairro RENAME COLUMN co_bairro TO codigo_bairro_ibge;
ALTER TABLE db_msterritorializacao.tb_bairro RENAME COLUMN no_bairro TO nome_bairro_ibge;
ALTER TABLE db_msterritorializacao.tb_bairro RENAME COLUMN co_municipio TO codigo_municipio_ibge;
ALTER TABLE db_msterritorializacao.tb_bairro RENAME COLUMN co_distrito TO codigo_distrito_ibge;
ALTER TABLE db_msterritorializacao.tb_bairro RENAME COLUMN no_distrito TO nome_distrito_ibge;
ALTER TABLE db_msterritorializacao.tb_bairro RENAME COLUMN co_subdistrito TO codigo_subdistrito_ibge;
ALTER TABLE db_msterritorializacao.tb_bairro RENAME COLUMN no_subdistrito TO nome_subdistrito_ibge;
ALTER TABLE db_msterritorializacao.tb_bairro RENAME COLUMN co_concentracao_urbana TO codigo_concentracao_urbana_ibge;
ALTER TABLE db_msterritorializacao.tb_bairro RENAME COLUMN no_concentracao_urbana TO nome_concentracao_urbana_ibge;
ALTER TABLE db_msterritorializacao.tb_bairro RENAME COLUMN nu_area_km2 TO area_km2_ibge;
ALTER TABLE db_msterritorializacao.tb_bairro RENAME COLUMN geom TO geometria_bairro;
ALTER TABLE db_msterritorializacao.tb_bairro RENAME COLUMN no_fonte_geom TO origem_geometria_bairro;
ALTER TABLE db_msterritorializacao.tb_bairro RENAME COLUMN dt_carga TO data_carga_pipeline_etl_bairro;

-- Índices
ALTER INDEX db_msterritorializacao.ix_tb_bairro_co_municipio RENAME TO ix_tb_bairro_codigo_municipio_ibge;
ALTER INDEX db_msterritorializacao.ix_tb_bairro_geom RENAME TO ix_tb_bairro_geometria_bairro;

-- Constraint CHECK (o nome ainda cita a coluna antiga)
ALTER TABLE db_msterritorializacao.tb_bairro
  RENAME CONSTRAINT ck_tb_bairro_co_municipio TO ck_tb_bairro_codigo_municipio_ibge;

-- FK para tb_municipio, recriada explicitamente
ALTER TABLE db_msterritorializacao.tb_bairro
  DROP CONSTRAINT fk_tb_bairro_tb_municipio;

ALTER TABLE db_msterritorializacao.tb_bairro
  ADD CONSTRAINT fk_tb_bairro_tb_municipio
  FOREIGN KEY (codigo_municipio_ibge)
  REFERENCES db_msterritorializacao.tb_municipio (codigo_municipio_ibge)
  ON UPDATE CASCADE ON DELETE RESTRICT;
```

### Adição de campos `id`, geração de valores UUIDv7 e atualização de PKs / FKs

```

-- =============================================================================
-- Migração 001: chave primária substituta UUIDv7 (id) + chaves estrangeiras por UUID
-- Hierarquia: tb_pais (id) <- tb_estado (id_pais) <- tb_municipio (id_estado) <- tb_bairro (id_municipio)
--
-- Requisitos:
--   * PostgreSQL 18 (uuidv7() nativo; a imagem postgis/postgis:18-3.6 atende)
--   * Colunas já renomeadas (codigo_pais_onu, codigo_estado_ibge, codigo_municipio_ibge, codigo_bairro_ibge)
--   * Nenhum ETL em execução durante a migração
--
-- Tudo roda em UMA transação: se qualquer passo falhar, nada é alterado.
-- Faça um backup antes:  pg_dump -U postgres -d db_msterritorializacao -n db_msterritorializacao -Fc -f backup_pre_uuid.dump
-- =============================================================================

BEGIN;

SET LOCAL lock_timeout = '15s';   -- não fica esperando indefinidamente por locks de outras sessões

-- 0) Falha cedo se uuidv7() não existir (versão do Postgres < 18)
SELECT uuidv7();

-- -----------------------------------------------------------------------------
-- 1) Colunas "id" UUIDv7 (chaves primárias). O DEFAULT uuidv7() também vale para os novos registros.
--    Como uuidv7() é volátil, cada linha existente recebe um UUID distinto.
-- -----------------------------------------------------------------------------
ALTER TABLE db_msterritorializacao.tb_pais      ADD COLUMN id uuid NOT NULL DEFAULT uuidv7();
ALTER TABLE db_msterritorializacao.tb_estado    ADD COLUMN id uuid NOT NULL DEFAULT uuidv7();
ALTER TABLE db_msterritorializacao.tb_municipio ADD COLUMN id uuid NOT NULL DEFAULT uuidv7();
ALTER TABLE db_msterritorializacao.tb_bairro    ADD COLUMN id uuid NOT NULL DEFAULT uuidv7();

-- -----------------------------------------------------------------------------
-- 2) Remove as restrições antigas: primeiro as FKs (de baixo para cima), depois as PKs por código
-- -----------------------------------------------------------------------------
ALTER TABLE db_msterritorializacao.tb_bairro    DROP CONSTRAINT IF EXISTS fk_tb_bairro_tb_municipio;
ALTER TABLE db_msterritorializacao.tb_municipio DROP CONSTRAINT IF EXISTS fk_tb_municipio_tb_estado;
ALTER TABLE db_msterritorializacao.tb_estado    DROP CONSTRAINT IF EXISTS fk_tb_estado_tb_pais;

ALTER TABLE db_msterritorializacao.tb_bairro    DROP CONSTRAINT tb_bairro_pkey;
ALTER TABLE db_msterritorializacao.tb_municipio DROP CONSTRAINT tb_municipio_pkey;
ALTER TABLE db_msterritorializacao.tb_estado    DROP CONSTRAINT tb_estado_pkey;
ALTER TABLE db_msterritorializacao.tb_pais      DROP CONSTRAINT tb_pais_pkey;

-- -----------------------------------------------------------------------------
-- 3) Novas PKs em "id". Os códigos oficiais continuam NOT NULL e UNIQUE (identificam o registro de
--    negócio e sustentam o ON CONFLICT dos ETLs); só deixam de ser a chave primária.
-- -----------------------------------------------------------------------------
ALTER TABLE db_msterritorializacao.tb_pais ADD CONSTRAINT tb_pais_pkey PRIMARY KEY (id);
ALTER TABLE db_msterritorializacao.tb_pais ALTER COLUMN codigo_pais_onu SET NOT NULL;
ALTER TABLE db_msterritorializacao.tb_pais ADD CONSTRAINT uq_tb_pais_codigo_pais_onu UNIQUE (codigo_pais_onu);

ALTER TABLE db_msterritorializacao.tb_estado ADD CONSTRAINT tb_estado_pkey PRIMARY KEY (id);
ALTER TABLE db_msterritorializacao.tb_estado ALTER COLUMN codigo_estado_ibge SET NOT NULL;
ALTER TABLE db_msterritorializacao.tb_estado ADD CONSTRAINT uq_tb_estado_codigo_estado_ibge UNIQUE (codigo_estado_ibge);

ALTER TABLE db_msterritorializacao.tb_municipio ADD CONSTRAINT tb_municipio_pkey PRIMARY KEY (id);
ALTER TABLE db_msterritorializacao.tb_municipio ALTER COLUMN codigo_municipio_ibge SET NOT NULL;
ALTER TABLE db_msterritorializacao.tb_municipio ADD CONSTRAINT uq_tb_municipio_codigo_municipio_ibge UNIQUE (codigo_municipio_ibge);

ALTER TABLE db_msterritorializacao.tb_bairro ADD CONSTRAINT tb_bairro_pkey PRIMARY KEY (id);
ALTER TABLE db_msterritorializacao.tb_bairro ALTER COLUMN codigo_bairro_ibge SET NOT NULL;
ALTER TABLE db_msterritorializacao.tb_bairro ADD CONSTRAINT uq_tb_bairro_codigo_bairro_ibge UNIQUE (codigo_bairro_ibge);

-- -----------------------------------------------------------------------------
-- 4) Colunas de chave estrangeira UUID (sem DEFAULT: um UUID gerado não aponta para pai nenhum)
-- -----------------------------------------------------------------------------
ALTER TABLE db_msterritorializacao.tb_estado    ADD COLUMN id_pais      uuid;
ALTER TABLE db_msterritorializacao.tb_municipio ADD COLUMN id_estado    uuid;
ALTER TABLE db_msterritorializacao.tb_bairro    ADD COLUMN id_municipio uuid;

-- -----------------------------------------------------------------------------
-- 5) Replica os relacionamentos existentes, de cima para baixo na hierarquia
-- -----------------------------------------------------------------------------
UPDATE db_msterritorializacao.tb_estado e
   SET id_pais = p.id
  FROM db_msterritorializacao.tb_pais p
 WHERE p.codigo_pais_onu = e.codigo_pais_onu;

UPDATE db_msterritorializacao.tb_municipio m
   SET id_estado = e.id
  FROM db_msterritorializacao.tb_estado e
 WHERE e.codigo_estado_ibge = m.codigo_estado_ibge;

UPDATE db_msterritorializacao.tb_bairro b
   SET id_municipio = m.id
  FROM db_msterritorializacao.tb_municipio m
 WHERE m.codigo_municipio_ibge = b.codigo_municipio_ibge;

-- -----------------------------------------------------------------------------
-- 6) Validação: se alguma linha ficou sem pai, aborta e desfaz tudo
-- -----------------------------------------------------------------------------
DO $$
DECLARE
    n bigint;
BEGIN
    SELECT count(*) INTO n FROM db_msterritorializacao.tb_estado WHERE id_pais IS NULL;
    IF n > 0 THEN RAISE EXCEPTION 'tb_estado: % linha(s) sem id_pais', n; END IF;

    SELECT count(*) INTO n FROM db_msterritorializacao.tb_municipio WHERE id_estado IS NULL;
    IF n > 0 THEN RAISE EXCEPTION 'tb_municipio: % linha(s) sem id_estado', n; END IF;

    SELECT count(*) INTO n FROM db_msterritorializacao.tb_bairro WHERE id_municipio IS NULL;
    IF n > 0 THEN RAISE EXCEPTION 'tb_bairro: % linha(s) sem id_municipio', n; END IF;
END
$$;

-- -----------------------------------------------------------------------------
-- 7) Novas FKs por UUID + índices nas colunas de FK
-- -----------------------------------------------------------------------------
ALTER TABLE db_msterritorializacao.tb_estado ALTER COLUMN id_pais SET NOT NULL;
ALTER TABLE db_msterritorializacao.tb_estado
    ADD CONSTRAINT fk_tb_estado_tb_pais
    FOREIGN KEY (id_pais) REFERENCES db_msterritorializacao.tb_pais (id)
    ON UPDATE CASCADE ON DELETE RESTRICT;
CREATE INDEX ix_tb_estado_id_pais ON db_msterritorializacao.tb_estado (id_pais);

ALTER TABLE db_msterritorializacao.tb_municipio ALTER COLUMN id_estado SET NOT NULL;
ALTER TABLE db_msterritorializacao.tb_municipio
    ADD CONSTRAINT fk_tb_municipio_tb_estado
    FOREIGN KEY (id_estado) REFERENCES db_msterritorializacao.tb_estado (id)
    ON UPDATE CASCADE ON DELETE RESTRICT;
CREATE INDEX ix_tb_municipio_id_estado ON db_msterritorializacao.tb_municipio (id_estado);

ALTER TABLE db_msterritorializacao.tb_bairro ALTER COLUMN id_municipio SET NOT NULL;
ALTER TABLE db_msterritorializacao.tb_bairro
    ADD CONSTRAINT fk_tb_bairro_tb_municipio
    FOREIGN KEY (id_municipio) REFERENCES db_msterritorializacao.tb_municipio (id)
    ON UPDATE CASCADE ON DELETE RESTRICT;
CREATE INDEX ix_tb_bairro_id_municipio ON db_msterritorializacao.tb_bairro (id_municipio);

COMMIT;

-- =============================================================================
-- Conferências (rode depois do COMMIT)
-- =============================================================================

-- a) PKs, UNIQUEs, FKs e CHECKs de cada tabela
-- SELECT conrelid::regclass AS tabela, conname, contype, pg_get_constraintdef(oid) AS definicao
--   FROM pg_constraint
--  WHERE connamespace = 'db_msterritorializacao'::regnamespace
--  ORDER BY conrelid::regclass::text, contype, conname;

-- b) Os UUIDs são versão 7? (esperado: 7 em todas as linhas)
-- SELECT 'tb_pais' AS tabela, uuid_extract_version(id) AS versao, count(*) FROM db_msterritorializacao.tb_pais GROUP BY 2
-- UNION ALL SELECT 'tb_estado',    uuid_extract_version(id), count(*) FROM db_msterritorializacao.tb_estado    GROUP BY 2
-- UNION ALL SELECT 'tb_municipio', uuid_extract_version(id), count(*) FROM db_msterritorializacao.tb_municipio GROUP BY 2
-- UNION ALL SELECT 'tb_bairro',    uuid_extract_version(id), count(*) FROM db_msterritorializacao.tb_bairro    GROUP BY 2;

-- c) O UUID do pai bate com o código do pai? (esperado: 0 linhas em cada consulta)
-- SELECT count(*) FROM db_msterritorializacao.tb_estado e
--   JOIN db_msterritorializacao.tb_pais p ON p.id = e.id_pais
--  WHERE p.codigo_pais_onu <> e.codigo_pais_onu;
-- SELECT count(*) FROM db_msterritorializacao.tb_municipio m
--   JOIN db_msterritorializacao.tb_estado e ON e.id = m.id_estado
--  WHERE e.codigo_estado_ibge <> m.codigo_estado_ibge;
-- SELECT count(*) FROM db_msterritorializacao.tb_bairro b
--   JOIN db_msterritorializacao.tb_municipio m ON m.id = b.id_municipio
--  WHERE m.codigo_municipio_ibge <> b.codigo_municipio_ibge;

```
