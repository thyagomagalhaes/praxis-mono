--- Subquery para criacao dos databases se nao existem

SELECT 'CREATE DATABASE praxis_db_dev' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'praxis_db_dev');
SELECT 'CREATE DATABASE praxis_db_mock' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'praxis_db_mock');

--
-- Alteracao do timezone
--

ALTER DATABASE praxis_db_dev SET timezone TO 'UTC';
ALTER DATABASE praxis_db_mock SET timezone TO 'UTC';