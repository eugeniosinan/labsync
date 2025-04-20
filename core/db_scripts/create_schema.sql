-- Criar o banco de dados labsync_db, caso não exista
CREATE DATABASE IF NOT EXISTS labsync_db;

-- Conectar ao banco de dados labsync_db (importante para criar o schema e a tabela dentro deste banco)
\c labsync_db;

-- Criar o schema 'labsync' se ele não existir
CREATE SCHEMA IF NOT EXISTS labsync;

-- Criar a tabela de usuários
CREATE TABLE IF NOT EXISTS labsync."users" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL
);

-- Inserir um usuário administrativo de exemplo (certifique-se de alterar a senha)
INSERT INTO labsync."users" (username, password_hash)
VALUES ('admin', '$2b$12$V1c8Zw1FpD.1v.oYc8pMwGhQ7FLs9/eUyVpO2R/tl1zQFeKBtZWw6'); -- Senha: admin123 (criptografada)
