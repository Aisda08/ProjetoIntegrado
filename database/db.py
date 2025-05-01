import psycopg2
from psycopg2 import sql

def conectar():
    # Configurações da conexão com o banco de dados
    db_config = {
        "host": "localhost",
        "database": "projeto_integrado",
        "user": "postgres",
        "password": "12345678",
        "port": "5432"
    }

    # Retorna conecção com o banco de dados.
    return psycopg2.connect(**db_config)