-- Cria as tabelas mínimas necessárias para o PDV

-- Tabela de Usuários (Login_Model)
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    login VARCHAR(50) UNIQUE NOT NULL,
    senha CHAR(64) NOT NULL, -- Senha hash SHA-256
    cargo VARCHAR(20) DEFAULT 'Funcionario'
);

-- Tabela de Produtos (Produto_Model)
CREATE TABLE IF NOT EXISTS produto (
    id_produto INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) UNIQUE NOT NULL,
    preco_venda DECIMAL(10, 2) NOT NULL,
    quantidade_estoque INT DEFAULT 0
);

-- Tabela de Caixas (Relatório_Model, Produto_Model)
CREATE TABLE IF NOT EXISTS caixa (
    id_caixa INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario_abertura INT NOT NULL,
    data_abertura DATETIME NOT NULL,
    status ENUM('aberto', 'fechado') DEFAULT 'aberto',
    valor_inicial DECIMAL(10, 2) DEFAULT 0,
    valor_final DECIMAL(10, 2) DEFAULT 0,
    data_fechamento DATETIME,
    total_dinheiro DECIMAL(10, 2) DEFAULT 0,
    total_pix DECIMAL(10, 2) DEFAULT 0,
    total_credito DECIMAL(10, 2) DEFAULT 0,
    total_debito DECIMAL(10, 2) DEFAULT 0,
    FOREIGN KEY (id_usuario_abertura) REFERENCES usuario(id_usuario)
);

-- Tabela de Sangrias (Produto_Model)
CREATE TABLE IF NOT EXISTS sangria (
    id_sangria INT AUTO_INCREMENT PRIMARY KEY,
    id_caixa INT NOT NULL,
    id_usuario INT NOT NULL,
    data_hora DATETIME NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    motivo VARCHAR(255),
    FOREIGN KEY (id_caixa) REFERENCES caixa(id_caixa),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

-- Insira um usuário Administrador inicial (Login: admin, Senha: 123456)
-- O hash SHA-256 da senha '123456' é '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86a6788856994119d80d2ce5'
INSERT INTO usuario (nome, login, senha, cargo) 
VALUES ('Administrador PDV', 'admin', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86a6788856994119d80d2ce5', 'Admin');

-- Garante que o usuário zanatta exista e possa se conectar de qualquer host ('%')
-- Use a senha do seu Login_Model: 'yM&6esW$Lq$#Ahsi!mQVLproig7'

-- 1. Cria ou atualiza o usuário com a senha
-- Depois (Corrigido):
CREATE USER IF NOT EXISTS 'zanatta'@'%' IDENTIFIED WITH mysql_native_password BY 'pdvpassword123';
-- 2. Concede todos os privilégios no banco 'pdv' para o usuário 'zanatta' de qualquer host
GRANT ALL PRIVILEGES ON pdv.* TO 'zanatta'@'%';

-- 3. Aplica as mudanças de privilégio
FLUSH PRIVILEGES;