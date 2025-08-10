import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_NAME = "controle_de_acesso"
DB_USER = "postgres"
DB_PASSWORD = "12345678"
DB_HOST = "localhost"
DB_PORT = "5432"


def criar_bdd():
    # Conexão inicial ao banco postgres padrão
    conn = psycopg2.connect(
        host=DB_HOST,
        database="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    existe = cursor.fetchone()

    if not existe:
        cursor.execute(f"CREATE DATABASE {DB_NAME}")

    cursor.close()
    conn.close()

    # Depois que o banco existe, cria a tabela se não existir
    criar_tabela()


def criar_tabela():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionario (
            cpf CHAR(11) NOT NULL,
            nome VARCHAR(70) NOT NULL,
            foto_path TEXT NOT NULL,
            face_encode double precision[] NOT NULL,
            email VARCHAR(70) NOT NULL,
            celular CHAR(11) NOT NULL,
            PRIMARY KEY (cpf)
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()


def conectar():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
