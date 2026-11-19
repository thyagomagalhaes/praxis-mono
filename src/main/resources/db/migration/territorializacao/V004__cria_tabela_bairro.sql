--
-- Estrutura da tabela "db_msterritorializacao.tb_bairro"
--

CREATE TABLE db_msterritorializacao.tb_bairro (
	id uuid DEFAULT uuidv7() NOT NULL,
	id_municipio uuid NOT NULL,
	codigo_bairro_ibge int8 NOT NULL,
	nome_bairro_ibge text NOT NULL,
	codigo_municipio_ibge int4 NOT NULL,
	codigo_distrito_ibge int8 NULL,
	nome_distrito_ibge text NULL,
	codigo_subdistrito_ibge int8 NULL,
	nome_subdistrito_ibge text NULL,
	codigo_concentracao_urbana_ibge text NULL,
	nome_concentracao_urbana_ibge text NULL,
	area_km2_ibge numeric(14, 4) NULL,
	geometria_bairro public.geometry(multipolygon, 4326) NULL,
	origem_geometria_bairro text NULL,
	data_carga_pipeline_etl_bairro timestamptz DEFAULT now() NOT NULL,
	/* Keys */
	CONSTRAINT ck_tb_bairro_codigo_municipio_ibge CHECK (((codigo_bairro_ibge / 1000) = codigo_municipio_ibge)),
	CONSTRAINT tb_bairro_co_bairro_not_null NOT NULL codigo_bairro_ibge,
	CONSTRAINT tb_bairro_co_municipio_not_null NOT NULL codigo_municipio_ibge,
	CONSTRAINT tb_bairro_dt_carga_not_null NOT NULL data_carga_pipeline_etl_bairro,
	CONSTRAINT tb_bairro_id_municipio_not_null NOT NULL id_municipio,
	CONSTRAINT tb_bairro_id_not_null NOT NULL id,
	CONSTRAINT tb_bairro_no_bairro_not_null NOT NULL nome_bairro_ibge,
	CONSTRAINT tb_bairro_pkey PRIMARY KEY (id),
	CONSTRAINT uq_tb_bairro_codigo_bairro_ibge UNIQUE (codigo_bairro_ibge),
	CONSTRAINT fk_tb_bairro_tb_municipio FOREIGN KEY (id_municipio) REFERENCES db_msterritorializacao.tb_municipio(id) ON DELETE RESTRICT ON UPDATE CASCADE
);


COMMENT ON TABLE db_msterritorializacao.tb_bairro
  IS 'Bairros do Brasil';

--
-- Criando INDEX da tabela
-- 

CREATE INDEX ix_tb_bairro_codigo_municipio_ibge ON db_msterritorializacao.tb_bairro USING btree (codigo_municipio_ibge);
CREATE INDEX ix_tb_bairro_geometria_bairro ON db_msterritorializacao.tb_bairro USING gist (geometria_bairro);
CREATE INDEX ix_tb_bairro_id_municipio ON db_msterritorializacao.tb_bairro USING btree (id_municipio);


