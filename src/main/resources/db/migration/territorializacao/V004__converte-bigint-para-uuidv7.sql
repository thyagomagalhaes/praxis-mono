-- 1. ADICIONAR COLUNAS TEMPORÁRIAS UUID
ALTER TABLE tb_pais ADD COLUMN new_id UUID;

ALTER TABLE tb_estado ADD COLUMN new_id UUID;
ALTER TABLE tb_estado ADD COLUMN new_id_pais UUID;

ALTER TABLE tb_municipio ADD COLUMN new_id UUID;
ALTER TABLE tb_municipio ADD COLUMN new_id_estado UUID;

ALTER TABLE tb_bairro ADD COLUMN new_id UUID;
ALTER TABLE tb_bairro ADD COLUMN new_id_municipio UUID;


-- 2. GERAR UUIDv7 E REPLICAR RELACIONAMENTOS (Respeitando a Hierarquia)

-- tb_pais: Gera os novos UUIDs primários
UPDATE tb_pais SET new_id = uuidv7();

-- tb_estado: Gera o seu UUID e herda o UUID do respectivo pai
UPDATE tb_estado e 
SET new_id = uuidv7(), 
    new_id_pais = p.new_id
FROM tb_pais p 
WHERE e.id_pais = p.id;

-- tb_municipio: Gera o seu UUID e herda o UUID do respectivo estado
UPDATE tb_municipio m 
SET new_id = uuidv7(), 
    new_id_estado = e.new_id
FROM tb_estado e 
WHERE m.id_estado = e.id;

-- tb_bairro: Gera o seu UUID e herda o UUID do respectivo município
UPDATE tb_bairro b 
SET new_id = uuidv7(), 
    new_id_municipio = m.new_id
FROM tb_municipio m 
WHERE b.id_municipio = m.id;


-- 3. REMOVER RESTRIÇÕES DE INTEGRIDADE ANTIGAS (Substitua os nomes 'fk_...' e 'pk_...' pelos reais do seu banco)
ALTER TABLE tb_bairro DROP CONSTRAINT IF EXISTS fk_bairro_municipio, DROP CONSTRAINT IF EXISTS tb_bairro_pkey;
ALTER TABLE tb_municipio DROP CONSTRAINT IF EXISTS fk_municipio_estado, DROP CONSTRAINT IF EXISTS tb_municipio_pkey;
ALTER TABLE tb_estado DROP CONSTRAINT IF EXISTS fk_estado_pais, DROP CONSTRAINT IF EXISTS tb_estado_pkey;
ALTER TABLE tb_pais DROP CONSTRAINT IF EXISTS tb_pais_pkey;


-- 4. REMOVER COLUNAS BIGINT ANTIGAS
ALTER TABLE tb_bairro DROP COLUMN id, DROP COLUMN id_municipio;
ALTER TABLE tb_municipio DROP COLUMN id, DROP COLUMN id_estado;
ALTER TABLE tb_estado DROP COLUMN id, DROP COLUMN id_pais;
ALTER TABLE tb_pais DROP COLUMN id;


-- 5. RENOMEAR AS NOVAS COLUNAS PARA O PADRÃO ORIGINAL
ALTER TABLE tb_pais RENAME COLUMN new_id TO id;

ALTER TABLE tb_estado RENAME COLUMN new_id TO id;
ALTER TABLE tb_estado RENAME COLUMN new_id_pais TO id_pais;

ALTER TABLE tb_municipio RENAME COLUMN new_id TO id;
ALTER TABLE tb_municipio RENAME COLUMN new_id_estado TO id_estado;

ALTER TABLE tb_bairro RENAME COLUMN new_id TO id;
ALTER TABLE tb_bairro RENAME COLUMN new_id_municipio TO id_municipio;


-- 6. APLICAR RESTRIÇÕES DE NOT NULL E CHAVES PRIMÁRIAS
ALTER TABLE tb_pais ALTER COLUMN id SET NOT NULL, ADD PRIMARY KEY (id);

ALTER TABLE tb_estado ALTER COLUMN id SET NOT NULL, ALTER COLUMN id_pais SET NOT NULL, ADD PRIMARY KEY (id);

ALTER TABLE tb_municipio ALTER COLUMN id SET NOT NULL, ALTER COLUMN id_estado SET NOT NULL, ADD PRIMARY KEY (id);

ALTER TABLE tb_bairro ALTER COLUMN id SET NOT NULL, ALTER COLUMN id_municipio SET NOT NULL, ADD PRIMARY KEY (id);


-- 7. REAPLICAR AS CHAVES ESTRANGEIRAS (FOREIGN KEYS) E DEFINIR DEFAULT UUIDv7 PARA OS NOVOS REGISTROS
ALTER TABLE tb_pais ALTER COLUMN id SET DEFAULT uuidv7();

ALTER TABLE tb_estado ALTER COLUMN id SET DEFAULT uuidv7();
ALTER TABLE tb_estado ADD CONSTRAINT fk_estado_pais FOREIGN KEY (id_pais) REFERENCES tb_pais(id) ON DELETE CASCADE;

ALTER TABLE tb_municipio ALTER COLUMN id SET DEFAULT uuidv7();
ALTER TABLE tb_municipio ADD CONSTRAINT fk_municipio_estado FOREIGN KEY (id_estado) REFERENCES tb_estado(id) ON DELETE CASCADE;

ALTER TABLE tb_bairro ALTER COLUMN id SET DEFAULT uuidv7();
ALTER TABLE tb_bairro ADD CONSTRAINT fk_bairro_municipio FOREIGN KEY (id_municipio) REFERENCES tb_municipio(id) ON DELETE CASCADE;