# database.py
"""
Módulo de acesso ao banco de dados SQLite para o app de finanças pessoais.
"""

# Adaptado para MySQL
import mysql.connector

# Configure aqui as credenciais do seu banco MySQL
MYSQL_CONFIG = {
    'user': 'root',         # Altere para seu usuário
    'password': 'Bolsonaro222022',   # Altere para sua senha
    'host': 'localhost',
    'raise_on_warnings': True
}

def create_database_if_not_exists():
    conn = mysql.connector.connect(
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password'],
        host=MYSQL_CONFIG['host']
    )
    cur = conn.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS financas DEFAULT CHARACTER SET utf8mb4;")
    cur.close()
    conn.close()

def get_connection():
    config = MYSQL_CONFIG.copy()
    config['database'] = 'financas'
    return mysql.connector.connect(**config)

def init_db():
    create_database_if_not_exists()
    conn = get_connection()
    cur = conn.cursor()
    # Criação de tabelas com tratamento de erro para evitar crash se já existirem
    tabelas = [
        # Usuários
        ('''CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario VARCHAR(100) UNIQUE NOT NULL,
            senha VARCHAR(100) NOT NULL,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;'''),
        # Categorias
        ('''CREATE TABLE IF NOT EXISTS categorias (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(50) NOT NULL,
            tipo VARCHAR(20) NOT NULL
        ) ENGINE=InnoDB;'''),
        # Objetivos/Sonhos
        ('''CREATE TABLE IF NOT EXISTS objetivos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT,
            nome VARCHAR(100) NOT NULL,
            valor_meta DECIMAL(12,2) NOT NULL,
            valor_atual DECIMAL(12,2) DEFAULT 0,
            prazo DATE,
            prioridade INT DEFAULT 1,
            descricao TEXT,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        ) ENGINE=InnoDB;'''),
        # Configurações do usuário
        ('''CREATE TABLE IF NOT EXISTS configuracoes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT,
            chave VARCHAR(50) NOT NULL,
            valor TEXT,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        ) ENGINE=InnoDB;'''),
        # Orçamento mensal
        ('''CREATE TABLE IF NOT EXISTS orcamento (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT,
            categoria_id INT,
            mes_ano VARCHAR(7) NOT NULL, -- formato AAAA-MM
            valor_planejado DECIMAL(10,2) NOT NULL,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY(categoria_id) REFERENCES categorias(id)
        ) ENGINE=InnoDB;'''),
        # Lançamentos (gastos/investimentos/receitas)
        ('''CREATE TABLE IF NOT EXISTS lancamentos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tipo VARCHAR(20) NOT NULL,
            categoria_id INT NOT NULL,
            valor DECIMAL(10,2) NOT NULL,
            data DATE NOT NULL,
            descricao TEXT,
            forma_pagamento VARCHAR(30),
            status VARCHAR(20),
            recorrente BOOLEAN DEFAULT FALSE,
            objetivo_id INT,
            anexo VARCHAR(255),
            usuario_id INT,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY(categoria_id) REFERENCES categorias(id),
            FOREIGN KEY(objetivo_id) REFERENCES objetivos(id)
        ) ENGINE=InnoDB;'''),
        # Notificações
        ('''CREATE TABLE IF NOT EXISTS notificacoes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT,
            mensagem TEXT NOT NULL,
            lida BOOLEAN DEFAULT FALSE,
            data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        ) ENGINE=InnoDB;'''),
        # Histórico de login
        ('''CREATE TABLE IF NOT EXISTS historico_login (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT,
            data_login DATETIME DEFAULT CURRENT_TIMESTAMP,
            sucesso BOOLEAN,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        ) ENGINE=InnoDB;''')
    ]
    for sql in tabelas:
        try:
            cur.execute(sql)
        except Exception:
            pass  # Ignora erro se tabela já existe
    conn.commit()
    cur.close()
    conn.close()

# Funções utilitárias para manipulação dos dados
def inserir_categoria(nome, tipo):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO categorias (nome, tipo) VALUES (%s, %s)", (nome, tipo))
    conn.commit()
    cur.close()
    conn.close()

def inserir_usuario(usuario, senha):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO usuarios (usuario, senha) VALUES (%s, %s)", (usuario, senha))
    conn.commit()
    cur.close()
    conn.close()


def inserir_lancamento(tipo, categoria_id, valor, data, descricao, forma_pagamento, status, recorrente, objetivo_id, anexo, usuario_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO lancamentos (tipo, categoria_id, valor, data, descricao, forma_pagamento, status, recorrente, objetivo_id, anexo, usuario_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (tipo, categoria_id, valor, data, descricao, forma_pagamento, status, recorrente, objetivo_id, anexo, usuario_id))
    conn.commit()
    cur.close()
    conn.close()

def inserir_objetivo(usuario_id, nome, valor_meta, prazo, prioridade, descricao):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO objetivos (usuario_id, nome, valor_meta, prazo, prioridade, descricao)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (usuario_id, nome, valor_meta, prazo, prioridade, descricao))
    conn.commit()
    cur.close()
    conn.close()

def buscar_objetivos(usuario_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, valor_meta, valor_atual, prazo, prioridade, descricao FROM objetivos WHERE usuario_id=%s", (usuario_id,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

def inserir_orcamento(usuario_id, categoria_id, mes_ano, valor_planejado):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orcamento (usuario_id, categoria_id, mes_ano, valor)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE valor=VALUES(valor)
    """, (usuario_id, categoria_id, mes_ano, valor_planejado))
    conn.commit()
    cur.close()
    conn.close()

def buscar_orcamento(usuario_id, mes_ano=None):
    conn = get_connection()
    cur = conn.cursor()
    if mes_ano:
        cur.execute("SELECT categoria_id, valor FROM orcamento WHERE usuario_id=%s AND mes_ano=%s", (usuario_id, mes_ano))
    else:
        cur.execute("SELECT categoria_id, valor, mes_ano FROM orcamento WHERE usuario_id=%s", (usuario_id,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

def buscar_categorias(tipo=None):
    conn = get_connection()
    cur = conn.cursor()
    if tipo:
        cur.execute("SELECT id, nome FROM categorias WHERE tipo=%s", (tipo,))
    else:
        cur.execute("SELECT id, nome FROM categorias")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

def buscar_lancamentos(usuario_id, tipo=None):
    conn = get_connection()
    cur = conn.cursor()
    if tipo:
        cur.execute("""
            SELECT l.id, l.tipo, c.nome, l.valor, l.data, l.observacao
            FROM lancamentos l JOIN categorias c ON l.categoria_id = c.id
            WHERE l.usuario_id=%s AND l.tipo=%s
            ORDER BY l.data DESC
        """, (usuario_id, tipo))
    else:
        cur.execute("""
            SELECT l.id, l.tipo, c.nome, l.valor, l.data, l.observacao
            FROM lancamentos l JOIN categorias c ON l.categoria_id = c.id
            WHERE l.usuario_id=%s
            ORDER BY l.data DESC
        """, (usuario_id,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

def inserir_notificacao(usuario_id, mensagem):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO notificacoes (usuario_id, mensagem) VALUES (%s, %s)", (usuario_id, mensagem))
    conn.commit()
    cur.close()
    conn.close()

def buscar_notificacoes(usuario_id, apenas_nao_lidas=True):
    conn = get_connection()
    cur = conn.cursor()
    if apenas_nao_lidas:
        cur.execute("SELECT id, mensagem, data_envio FROM notificacoes WHERE usuario_id=%s AND lida=FALSE", (usuario_id,))
    else:
        cur.execute("SELECT id, mensagem, data_envio, lida FROM notificacoes WHERE usuario_id=%s", (usuario_id,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

def marcar_notificacao_lida(notificacao_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE notificacoes SET lida=TRUE WHERE id=%s", (notificacao_id,))
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    init_db()
