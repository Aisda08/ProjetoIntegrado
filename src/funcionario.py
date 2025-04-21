import face_recognition

import psycopg2
from psycopg2 import sql

# Configurações da conexão com o banco de dados
db_config = {
    "host": "localhost",
    "database": "projeto_integrado",
    "user": "postgres",
    "password": "12345678",
    "port": "5432"
}

# Conecta ao banco de dados.
conn = psycopg2.connect(**db_config)
cursor = conn.cursor()


cpf = input("CPF: ")
nome = input("Nome: ")
foto = ""
encode = face_recognition.face_encodings(foto)

# Inserir dados no banco de dados.
sql = """
    INSERT INTO funcionarios (cpf, nome, foto, face_encoding)
    VALUES (%s, %s, %s, %s)
"""
valores = (cpf, nome, foto, encode)

cursor.execute(sql, valores)
conn.commit()

# Libera recursos no final.
cursor.close()
conn.close()