# python -m main.py

import cv2
import face_recognition
from database import db

conn = db.conectar()
cursor = conn.cursor()

camCapture = cv2.VideoCapture(0)

try:
    while True:
        _, frame = camCapture.read()
        frame = cv2.flip(frame, 1)

        faces_loc = face_recognition.face_locations(frame)
        if faces_loc: 
            faces_loc = sorted(faces_loc, 
                        key=lambda f: (f[2] - f[0]) * (f[1] - f[3]), 
                        reverse=True)
            faces_loc = [faces_loc[0]]
        
        faces_enc = face_recognition.face_encodings(frame, faces_loc)

        if faces_enc:
            cursor.execute("SELECT nome, face_encode FROM funcionario")
            db_encodings = cursor.fetchall()

            known_encodings = []
            known_names = []
            for name, enc in db_encodings:
                known_names.append(name)
                known_encodings.append(enc)

            matches = face_recognition.compare_faces(known_encodings, faces_enc[0])

            if True in matches:
                match_index = matches.index(True)
                label = f"Reconhecido: {known_names[match_index]}"
                color = (0, 255, 0)  # Verde

                # Processamento do texto centralizado no canto inferior
                frame_height, frame_width = frame.shape[:2]

                # Dividir o texto em duas linhas
                title_text = "Reconhecido:"
                name_text = label.replace("Reconhecido: ", "")

                # Obter tamanhos dos textos
                (title_width, _), _ = cv2.getTextSize(title_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)
                (name_width, name_height), _ = cv2.getTextSize(name_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)

                # Centralizar os textos
                title_x = (frame_width - title_width) // 2
                name_x = (frame_width - name_width) // 2
                title_y = frame_height - 45
                name_y = frame_height - 20

                # Desenhar os textos
                cv2.putText(frame, title_text, (title_x, title_y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                cv2.putText(frame, name_text, (name_x, name_y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            else:
                label = "Desconhecido"
                color = (0, 0, 255)  # Vermelho

                # Caso 'Desconhecido', apenas uma linha
                frame_height, frame_width = frame.shape[:2]
                (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)
                text_x = (frame_width - text_width) // 2
                text_y = frame_height - 20
                cv2.putText(frame, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        # Desenhar os retângulos ao redor dos rostos
        for (top, right, bottom, left), face_encoding in zip(faces_loc, faces_enc):
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)


        title = "Trabalho de Conclusão - Reconhecimento Facial"
        cv2.imshow(title, frame)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

finally:
    camCapture.release()
    cv2.destroyAllWindows()
    cursor.close()
    conn.close()