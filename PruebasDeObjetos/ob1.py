import cv2

# Inicializar la captura de video desde la cámara
cap = cv2.VideoCapture(0)

while True:
    # Leer el frame actual de la cámara
    ret, frame = cap.read()
    if not ret:
        break

    # Convertir el frame a escala de grises
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Aplicar un desenfoque gaussiano para reducir el ruido
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detectar los bordes utilizando el detector de Canny
    edges = cv2.Canny(blurred, 50, 150)

    # Encontrar los contornos
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Dibujar los contornos en el frame original
    cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)

    # Mostrar el frame con los contornos dibujados
    cv2.imshow('Detección de Objetos', frame)

    # Salir del bucle si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la captura de video y cerrar las ventanas
cap.release()
cv2.destroyAllWindows()
