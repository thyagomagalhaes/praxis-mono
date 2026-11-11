-- ==============================================================================
-- 01_init_etl.sql
-- Script de DDL e ETL Automático com Chaves Primárias e Estrangeiras em UUIDv7
--Abaixo está a solução completa composta pelo docker-compose.yml e o script SQL de DDL e 
--ETL automático (01_init_etl.sql).
--
--Esse script utiliza a extensão PostGIS junto com a extensão http (pgsql-http) para 
--consultar diretamente em linguagem SQL nativa:
--
--Overpass API (OpenStreetMap): Países (admin_level=2), Estados (admin_level=4), 
--Municípios e Bairros do Brasil.
--
--IBGE Localidades API: Subdistritos e Distritos para enriquecer a tabela tb_bairro.
--
--Brasil API: Logradouros por CEP (com preenchimento da FK para a tabela tb_bairro).

--implementa uma função em PL/pgSQL para geração de UUIDv7 (ordenável por timestamp) 
--nativamente no PostgreSQL, reestrutura todas as Chaves Primárias (PK) e Chaves Estrangeiras 
--(FK) para o tipo UUID, e mantém o osm_id como um campo BIGINT UNIQUE para possibilitar os 
--cruzamentos e mapeamentos durante os processos de ETL e atualização do IBGE.

-- ==============================================================================

-- ==============================================================================
-- 01_init_etl.sql
-- Script de DDL e ETL Automático Compatível com pg_tileserv e UUIDv7
-- ==============================================================================

-- 1. EXTENSÕES NECESSÁRIAS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS http;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ==============================================================================
-- 2. GERADOR DE UUIDv7 NATIVO EM PL/PGSQL
-- ==============================================================================
CREATE OR REPLACE FUNCTION generate_uuid_v7()
RETURNS uuid AS $$
DECLARE
    v_time double precision;
    v_epoch_ms bigint;
    v_bytes bytea;
    v_rand_a int;
    v_rand_b bigint;
BEGIN
    v_time := extract(epoch from clock_timestamp());
    v_epoch_ms := (v_time * 1000)::bigint;
    
    v_bytes := decode(lpad(to_hex(v_epoch_ms), 12, '0'), 'hex');
    
    v_rand_a := (random() * 4095)::int;
    v_bytes := v_bytes || decode(lpad(to_hex((0x7000 | v_rand_a)), 4, '0'), 'hex');
    
    v_rand_b := (random() * 4611686018427387903)::bigint;
    v_bytes := v_bytes || decode(lpad(to_hex((0x8000000000000000::bit(64) | v_rand_b::bit(64))::bigint), 16, '0'), 'hex');
    
    RETURN encode(v_bytes, 'hex')::uuid;
END;
$$ LANGUAGE plpgsql VOLATILE;

-- ==============================================================================
-- 3. DDL COM CHAVES UUIDv7 E RESTRICÕES GEOMÉTRICAS COMPATÍVEIS
-- ==============================================================================

-- 3.1. Tabela de Países
CREATE TABLE IF NOT EXISTS tb_pais (
    id UUID PRIMARY KEY DEFAULT generate_uuid_v7(),
    osm_id BIGINT UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    iso_a2 VARCHAR(2),
    iso_a3 VARCHAR(3),
    way GEOMETRY(GeometryCollection, 4326),
    tags JSONB
);

-- 3.2. Tabela de Estados
CREATE TABLE IF NOT EXISTS tb_estado (
    id UUID PRIMARY KEY DEFAULT generate_uuid_v7(),
    osm_id BIGINT UNIQUE NOT NULL,
    id_pais UUID REFERENCES tb_pais(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    state_code VARCHAR(10),
    way GEOMETRY(GeometryCollection, 4326),
    tags JSONB
);

-- 3.3. Tabela de Municípios
CREATE TABLE IF NOT EXISTS tb_municipio (
    id UUID PRIMARY KEY DEFAULT generate_uuid_v7(),
    osm_id BIGINT UNIQUE NOT NULL,
    id_estado UUID REFERENCES tb_estado(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    ibge_code VARCHAR(10),
    way GEOMETRY(GeometryCollection, 4326),
    tags JSONB
);

-- 3.4. Tabela de Bairros
CREATE TABLE IF NOT EXISTS tb_bairro (
    id UUID PRIMARY KEY DEFAULT generate_uuid_v7(),
    osm_id BIGINT UNIQUE NOT NULL,
    id_municipio UUID REFERENCES tb_municipio(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    way GEOMETRY(GeometryCollection, 4326),
    tags JSONB,
    distrito_id BIGINT,
    distrito_nome VARCHAR(255),
    subdistrito_id BIGINT,
    subdistrito_nome VARCHAR(255)
);

-- 3.5. Tabela de Logradouros
CREATE TABLE IF NOT EXISTS tb_logradouro (
    id UUID PRIMARY KEY DEFAULT generate_uuid_v7(),
    cep VARCHAR(8) UNIQUE NOT NULL,
    state VARCHAR(2) NOT NULL,
    city VARCHAR(255) NOT NULL,
    neighborhood VARCHAR(255),
    street VARCHAR(255) NOT NULL,
    service VARCHAR(100),
    location_type VARCHAR(50),
    location_coordinates GEOMETRY(Point, 4326),
    id_bairro UUID REFERENCES tb_bairro(id) ON DELETE SET NULL
);

-- Índices Espaciais (GIST)
CREATE INDEX IF NOT EXISTS idx_tb_pais_way ON tb_pais USING GIST(way);
CREATE INDEX IF NOT EXISTS idx_tb_estado_way ON tb_estado USING GIST(way);
CREATE INDEX IF NOT EXISTS idx_tb_municipio_way ON tb_municipio USING GIST(way);
CREATE INDEX IF NOT EXISTS idx_tb_bairro_way ON tb_bairro USING GIST(way);
CREATE INDEX IF NOT EXISTS idx_tb_logradouro_location ON tb_logradouro USING GIST(location_coordinates);

-- Índices B-Tree para Foreign Keys
CREATE INDEX IF NOT EXISTS idx_tb_estado_pais ON tb_estado(id_pais);
CREATE INDEX IF NOT EXISTS idx_tb_municipio_estado ON tb_municipio(id_estado);
CREATE INDEX IF NOT EXISTS idx_tb_bairro_municipio ON tb_bairro(id_municipio);
CREATE INDEX IF NOT EXISTS idx_tb_logradouro_bairro ON tb_logradouro(id_bairro);

-- Permissões explícitas para garantir visibilidade no pg_tileserv
GRANT USAGE ON SCHEMA public TO CURRENT_USER;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO CURRENT_USER;

-- ==============================================================================
-- 4. PROCESSOS DE ETL COM CAST GEOMÉTRICO
-- ==============================================================================

-- 4.1. ETL Overpass API -> Países
WITH overpass_pais AS (
    SELECT http_post(
        'https://overpass-api.de/api/interpreter',
        '[out:json][timeout:60]; relation["admin_level"="2"]["type"="boundary"]["boundary"="administrative"]; out tags center;',
        'application/x-www-form-urlencoded'
    ) AS res
),
parsed_paises AS (
    SELECT 
        generate_uuid_v7() AS id,
        (elem ->> 'id')::BIGINT AS osm_id,
        COALESCE(elem -> 'tags' ->> 'name:pt', elem -> 'tags' ->> 'name', 'Desconhecido') AS name,
        elem -> 'tags' ->> 'ISO3166-1:alpha2' AS iso_a2,
        elem -> 'tags' ->> 'ISO3166-1:alpha3' AS iso_a3,
        ST_Force2D(ST_Collect(ST_SetSRID(ST_MakePoint((elem -> 'center' ->> 'lon')::float, (elem -> 'center' ->> 'lat')::float), 4326))) AS way,
        elem -> 'tags' AS tags
    FROM overpass_pais,
    LATERAL jsonb_array_elements((res).content::jsonb -> 'elements') AS elem
    WHERE (res).status = 200 AND elem ? 'center'
)
INSERT INTO tb_pais (id, osm_id, name, iso_a2, iso_a3, way, tags)
SELECT id, osm_id, name, iso_a2, iso_a3, way, tags FROM parsed_paises
ON CONFLICT (osm_id) DO NOTHING;

-- 4.2. ETL Overpass API -> Estados
WITH overpass_estado AS (
    SELECT http_post(
        'https://overpass-api.de/api/interpreter',
        '[out:json][timeout:90]; relation["admin_level"="4"]["type"="boundary"]["boundary"="administrative"]; out tags center;',
        'application/x-www-form-urlencoded'
    ) AS res
),
parsed_estados AS (
    SELECT 
        generate_uuid_v7() AS id,
        (elem ->> 'id')::BIGINT AS osm_id,
        COALESCE(elem -> 'tags' ->> 'name:pt', elem -> 'tags' ->> 'name', 'Desconhecido') AS name,
        elem -> 'tags' ->> 'ISO3166-2' AS state_code,
        ST_Force2D(ST_Collect(ST_SetSRID(ST_MakePoint((elem -> 'center' ->> 'lon')::float, (elem -> 'center' ->> 'lat')::float), 4326))) AS way,
        elem -> 'tags' AS tags
    FROM overpass_estado,
    LATERAL jsonb_array_elements((res).content::jsonb -> 'elements') AS elem
    WHERE (res).status = 200 AND elem ? 'center'
)
INSERT INTO tb_estado (id, osm_id, id_pais, name, state_code, way, tags)
SELECT 
    e.id,
    e.osm_id,
    p.id AS id_pais,
    e.name,
    e.state_code,
    e.way,
    e.tags
FROM parsed_estados e
LEFT JOIN tb_pais p ON ST_Contains(p.way, e.way) OR ST_DWithin(p.way, e.way, 1.0)
ON CONFLICT (osm_id) DO NOTHING;

-- 4.3. ETL Overpass API -> Municípios
WITH overpass_muni AS (
    SELECT http_post(
        'https://overpass-api.de/api/interpreter',
        '[out:json][timeout:180]; area["ISO3166-1"="BR"]->.a; (node["place"~"city|town"](area.a); rel["admin_level"="8"]["boundary"="administrative"](area.a);); out tags center;',
        'application/x-www-form-urlencoded'
    ) AS res
),
parsed_muni AS (
    SELECT 
        generate_uuid_v7() AS id,
        (elem ->> 'id')::BIGINT AS osm_id,
        COALESCE(elem -> 'tags' ->> 'name', 'Sem nome') AS name,
        COALESCE(elem -> 'tags' ->> 'IBGE:GEOCODIGO', elem -> 'tags' ->> 'ibge:code') AS ibge_code,
        ST_Force2D(ST_Collect(
            ST_SetSRID(
                ST_MakePoint(
                    COALESCE((elem -> 'center' ->> 'lon')::float, (elem ->> 'lon')::float),
                    COALESCE((elem -> 'center' ->> 'lat')::float, (elem ->> 'lat')::float)
                ), 4326
            )
        )) AS way,
        elem -> 'tags' AS tags
    FROM overpass_muni,
    LATERAL jsonb_array_elements((res).content::jsonb -> 'elements') AS elem
    WHERE (res).status = 200
)
INSERT INTO tb_municipio (id, osm_id, id_estado, name, ibge_code, way, tags)
SELECT 
    m.id,
    m.osm_id,
    e.id AS id_estado,
    m.name,
    m.ibge_code,
    m.way,
    m.tags
FROM parsed_muni m
LEFT JOIN tb_estado e ON ST_Contains(e.way, m.way) OR ST_DWithin(e.way, m.way, 0.5)
ON CONFLICT (osm_id) DO NOTHING;

-- 4.4. ETL Overpass API -> Bairros
WITH overpass_bairro AS (
    SELECT http_post(
        'https://overpass-api.de/api/interpreter',
        '[out:json][timeout:180]; area["ISO3166-1"="BR"]->.a; node["place"~"suburb|neighbourhood"](area.a); out tags center;',
        'application/x-www-form-urlencoded'
    ) AS res
),
parsed_bairro AS (
    SELECT 
        generate_uuid_v7() AS id,
        (elem ->> 'id')::BIGINT AS osm_id,
        COALESCE(elem -> 'tags' ->> 'name', 'Bairro sem nome') AS name,
        ST_Force2D(ST_Collect(ST_SetSRID(ST_MakePoint((elem ->> 'lon')::float, (elem ->> 'lat')::float), 4326))) AS way,
        elem -> 'tags' AS tags
    FROM overpass_bairro,
    LATERAL jsonb_array_elements((res).content::jsonb -> 'elements') AS elem
    WHERE (res).status = 200
)
INSERT INTO tb_bairro (id, osm_id, id_municipio, name, way, tags)
SELECT 
    b.id,
    b.osm_id,
    m.id AS id_municipio,
    b.name,
    b.way,
    b.tags
FROM parsed_bairro b
LEFT JOIN tb_municipio m ON ST_Contains(m.way, b.way) OR ST_DWithin(m.way, b.way, 0.1)
ON CONFLICT (osm_id) DO NOTHING;

-- 4.5. ETL IBGE Localidades API -> Atualiza Distritos/Subdistritos
WITH ibge_subdistritos AS (
    SELECT http_get('https://servicodados.ibge.gov.br/api/v1/localidades/subdistritos') AS res
),
parsed_ibge AS (
    SELECT 
        (elem ->> 'id')::BIGINT AS subdistrito_id,
        elem ->> 'nome' AS subdistrito_nome,
        (elem -> 'distrito' ->> 'id')::BIGINT AS distrito_id,
        elem -> 'distrito' ->> 'nome' AS distrito_nome,
        (elem -> 'distrito' -> 'municipio' ->> 'id')::BIGINT AS ibge_municipio_id,
        LOWER(elem ->> 'nome') AS subdistrito_lower
    FROM ibge_subdistritos,
    LATERAL jsonb_array_elements((res).content::jsonb) AS elem
    WHERE (res).status = 200
)
UPDATE tb_bairro b
SET 
    subdistrito_id = i.subdistrito_id,
    subdistrito_nome = i.subdistrito_nome,
    distrito_id = i.distrito_id,
    distrito_nome = i.distrito_nome
FROM parsed_ibge i
JOIN tb_municipio m ON (
    m.ibge_code = i.ibge_municipio_id::text 
    OR LEFT(m.ibge_code, 7) = LEFT(i.ibge_municipio_id::text, 7)
)
WHERE b.id_municipio = m.id
  AND (
      LOWER(b.name) = i.subdistrito_lower 
      OR i.subdistrito_lower LIKE '%' || LOWER(b.name) || '%'
      OR LOWER(b.name) LIKE '%' || i.subdistrito_lower || '%'
  );

-- 4.6. ETL Brasil API -> Logradouros via CEP
WITH ceps_input (cep_code) AS (
    VALUES ('01001000'), ('50010000'), ('20040002'), ('70040010')
),
brasil_api_res AS (
    SELECT 
        c.cep_code,
        http_get('https://brasilapi.com.br/api/cep/v2/' || c.cep_code) AS res
    FROM ceps_input c
),
parsed_logradouro AS (
    SELECT 
        generate_uuid_v7() AS id,
        (res).content::jsonb ->> 'cep' AS cep,
        (res).content::jsonb ->> 'state' AS state,
        (res).content::jsonb ->> 'city' AS city,
        (res).content::jsonb ->> 'neighborhood' AS neighborhood,
        (res).content::jsonb ->> 'street' AS street,
        (res).content::jsonb ->> 'service' AS service,
        (res).content::jsonb -> 'location' ->> 'type' AS location_type,
        CASE 
            WHEN (res).content::jsonb -> 'location' -> 'coordinates' ->> 'longitude' IS NOT NULL THEN
                ST_SetSRID(
                    ST_MakePoint(
                        ((res).content::jsonb -> 'location' -> 'coordinates' ->> 'longitude')::float,
                        ((res).content::jsonb -> 'location' -> 'coordinates' ->> 'latitude')::float
                    ), 4326
                )
            ELSE NULL
        END AS location_coordinates,
        LOWER((res).content::jsonb ->> 'neighborhood') AS neighborhood_lower
    FROM brasil_api_res
    WHERE (res).status = 200
)
INSERT INTO tb_logradouro (
    id, cep, state, city, neighborhood, street, service, location_type, location_coordinates, id_bairro
)
SELECT 
    l.id,
    l.cep,
    l.state,
    l.city,
    l.neighborhood,
    l.street,
    l.service,
    l.location_type,
    l.location_coordinates,
    b.id AS id_bairro
FROM parsed_logradouro l
LEFT JOIN tb_bairro b ON (
    LOWER(b.name) = l.neighborhood_lower
    OR LOWER(b.name) LIKE '%' || l.neighborhood_lower || '%'
)
ON CONFLICT (cep) DO UPDATE SET
    street = EXCLUDED.street,
    neighborhood = EXCLUDED.neighborhood,
    id_bairro = EXCLUDED.id_bairro;