--- Subquery para criacao dos databases se nao existem

SELECT 'CREATE DATABASE db_msacolhimento' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_msacolhimento');
SELECT 'CREATE DATABASE db_msacolhimento_mock' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_msacolhimento_mock');

--
-- Alteracao do timezone
--

ALTER DATABASE db_msacolhimento SET timezone TO 'UTC';
ALTER DATABASE db_msacolhimento_mock SET timezone TO 'UTC';