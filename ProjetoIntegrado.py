import cv2

cap = cv2.VideoCapture(0) # Acessa a câmera.

while True:
    _, img = cap.read() # Captura um frame da câmera.
    title = "Projeto Integrado - Reconhecimento Facial"
    cv2.imshow(title, img) # Exibe o frame.

    key = cv2.waitKey(1) # Espera por 1ms para uma tecla ser pressionada.
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()