# python -m main.py

import cv2
import face_recognition
from database import db
import numpy as np
import threading
import queue

TOLERANCIA = 0.50
FRAME_SCALE = 0.25
RECOGNITION_INTERVAL = 30

conn = db.conectar()
cursor = conn.cursor()
cursor.execute("SELECT nome, face_encode FROM funcionario")
db_encodings = cursor.fetchall()
known_names = [name for name, _ in db_encodings]
known_encodings = [enc for _, enc in db_encodings]

frame_queue = queue.Queue(maxsize=1)
result_lock = threading.Lock()

last_face_locations = []
last_face_names = []
last_color = (0, 0, 255)

frame_counter = 0

def process_faces():
    global last_face_locations, last_face_names, last_color, frame_counter
    while True:
        frame = frame_queue.get()
        if frame is None:
            break

        frame_counter += 1

        small_frame = cv2.resize(frame, (0, 0), fx=FRAME_SCALE, fy=FRAME_SCALE)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")

        face_names = []
        color = last_color

        if face_locations and frame_counter % RECOGNITION_INTERVAL == 0:
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            if not known_encodings:
                face_names = ["Desconhecido"] * len(face_locations)
                color = (0, 0, 255)
            elif face_encodings:
                distances = face_recognition.face_distance(known_encodings, face_encodings[0])
                best_match_index = np.argmin(distances)

                if distances[best_match_index] < TOLERANCIA:
                    face_names.append(known_names[best_match_index])
                    color = (0, 255, 0)
                else:
                    face_names.append("Desconhecido")
                    color = (0, 0, 255)
            else:
                face_names = last_face_names
        else:
            face_names = last_face_names


        with result_lock:
            last_face_locations = face_locations
            last_face_names = face_names
            last_color = color

thread = threading.Thread(target=process_faces, daemon=True)
thread.start()

camCapture = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = camCapture.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        if not frame_queue.full():
            frame_queue.put(frame)

        with result_lock:
            for (top, right, bottom, left), name in zip(last_face_locations, last_face_names):

                top = int(top / FRAME_SCALE)
                right = int(right / FRAME_SCALE)
                bottom = int(bottom / FRAME_SCALE)
                left = int(left / FRAME_SCALE)

                cv2.rectangle(frame, (left, top), (right, bottom), last_color, 2)

                frame_height, frame_width = frame.shape[:2]
                if name != "Desconhecido":
                    title_text = "Reconhecido:"
                    name_text = name
                    (title_width, _), _ = cv2.getTextSize(title_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)
                    (name_width, _), _ = cv2.getTextSize(name_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)
                    title_x = (frame_width - title_width) // 2
                    name_x = (frame_width - name_width) // 2
                    title_y = frame_height - 45
                    name_y = frame_height - 20
                    cv2.putText(frame, title_text, (title_x, title_y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, last_color, 2)
                    cv2.putText(frame, name_text, (name_x, name_y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, last_color, 2)
                else:
                    (text_width, _), _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)
                    text_x = (frame_width - text_width) // 2
                    text_y = frame_height - 20
                    cv2.putText(frame, name, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, last_color, 2)

        cv2.imshow("Trabalho de Conclusao de Curso - Reconhecimento Facial", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    frame_queue.put(None)
    camCapture.release()
    cv2.destroyAllWindows()
    cursor.close()
    conn.close()