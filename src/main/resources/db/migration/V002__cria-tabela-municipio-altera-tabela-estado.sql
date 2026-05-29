--
-- Estrutura da tabela "municipio"
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;



CREATE TABLE municipio (
	id serial NOT NULL,
	nome character varying(120) NOT NULL,
	/* Não vai ser UNIQUE porque todos os MUNICÍPIOS de DF tem o mesmo ibge_municipio */
	ibge_municipio integer,
	estado_id integer NOT NULL,
	lat_lon point,
    latitude double precision,
    longitude double precision,
    cod_tom smallint DEFAULT 0,
	 /* Keys */
	CONSTRAINT municipio_pk PRIMARY KEY (id),
	CONSTRAINT municipio_x_estado_fk FOREIGN KEY (estado_id) REFERENCES estado(id)
);

COMMENT ON COLUMN municipio.cod_tom
  IS 'Código TOM (SEFAZ)';

--
-- Adição de FK em estado referenciando a capital em municipio

ALTER TABLE estado ADD CONSTRAINT estado_x_municipio_fk FOREIGN KEY (capital_id) REFERENCES municipio(id);

--
-- Criando SEQUENCE e vinculando à tabela 
-- -- Para excluir fazemos  DROP SEQUENCE pais_seq CASCADE;

CREATE SEQUENCE municipio_seq  
	START WITH 1 
	INCREMENT BY 1 
	NO MINVALUE 
	NO MAXVALUE 
	CACHE 1;
	
ALTER TABLE municipio ALTER COLUMN id SET DEFAULT NEXTVAL('municipio_seq');

--
-- Criando INDEX das tabelas
--
-- Para excluir fazemos  DROP INDEX pais_nome_idx; 

CREATE INDEX municipio_nome_idx ON municipio(nome);