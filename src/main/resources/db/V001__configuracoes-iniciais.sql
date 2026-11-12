--- Subquery para criacao dos databases se nao existem

SELECT 'CREATE DATABASE praxissuas' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'praxissuas');
SELECT 'CREATE DATABASE praxissuas_test' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'praxissuas_test');

--
-- Alteracao do timezone
--

ALTER DATABASE praxissuas SET timezone TO 'UTC';
ALTER DATABASE praxissuas_test SET timezone TO 'UTC';
