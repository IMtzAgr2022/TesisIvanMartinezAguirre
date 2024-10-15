import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox
import time

# Inicializar la captura de video desde la cámara
cap = cv2.VideoCapture(0)

# Establecer el factor de conversión de píxeles a centímetros
pixels_per_cm = 20  # Cambia este valor según la calibración

# Variables del tamaño del cuadro en centímetros
width_cm = 34.5
height_cm = 32.5

# Variables del tamaño del cuadro en píxeles
width_pixels = int(width_cm * pixels_per_cm)
height_pixels = int(height_cm * pixels_per_cm)

# Función para ajustar el zoom de manera suave
def zoom_image(frame, zoom_factor):
    height, width = frame.shape[:2]
    center_x, center_y = width // 2, height // 2
    zoom_width, zoom_height = int(width / zoom_factor), int(height / zoom_factor)
    x1 = max(center_x - zoom_width // 2, 0)
    y1 = max(center_y - zoom_height // 2, 0)
    x2 = min(center_x + zoom_width // 2, width)
    y2 = min(center_y + zoom_height // 2, height)
    cropped = frame[y1:y2, x1:x2]
    zoomed = cv2.resize(cropped, (width, height))
    return zoomed

# Modificar la función measure_object
def measure_object(frame, contours):
    detected_square = False  # Inicializa la variable de detección del cuadro

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        # Dibuja un rectángulo alrededor del objeto detectado
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Medir dimensiones
        width_cm_measured = w / pixels_per_cm
        height_cm_measured = h / pixels_per_cm
        
        # Mostrar dimensiones medidas
        cv2.putText(frame, f"Ancho: {width_cm_measured:.2f} cm", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        cv2.putText(frame, f"Alto: {height_cm_measured:.2f} cm", (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Comprobar si el objeto coincide con el tamaño deseado
        if abs(width_cm_measured - width_cm) < 1 and abs(height_cm_measured - height_cm) < 1:
            cv2.putText(frame, "Cuadro Detectado", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            detected_square = True  # Se detectó el cuadro
        else:
            cv2.putText(frame, "Cuadro No Detectado", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Imprimir las medidas en consola
        print(f"Ancho: {width_cm_measured:.2f} cm, Alto: {height_cm_measured:.2f} cm")

    return detected_square  # Devuelve el estado de detección del cuadro

# Función para crear una ventana de confirmación con tkinter
def show_confirmation_window():
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal
    result = messagebox.askyesno("Confirmación", "¿Está bien colocado el objeto y listo para medir?")
    root.destroy()
    return result

def nothing(x):
    pass

# Crear una ventana de OpenCV
cv2.namedWindow('Contornos en tiempo real')

# Crear un deslizador para ajustar el zoom
cv2.createTrackbar('Zoom', 'Contornos en tiempo real', 1, 50, nothing)

# Variables para controlar la calibración y el temporizador
last_zoom_factor = 1
calibrating = True
last_update_time = time.time()
update_interval = 20  # Intervalo de actualización en segundos

# Bandera para controlar la detección del disco duro
disk_detected = False

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Obtener el valor del deslizador (zoom)
    zoom_factor = cv2.getTrackbarPos('Zoom', 'Contornos en tiempo real')
    zoom_factor = max(1, zoom_factor)  # Asegurarse de que el zoom factor sea al menos 1
    
    # Aplicar zoom a la imagen
    frame_zoomed = zoom_image(frame, zoom_factor)

    # Mostrar el frame con el zoom aplicado
    cv2.imshow('Contornos en tiempo real', frame_zoomed)

    if calibrating:
        # Mostrar la ventana de confirmación si el zoom ha cambiado
        if zoom_factor != last_zoom_factor:
            last_zoom_factor = zoom_factor
            if show_confirmation_window():
                calibrating = False
                print("Objeto calibrado y listo para medir.")
    else:
        # Convertir el frame a escala de grises
        gray = cv2.cvtColor(frame_zoomed, cv2.COLOR_BGR2GRAY)

        # Aplicar un desenfoque gaussiano para reducir el ruido
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Detectar los bordes utilizando Canny
        edges = cv2.Canny(blurred, 50, 150)

        # Encontrar los contornos
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Mostrar los contornos en el frame
        cv2.drawContours(frame_zoomed, contours, -1, (0, 255, 0), 2)

        # Mostrar el zoom actual en el frame
        cv2.putText(frame_zoomed, f"Zoom: {zoom_factor}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Actualizar las medidas cada 20 segundos
        current_time = time.time()
        if current_time - last_update_time >= update_interval:
            # Medir el objeto y actualizar el estado de detección
            detected_square = measure_object(frame_zoomed, contours)
            last_update_time = current_time
            
            # Iniciar la detección del disco duro si el cuadro fue detectado
            if detected_square and not disk_detected:
                print("Iniciando la detección del disco duro...")
                disk_detected = True  # Cambia a la detección del disco duro

        # Mostrar el frame actualizado
        cv2.imshow('Contornos en tiempo real', frame_zoomed)

    # Salir del bucle si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la captura de video y cerrar las ventanas
cap.release()
cv2.destroyAllWindows()
