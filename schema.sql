CREATE TABLE IF NOT EXISTS clientes (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 nome TEXT NOT NULL CHECK(length(trim(nome)) BETWEEN 1 AND 100),
 email TEXT NOT NULL CHECK(length(email) BETWEEN 1 AND 150),
 telefone TEXT NOT NULL CHECK(length(trim(telefone)) BETWEEN 1 AND 30)
);
CREATE TABLE IF NOT EXISTS tecnicos (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 nome TEXT NOT NULL CHECK(length(trim(nome)) BETWEEN 1 AND 100),
 email TEXT NOT NULL CHECK(length(email) BETWEEN 1 AND 150),
 especialidade TEXT NOT NULL CHECK(length(trim(especialidade)) BETWEEN 1 AND 100)
);
CREATE TABLE IF NOT EXISTS chamados (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE RESTRICT,
 tecnico_id INTEGER NOT NULL REFERENCES tecnicos(id) ON DELETE RESTRICT,
 titulo TEXT NOT NULL CHECK(length(trim(titulo)) BETWEEN 1 AND 150),
 descricao TEXT NOT NULL CHECK(length(trim(descricao)) BETWEEN 1 AND 3000),
 status TEXT NOT NULL DEFAULT 'Aberto' CHECK(status IN ('Aberto','Em andamento','Concluído')),
 criado_em TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now')),
 atualizado_em TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now'))
);
CREATE INDEX IF NOT EXISTS idx_chamados_cliente ON chamados(cliente_id);
CREATE INDEX IF NOT EXISTS idx_chamados_tecnico_status ON chamados(tecnico_id,status);
