--
-- Estrutura da tabela "pais"
--

CREATE TABLE pais (
  id       serial NOT NULL,
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
-- Estrutura da tabela "estado"
--

CREATE TABLE estado (
	id serial NOT NULL,
	nome varchar(80) NOT NULL,
	uf   char(2) NOT NULL,
    ibge_estado integer UNIQUE,
    regiao varchar(20) NOT NULL,
    ddd JSON,
    pais_id integer NOT NULL,
	capital_id integer NOT NULL,
    /* Keys */
	CONSTRAINT estado_pk PRIMARY KEY (id),
	CONSTRAINT estado_x_pais_fk FOREIGN KEY (pais_id) REFERENCES pais(id)
);

COMMENT ON TABLE estado
  IS 'Unidades Federativas';


--
-- Criando SEQUENCE e vinculando à tabela 
-- -- Para excluir fazemos  DROP SEQUENCE pais_seq CASCADE;

CREATE SEQUENCE pais_seq;
ALTER TABLE pais ALTER COLUMN id SET DEFAULT NEXTVAL('pais_seq');

CREATE SEQUENCE estado_seq;
ALTER TABLE estado ALTER COLUMN id SET DEFAULT NEXTVAL('estado_seq');
-- ALTER SEQUENCE estado_seq RESTART 99;

--
-- Criando INDEX das tabelas
--
-- Para excluir fazemos  DROP INDEX pais_nome_idx; 

CREATE INDEX pais_nome_idx ON pais(nome);

CREATE INDEX estado_nome_idx ON estado(nome);



