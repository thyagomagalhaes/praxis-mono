--
-- Estrutura da tabela "pais"
--


CREATE TABLE pais (
  id       smallint NOT NULL,
  nome     varchar(60),
  nome_eng  varchar(60),
  nacionalidade varchar(60),
  sigla     char(2),
  bacen    smallint,
  /* Keys */
  CONSTRAINT pais_pk PRIMARY KEY (id)
);

COMMENT ON TABLE pais
  IS 'Países e Nações';

COMMENT ON COLUMN pais.sigla
  IS 'ISO 3166-1 Alpha2';

--
-- Criando SEQUENCE e vinculando à tabela 
--

CREATE SEQUENCE pais_id_seq;
ALTER TABLE pais ALTER COLUMN id SET DEFAULT NEXTVAL('pais_id_seq');

-- Para excluir fazemos  DROP SEQUENCE pais_id_seq CASCADE;

--
-- Criando INDEX da tabela
--

CREATE INDEX pais_nome_idx ON pais(nome);

-- Para excluir fazemos  DROP INDEX pais_nome_idx; 
