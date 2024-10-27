import os
import cv2
import numpy as np
import torch
from ultralytics import YOLO
import requests
from datetime import datetime

# Cargar modelos más ligeros y activar CUDA si está disponible
device = 'cuda' if torch.cuda.is_available() else 'cpu'
pose_model = YOLO('yolov8n-pose.pt').to(device)  # Modelo de pose
object_model = YOLO('yolov8s.pt').to(device)  # Modelo de objetos

# Inicializar captura de video desde la webcam
cap = cv2.VideoCapture(1)  # Cambia el índice a 0 para usar la cámara predeterminada
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Ancho
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Alto

# Verificar si la cámara se abre correctamente
if not cap.isOpened():
    print("Error: No se pudo abrir la cámara.")
    exit()

# Inicializar estado de brazos
LeftArmRaised = False
RightArmRaised = False

# Notificar que no hay detección al iniciar
requests.post('http://localhost:5000/pose-detected', json={"pose_detected": 0, "timestamp": "NA"})

def process_frame(frame):
    global LeftArmRaised, RightArmRaised
    # Detección de objetos
    object_results = object_model(frame)
    object_boxes = object_results[0].boxes

    # Imprimir el número de cuadros detectados
    print(f"Número de cuadros detectados: {len(object_boxes) if object_boxes is not None else 0}")

    if object_boxes is not None:
        for box in object_boxes:
            cls = int(box.cls[0].item())  
            conf = box.conf[0].item() 

            if conf > 0.3: 
                x1, y1, x2, y2 = map(int, box.xyxy[0]) 
                label = f'{object_model.names[cls]}: {conf:.2f}'
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                if cls == 0:  # Si la clase es persona
                    pose_results = pose_model(frame)
                    keypoints = pose_results[0].keypoints

                    if keypoints is not None:
                        points = keypoints.xy[0].tolist() 

                        if len(points) > 10:
                            
                            for i, point in enumerate(points):
                                if len(point) >= 3:  # Verificar que haya al menos 3 elementos en point
                                    x, y, conf = int(point[0]), int(point[1]), point[2]
                                    if conf > 0.5:  
                                        cv2.circle(frame, (x, y), 5, (255, 0, 0), -1)  
                                        if i in [5, 6]:  
                                            cv2.line(frame, (int(points[5][0]), int(points[5][1])),
                                                     (int(points[6][0]), int(points[6][1])),
                                                     (255, 0, 0), 2)

                            # Detectar movimiento de manos
                            LeftArmRaised = points[9][1] < points[0][1] if points[9][1] != 0 else False
                            RightArmRaised = points[10][1] < points[0][1] if points[10][1] != 0 else False

                            # Comprobar condiciones de peligro
                            if LeftArmRaised and RightArmRaised:
                                print("PELIGRO DETECTADO")
                                timestamp = datetime.now().strftime("%H:%M:%S")
                                requests.post('http://localhost:5000/pose-detected', json={"pose_detected": 1, "timestamp": timestamp})

                elif cls == 43:  # Si se detecta un cuchillo
                    if conf > 0.5:
                        print("PELIGRO, CUCHILLO DETECTADO")
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        requests.post('http://localhost:5000/pose-detected', json={"pose_detected": 2, "timestamp": timestamp})


while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: No se pudo leer el frame.")
        break

    process_frame(frame)

    cv2.imshow('Pose and Object Detection', frame)

    # Salir del bucle si se presiona 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la captura de video y cerrar la ventana
cap.release()
cv2.destroyAllWindows()
