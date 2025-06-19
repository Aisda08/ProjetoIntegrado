import psycopg2

def conectar():
    db_config = {
        "host": "localhost",
        "database": "projeto_integrado",
        "user": "postgres",
        "password": "12345678",
        "port": "5432"
    }
    
    return psycopg2.connect(**db_config)