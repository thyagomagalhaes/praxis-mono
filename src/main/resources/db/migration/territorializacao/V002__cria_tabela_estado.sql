--
-- Estrutura da tabela "db_msterritorializacao.tb_estado"
--

CREATE TABLE db_msterritorializacao.tb_estado (
	id uuid DEFAULT uuidv7() NOT NULL,
	id_pais uuid NOT NULL,
	codigo_estado_ibge int2 NOT NULL,
	sigla_estado bpchar(2) NOT NULL,
	nome_estado text NOT NULL,
	codigo_pais_onu int2 DEFAULT 76 NOT NULL,
	codigo_regiao_ibge int2 NOT NULL,
	sigla_regiao varchar(2) NULL,
	nome_regiao text NOT NULL,
	geometria_estado public.geometry(multipolygon, 4326) NULL,
	origem_geometria_estado text NULL,
	data_carga_pipeline_etl_estado timestamptz DEFAULT now() NOT NULL,
	 /* Keys */
	CONSTRAINT tb_estado_co_pais_m49_not_null NOT NULL codigo_pais_onu,
	CONSTRAINT tb_estado_co_regiao_not_null NOT NULL codigo_regiao_ibge,
	CONSTRAINT tb_estado_co_uf_not_null NOT NULL codigo_estado_ibge,
	CONSTRAINT tb_estado_dt_carga_not_null NOT NULL data_carga_pipeline_etl_estado,
	CONSTRAINT tb_estado_id_not_null NOT NULL id,
	CONSTRAINT tb_estado_id_pais_not_null NOT NULL id_pais,
	CONSTRAINT tb_estado_no_estado_not_null NOT NULL nome_estado,
	CONSTRAINT tb_estado_no_regiao_not_null NOT NULL nome_regiao,
	CONSTRAINT tb_estado_pkey PRIMARY KEY (id),
	CONSTRAINT tb_estado_sg_uf_not_null NOT NULL sigla_estado,
	CONSTRAINT uq_tb_estado_codigo_estado_ibge UNIQUE (codigo_estado_ibge),
	CONSTRAINT uq_tb_estado_sigla_estado UNIQUE (sigla_estado),
	CONSTRAINT fk_tb_estado_tb_pais FOREIGN KEY (id_pais) REFERENCES db_msterritorializacao.tb_pais(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

COMMENT ON TABLE db_msterritorializacao.tb_estado
  IS 'Estados';


--
-- Criando INDEX da tabela
-- 

CREATE INDEX ix_tb_estado_codigo_pais_onu ON db_msterritorializacao.tb_estado USING btree (codigo_pais_onu);
CREATE INDEX ix_tb_estado_codigo_regiao_ibge ON db_msterritorializacao.tb_estado USING btree (codigo_regiao_ibge);
CREATE INDEX ix_tb_estado_geometria_estado ON db_msterritorializacao.tb_estado USING gist (geometria_estado);
CREATE INDEX ix_tb_estado_id_pais ON db_msterritorializacao.tb_estado USING btree (id_pais);

