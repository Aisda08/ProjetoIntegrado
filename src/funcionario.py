import cv2
import face_recognition
import os
from datetime import datetime
import psycopg2
from psycopg2 import sql

def getPhoto():
    camCapture = cv2.VideoCapture(0)
    print("Pressione 's' para salvar a foto")

    while True:
        _, frame = camCapture.read()
        frame = cv2.flip(frame, 1)
        cv2.imshow("Captura", frame)

        key = cv2.waitKey(1) # Espera por 1ms para uma tecla ser pressionada.
        if key == ord('s'):
            break

    camCapture.release()
    cv2.destroyAllWindows()

    nome_arquivo = f"{nome.replace(' ', '_')}_{timestamp}.jpg"
    caminho_imagem = os.path.join("img", "funcionario", nome_arquivo)
    cv2.imwrite(caminho_imagem, frame)

    return frame


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
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")


cpf = input("CPF: ")
nome = input("Nome: ")
foto = getPhoto()
encode = face_recognition.face_encodings(foto)[0] # ***************

# Inserir dados no banco de dados.
sql = """
    INSERT INTO funcionario (cpf, nome, foto_path, face_encode, data_cadastro)
    VALUES (%s, %s, %s, %s, %s)
"""

cursor.execute(sql, (cpf, nome, foto, encode, timestamp))
conn.commit()

# Libera recursos no final.
cursor.close()
conn.close()