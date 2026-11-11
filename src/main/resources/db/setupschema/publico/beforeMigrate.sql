--- Subquery para criacao dos databases se nao existem

SELECT 'CREATE DATABASE db_mspublico' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_mspublico');
SELECT 'CREATE DATABASE db_mspublico_mock' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_mspublico_mock');

--
-- Alteracao do timezone
--

ALTER DATABASE db_mspublico SET timezone TO 'UTC';
ALTER DATABASE db_mspublico_mock SET timezone TO 'UTC';