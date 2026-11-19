-- Subqueries para criacao dos databases se nao existem
SELECT 'CREATE DATABASE db_msterritorializacao' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_msterritorializacao');
SELECT 'CREATE DATABASE db_msterritorializacao_mock' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_msterritorializacao_mock');

-- Habilita extensão espacial (caso utilize mapas)

-- PostGIS adiciona suporte a dados geográficos ao PostgreSQL: pontos, linhas e polígonos, cálculos de distância e área, 
-- consultas espaciais e sistemas de coordenadas. É útil para mapas, endereços e análise de localização.

-- HTTP permite fazer requisições HTTP diretamente do banco, por exemplo, chamar uma API a partir de uma consulta ou função 
-- SQL. Isso pode ser prático para integrações, mas exige cuidado com permissões, segurança e dependência de serviços 
-- externos.

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS http;

--
-- Alteracao do timezone
--
ALTER DATABASE db_msterritorializacao SET timezone TO 'UTC';
ALTER DATABASE db_msterritorializacao_mock SET timezone TO 'UTC';