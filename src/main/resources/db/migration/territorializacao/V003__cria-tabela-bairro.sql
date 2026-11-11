--
-- Estrutura da tabela "bairro"
--


CREATE TABLE bairro (
	id serial NOT NULL,
	nome character varying(120) NOT NULL,
	subdistrito character varying(20) NOT NULL,
	municipio_id integer NOT NULL,	
	 /* Keys */
	CONSTRAINT bairro_pk PRIMARY KEY (id),
	CONSTRAINT bairro_x_municipio_fk FOREIGN KEY (municipio_id) REFERENCES municipio(id)
);

COMMENT ON COLUMN bairro.subdistrito
  IS 'Região Política Administrativa - RPA';
  
--
-- Criando SEQUENCE e vinculando à tabela 
-- -- Para excluir fazemos  DROP SEQUENCE bairro_seq CASCADE;

CREATE SEQUENCE bairro_seq;
ALTER TABLE bairro ALTER COLUMN id SET DEFAULT NEXTVAL('bairro_seq');

--
-- Criando INDEX das tabelas
--
-- Para excluir fazemos  DROP INDEX bairro_nome_idx; 
  
CREATE INDEX bairro_nome_idx ON bairro(nome);