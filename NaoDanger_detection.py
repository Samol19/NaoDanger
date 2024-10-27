# -*- coding: utf-8 -*-
#librerias
import time
import cv2 
from naoqi import ALProxy
import vision_definitions 
from PIL import Image 
import numpy as np 
import sys, os 
import requests
import sys
import threading

# Verificar que los argumentos fueron pasados correctamente
if len(sys.argv) != 3:
    print("Uso: python response_detection.py <ip> <port>")
    sys.exit(1)


NAOIP = "127.0.0.1"
NAOPORT = 23123

# Obtener valores de IP y Puerto de los argumentos
NAOIP = sys.argv[1]
NAOPORT = int(sys.argv[2])  # Asegúrate de convertir a entero

#Example
#audio_file_path = "X:\\JOSHUA\\UPC\\7 Ciclo\\Machine Learning\\NAO\\ta3\\entrega\\alarma.ogg"
ruta_actual = os.getcwd()  # Obtiene el directorio actual donde se está ejecutando el script
#audio_danger = os.path.join(ruta_actual, 'alarma.ogg')

audio_danger = "D:\\Descargas\\NaoDangerExeModificado\\alarma.ogg"


camProxy = ALProxy("ALVideoDevice", NAOIP,NAOPORT) 
motion_proxy = ALProxy("ALMotion", NAOIP, NAOPORT)
posture_proxy = ALProxy("ALRobotPosture", NAOIP, NAOPORT)
speech_proxy = ALProxy("ALTextToSpeech", NAOIP, NAOPORT)
audio_proxy = ALProxy("ALAudioPlayer", NAOIP, NAOPORT)
behavior_manager = ALProxy("ALBehaviorManager", NAOIP, NAOPORT)
postures = posture_proxy.getPostureList()


cameraIndex = 0 
resolution = vision_definitions.kVGA # 
colorSpace = vision_definitions.kRGBColorSpace 
resolution = 2 # 
colorSpace =3
last_pose = "na"
# Variable compartida para el estado de la respuesta de YOLO
danger_response = 0
response_lock = threading.Lock()

#cv2.namedWindow("preview") 
vc = cv2.VideoCapture(1) 
#vc=cv2.VideoCapture('faces.mp4') 
behavior_name = "audio"
print(camProxy.getExpectedImageParameters(0)) 
print(postures)
#behavior_name = "C:\\Users\\USUARIO\\Documents\\audio\\behavior_1\\xar"

motion_proxy.wakeUp()
speech_proxy.say("Listo para escanear posibles peligros")


# if vc.isOpened(): # try to get the first frame rval, 
#  frame = vc.read() 
# else: 
#  rval = False 
# while vc.isOpened(): 
#  rval, frame = vc.read() 
#  frame=cv2.resize(frame, (640, 480)) 
#  #cv2.imshow("preview", frame) # 
#  key = cv2.waitKey(1) 
#  time.sleep(0.15) 
#  b,g,r = cv2.split(frame) # get b,g,r 
#  rgb_img = cv2.merge([r,g,b]) # switch it to rgb 
#  set=camProxy.putImage(0,640,480,rgb_img.tobytes()) 
#  #print(set) 
#  #if key == 27: 
#  # exit on ESC 
#  #break


def t_pose():
    try:
        # Definir los nombres de las articulaciones que se van a mover
        arm_names = ["LShoulderPitch", "RShoulderPitch", "LShoulderRoll", "RShoulderRoll"]
        head_names = ["HeadYaw"]  # Solo mover la cabeza

        # Definir los ángulos en radianes para la T-Pose (solo brazos)
        arm_angles = [0.0, 0.0, 0.5, -0.5]  # Brazos extendidos horizontalmente
        arm_angles_def = [0.0, 0.0, 0.0,0.0]  # Brazos extendidos horizontalmente defecto

        fractionMaxSpeed = 0.3

        # Establecer los ángulos de los brazos
        motion_proxy.setAngles(arm_names, arm_angles, fractionMaxSpeed)
        time.sleep(1)  # Esperar a que se complete el movimiento de los brazos

        # Movimiento de la cabeza de izquierda a derecha
        for angle in [-0.5, 0.5]:  # Movimientos hacia la izquierda y derecha
            motion_proxy.setAngles(head_names, [angle], fractionMaxSpeed)
            time.sleep(1)  # Esperar un segundo en cada posición

        # Volver la cabeza a la posición neutra
        motion_proxy.setAngles(head_names, [0.0], fractionMaxSpeed)
        time.sleep(1)  # Esperar un segundo en la posición neutra

        # Establecer los ángulos de los brazos
        motion_proxy.setAngles(arm_names, arm_angles_def, fractionMaxSpeed)
        time.sleep(1)  # Esperar a que se complete el movimiento de los brazos


    except Exception as e:
        print("Error al ejecutar la T-Pose con movimiento de cabeza:", e)

def play_audio():
    audio_proxy.post.playFile(audio_danger)
    # # Asegúrate de que el nombre del archivo sea 
    # if behavior_manager.isBehaviorInstalled(behavior_name):
    #     print("El comportamiento está disponible")

    #     # Ejecutar el comportamiento
    #     if not behavior_manager.isBehaviorRunning(behavior_name):
    #         print("Iniciando el comportamiento...")
    #         behavior_manager.startBehavior(behavior_name)
    #         time.sleep(15)
    #         print("El comportamiento ha terminado.")
    #         # Detener el comportamiento
    #         behavior_manager.stopBehavior(behavior_name)
    #     else:
    #         print("El comportamiento ya está en ejecución")
    # else:
    #     print("El comportamiento no está instalado en el robot")



def yolo_response_thread():
    global danger_response
    while True:
        # Llamar a la función yoloResponse en el hilo
        current_response = yoloResponse()
        with response_lock:
            danger_response = current_response

def yoloResponse():
    # Aquí reemplaza la URL con la URL real de tu backend
    global last_pose  # Declarar last_pose como global
    url = "http://localhost:5000/pose-detected"  

    try:
        # Realizar una solicitud GET para obtener el estado de la pose detectada
        response = requests.get(url)
        
        if response.status_code == 200:
            # Procesar la respuesta que ahora debería contener {"pose_detected": valor}
            response_data = response.json()
            pose_detected = response_data.get("timestamp")
            pose_detected_1 = response_data.get("pose_detected")
            if pose_detected != last_pose and (pose_detected_1 == 1 or pose_detected_1 == 2):
                last_pose=pose_detected
                return 1
            else:
                return 0

        else:
            print("Error en la solicitud a la API. Código de estado:", response.status_code)
            return 0   
    except Exception as e:
        print("Error al conectar con la API:", e)
        return 0
    

def main():

    global danger_response  # Usar la variable global
    # Crear y empezar el hilo de yoloResponse
    yolo_thread = threading.Thread(target=yolo_response_thread)
    yolo_thread.daemon = True  # Hacer el hilo un hilo daemon
    yolo_thread.start()


    while True:
        try:
            if danger_response == 1:
                print("PELIGRO! PELIGRO! PELIGRO!")
                speech_proxy.say("POSIBLE PELIGRO, llamando a las autoridades")
                audio_thread = threading.Thread(target=play_audio)
                audio_thread.start()  # Iniciar el hilo de audio
                # Ejecutar la postura T-Pose en el hilo principal
                t_pose()

            elif danger_response == 2:
                print("PELIGRO! PELIGRO! PELIGRO!")
                speech_proxy.say("PELIGRO! CUCHILLO DETECTADO!")
                audio_thread = threading.Thread(target=play_audio)
                audio_thread.start()
                t_pose()

            elif danger_response ==0:
                print("Todo normal...")

            # Mostrar el video en una ventana (opcional)
            # cv2.imshow("preview", frame) 

            # Salir del bucle si se presiona 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.05)  # Controlar la velocidad del bucle
        except Exception as e:
            print("Error:", e)



if __name__ == "__main__":
    main()