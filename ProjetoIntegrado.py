'''
Pacotes a serem instalados antes de rodar o código:
    1. opencv-python
    2. cmake
    3. dlib
    4. face_recognition

Passo a passo para instalar os pacotes:
    1. Pressione Win + R.
    2. Digite CMD e aperte Enter.
    3. Escreva "pip install opencv-python".
    4. Escreva "pip install cmake".
    5. Reinicie o computador.
    6. Repita o passo 1 e 2.
    7. Escreva "pip install dlib".
    4. Escreva "pip install face_recognition".
'''

import cv2
import face_recognition

cap = cv2.VideoCapture(0) # Acessa a câmera.

while True:
    _, img = cap.read() # Captura um frame da câmera.
    img = cv2.flip(img, 1) # Inverte imagem na horizontal.

    grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # Converte img para escalas de cinza.

    if len(faces) > 0: # Se detectar rostos.
        # Ordena os rostos pela área do rosto, do maior para o menor.
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True) 
        (x, y, w, h) = faces[0] # Seleciona apenas o maior rosto na imagem.

        match = None

        label = "Reconhecido" if match else "Desconhecido"
        color = (0, 255, 0) if match else (0, 0, 255) # Blue, Green, Red

        cv2.rectangle(img, (x, y), (x+w, y+h), color, 3) # Desenha um retângulo na tela.
        cv2.putText(img, label, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2) # Escreve label na tela.

    title = "Projeto Integrado - Reconhecimento Facial"
    cv2.imshow(title, img) # Exibe o frame.

    key = cv2.waitKey(1) # Espera por 1ms para uma tecla ser pressionada.
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()