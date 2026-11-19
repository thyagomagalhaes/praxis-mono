--
-- Estrutura da tabela "db_msterritorializacao.tb_pais"
--

CREATE TABLE db_msterritorializacao.tb_pais (
	id uuid DEFAULT uuidv7() NOT NULL,
	codigo_pais_onu int2 NOT NULL,
	sigla_pais_alfa2 bpchar(2) NULL,
	sigla_pais_alfa3 bpchar(3) NULL,
	nome_pais_pt text NOT NULL,
	codigo_regiao_onu int2 NULL,
	nome_regiao_onu text NULL,
	codigo_subregiao_onu int2 NULL,
	nome_subregiao_onu text NULL,
	codigo_regiao_intermediaria_onu int2 NULL,
	nome_regiao_intermediaria_onu text NULL,
	geometria_pais public.geometry(multipolygon, 4326) NULL,
	origem_geometria_pais text NULL,
	data_carga_pipeline_etl_pais timestamptz DEFAULT now() NOT NULL,
	 /* Keys */
	CONSTRAINT tb_pais_co_m49_not_null NOT NULL codigo_pais_onu,
	CONSTRAINT tb_pais_dt_carga_not_null NOT NULL data_carga_pipeline_etl_pais,
	CONSTRAINT tb_pais_id_not_null NOT NULL id,
	CONSTRAINT tb_pais_no_pais_not_null NOT NULL nome_pais_pt,
	CONSTRAINT tb_pais_pkey PRIMARY KEY (id),
	CONSTRAINT uq_tb_pais_codigo_pais_onu UNIQUE (codigo_pais_onu)
);

COMMENT ON TABLE db_msterritorializacao.tb_pais
  IS 'Países e Nações';

COMMENT ON COLUMN sigla_pais_alfa2
  IS 'ISO 3166-1 Alpha2';

COMMENT ON COLUMN sigla_pais_alfa3
  IS 'ISO 3166-1 Alpha3';

--
-- Criando INDEX da tabela
-- 

CREATE INDEX ix_tb_pais_geometria_pais ON db_msterritorializacao.tb_pais USING gist (geometria_pais);
CREATE UNIQUE INDEX ux_tb_pais_sigla_pais_alfa2 ON db_msterritorializacao.tb_pais USING btree (sigla_pais_alfa2) WHERE (sigla_pais_alfa2 IS NOT NULL);



