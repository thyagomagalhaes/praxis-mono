--- Subquery para criacao dos databases se nao existem

SELECT 'CREATE DATABASE db_msterritorializacao' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_msterritorializacao');
SELECT 'CREATE DATABASE db_msterritorializacao_mock' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_msterritorializacao_mock');

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS http;

--
-- Alteracao do timezone
--

ALTER DATABASE db_msterritorializacao SET timezone TO 'UTC';
ALTER DATABASE db_msterritorializacao_mock SET timezone TO 'UTC';