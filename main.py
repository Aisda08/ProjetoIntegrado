import cv2
import face_recognition
import time

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

camCapture = cv2.VideoCapture(0) # Acessa a câmera.

try:
    while True:
        _, frame = camCapture.read() # lê um frame da câmera.
        frame = cv2.flip(frame, 1) # Inverte imagem na horizontal.

        faces_loc = face_recognition.face_locations(frame) # Detecta os rostos.
        if faces_loc: 
            faces_loc = sorted(faces_loc, 
                        key=lambda f: (f[2] - f[0]) * (f[1] - f[3]), 
                        reverse=True) # Ordena do maior para o menor.
            faces_loc = [faces_loc[0]] # Seleciona apenas o maior rosto na imagem.
        
        faces_enc = face_recognition.face_encodings(frame, faces_loc) # Codifica rosto.

        if faces_enc: # se codificar algum rosto.
            cursor.execute("SELECT nome, face_encode FROM funcionario")
            db_encodings = cursor.fetchall()

            # Converte os encodings do banco para o formato do face_recognition
            known_encodings = []
            known_names = []
            for name, enc in db_encodings:
                known_names.append(name)
                known_encodings.append(enc)

            # Compara com os encodings conhecidos
            matches = face_recognition.compare_faces(known_encodings, faces_enc[0])

            if True in matches:
                    match_index = matches.index(True)
                    label = f"Reconhecido: {known_names[match_index]}"
                    color = (0, 255, 0)
            else:
                label = "Desconhecido"
                color = (0, 0, 255)

            for (top, right, bottom, left), face_encoding in zip(faces_loc, faces_enc):
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2) # Desenha um retângulo ao redor do rosto.
                cv2.putText(frame, label, (left, top - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2) # Escreve label na tela.

        title = "Projeto Integrado - Reconhecimento Facial"
        cv2.imshow(title, frame) # Exibe o frame.

        key = cv2.waitKey(1) # Espera por 1ms para uma tecla ser pressionada.
        if key == ord('q'):
            break

finally: # Libera recursos no final.
    camCapture.release()
    cv2.destroyAllWindows()
    cursor.close()
    conn.close()