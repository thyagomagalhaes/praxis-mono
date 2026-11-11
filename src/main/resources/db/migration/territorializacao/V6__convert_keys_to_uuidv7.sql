-- Função geradora de UUIDv7 (compatível com PostgreSQL < 17)
CREATE OR REPLACE FUNCTION generate_uuid_v7() RETURNS uuid AS $$
DECLARE
    unix_time_ms bytea;
    rand_bytes bytea;
BEGIN
    unix_time_ms := substring(int8send((extract(epoch from clock_timestamp()) * 1000)::bigint) from 3 for 6);
    rand_bytes := gen_random_bytes(10);
    rand_bytes := overlay(rand_bytes placing set_bit(get_bit(substring(rand_bytes from 1 for 1), 7), 7, 0) from 1 for 1);
    rand_bytes := overlay(rand_bytes placing set_bit(substring(rand_bytes from 1 for 1), 6, 1) from 1 for 1);
    
    RETURN encode(unix_time_ms || rand_bytes, 'hex')::uuid;
END;
$$ LANGUAGE plpgsql;

-- Remoção de FKs para alteração dos tipos de coluna
ALTER TABLE tb_estado DROP CONSTRAINT IF EXISTS tb_estado_id_pais_fkey;
ALTER TABLE tb_municipio DROP CONSTRAINT IF EXISTS tb_municipio_id_estado_fkey;
ALTER TABLE tb_bairro DROP CONSTRAINT IF EXISTS tb_bairro_id_municipio_fkey;
ALTER TABLE tb_logradouro DROP CONSTRAINT IF EXISTS tb_logradouro_id_bairro_fkey;

-- Adição das colunas temporárias UUIDv7
ALTER TABLE tb_pais ADD COLUMN new_id UUID DEFAULT generate_uuid_v7();
ALTER TABLE tb_estado ADD COLUMN new_id UUID DEFAULT generate_uuid_v7(), ADD COLUMN new_id_pais UUID;
ALTER TABLE tb_municipio ADD COLUMN new_id UUID DEFAULT generate_uuid_v7(), ADD COLUMN new_id_estado UUID;
ALTER TABLE tb_bairro ADD COLUMN new_id UUID DEFAULT generate_uuid_v7(), ADD COLUMN new_id_municipio UUID;
ALTER TABLE tb_logradouro ADD COLUMN new_id UUID DEFAULT generate_uuid_v7(), ADD COLUMN new_id_bairro UUID;

-- Atualização de relacionamentos nas colunas UUIDv7
UPDATE tb_estado e SET new_id_pais = p.new_id FROM tb_pais p WHERE e.id_pais = p.id;
UPDATE tb_municipio m SET new_id_estado = e.new_id FROM tb_estado e WHERE m.id_estado = e.id;
UPDATE tb_bairro b SET new_id_municipio = m.new_id FROM tb_municipio m WHERE b.id_municipio = m.id;
UPDATE tb_logradouro l SET new_id_bairro = b.new_id FROM tb_bairro b WHERE l.id_bairro = b.id;

-- Reestruturação de PKs e FKs para o formato UUIDv7
ALTER TABLE tb_pais DROP CONSTRAINT tb_pais_pkey CASCADE, DROP COLUMN id, RENAME COLUMN new_id TO id;
ALTER TABLE tb_pais ADD PRIMARY KEY (id);

ALTER TABLE tb_estado DROP CONSTRAINT tb_estado_pkey CASCADE, DROP COLUMN id, DROP COLUMN id_pais, RENAME COLUMN new_id TO id, RENAME COLUMN new_id_pais TO id_pais;
ALTER TABLE tb_estado ADD PRIMARY KEY (id), ADD CONSTRAINT tb_estado_id_pais_fkey FOREIGN KEY (id_pais) REFERENCES tb_pais(id);

ALTER TABLE tb_municipio DROP CONSTRAINT tb_municipio_pkey CASCADE, DROP COLUMN id, DROP COLUMN id_estado, RENAME COLUMN new_id TO id, RENAME COLUMN new_id_estado TO id_estado;
ALTER TABLE tb_municipio ADD PRIMARY KEY (id), ADD CONSTRAINT tb_municipio_id_estado_fkey FOREIGN KEY (id_estado) REFERENCES tb_estado(id);

ALTER TABLE tb_bairro DROP CONSTRAINT tb_bairro_pkey CASCADE, DROP COLUMN id, DROP COLUMN id_municipio, RENAME COLUMN new_id TO id, RENAME COLUMN new_id_municipio TO id_municipio;
ALTER TABLE tb_bairro ADD PRIMARY KEY (id), ADD CONSTRAINT tb_bairro_id_municipio_fkey FOREIGN KEY (id_municipio) REFERENCES tb_municipio(id);

ALTER TABLE tb_logradouro DROP CONSTRAINT tb_logradouro_pkey CASCADE, DROP COLUMN id, DROP COLUMN id_bairro, RENAME COLUMN new_id TO id, RENAME COLUMN new_id_bairro TO id_bairro;
ALTER TABLE tb_logradouro ADD PRIMARY KEY (id), ADD CONSTRAINT tb_logradouro_id_bairro_fkey FOREIGN KEY (id_bairro) REFERENCES tb_bairro(id);