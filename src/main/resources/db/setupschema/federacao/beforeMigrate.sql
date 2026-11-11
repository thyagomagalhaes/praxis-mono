--- Subquery para criacao dos databases se nao existem

SELECT 'CREATE DATABASE db_msfederacao' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_msfederacao');
SELECT 'CREATE DATABASE db_msfederacao_mock' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_msfederacao_mock');

--
-- Alteracao do timezone
--

ALTER DATABASE db_msfederacao SET timezone TO 'UTC';
ALTER DATABASE db_msfederacao_mock SET timezone TO 'UTC';

-- PostgreSQL 18 provides uuidv7(); PostGIS is supplied by postgis/postgis:18-3.6-alpine.
CREATE EXTENSION IF NOT EXISTS postgis;