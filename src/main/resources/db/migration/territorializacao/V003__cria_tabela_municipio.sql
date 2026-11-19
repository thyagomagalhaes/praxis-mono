--
-- Estrutura da tabela "db_msterritorializacao.tb_municipio"
--

CREATE TABLE db_msterritorializacao.tb_municipio (
	id uuid DEFAULT uuidv7() NOT NULL,
	id_estado uuid NOT NULL,
	codigo_municipio_ibge int4 NOT NULL,
	nome_municipio_ibge text NOT NULL,
	codigo_estado_ibge int2 NOT NULL,
	codigo_microrregiao_ibge int4 NULL,
	nome_microrregiao_ibge text NULL,
	codigo_mesorregiao_ibge int4 NULL,
	nome_mesorregiao_ibge text NULL,
	codigo_regiao_imediata_ibge int4 NULL,
	nome_regiao_imediata_ibge text NULL,
	codigo_regiao_intermediaria_ibge int4 NULL,
	nome_regiao_intermediaria_ibge text NULL,
	geometria_municipio public.geometry(multipolygon, 4326) NULL,
	origem_geometria_municipio text NULL,
	data_carga_pipeline_etl_municipio timestamptz DEFAULT now() NOT NULL,
	 /* Keys */
	CONSTRAINT ck_tb_municipio_codigo_estado_ibge CHECK (((codigo_municipio_ibge / 100000) = codigo_estado_ibge)),
	CONSTRAINT tb_municipio_co_municipio_not_null NOT NULL codigo_municipio_ibge,
	CONSTRAINT tb_municipio_co_uf_not_null NOT NULL codigo_estado_ibge,
	CONSTRAINT tb_municipio_dt_carga_not_null NOT NULL data_carga_pipeline_etl_municipio,
	CONSTRAINT tb_municipio_id_estado_not_null NOT NULL id_estado,
	CONSTRAINT tb_municipio_id_not_null NOT NULL id,
	CONSTRAINT tb_municipio_no_municipio_not_null NOT NULL nome_municipio_ibge,
	CONSTRAINT tb_municipio_pkey PRIMARY KEY (id),
	CONSTRAINT uq_tb_municipio_codigo_municipio_ibge UNIQUE (codigo_municipio_ibge),
	CONSTRAINT fk_tb_municipio_tb_estado FOREIGN KEY (id_estado) REFERENCES db_msterritorializacao.tb_estado(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

COMMENT ON TABLE db_msterritorializacao.tb_municipio
  IS 'Municípios do Brasil';


--
-- Criando INDEX da tabela
-- 

CREATE INDEX ix_tb_municipio_codigo_estado_ibge ON db_msterritorializacao.tb_municipio USING btree (codigo_estado_ibge);
CREATE INDEX ix_tb_municipio_geometria_municipio ON db_msterritorializacao.tb_municipio USING gist (geometria_municipio);
CREATE INDEX ix_tb_municipio_id_estado ON db_msterritorializacao.tb_municipio USING btree (id_estado);

