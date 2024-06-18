import time
import numpy as np
import cv2
from gpiozero import Motor, DistanceSensor
from picamera.array import PiRGBArray
from picamera import PiCamera

# Configuración de la cámara y sensores
camera = PiCamera()
camera.resolution = (640, 480)
raw_capture = PiRGBArray(camera, size=(640, 480))
sensor_distance = DistanceSensor(echo=18, trigger=17) # Pines GPIO para el sensor de distancia
motor_left = Motor(forward=4, backward=14)
motor_right = Motor(forward=17, backward=18)

# Funciones de control básico
def avanzar():
    motor_left.forward()
    motor_right.forward()

def retroceder():
    motor_left.backward()
    motor_right.backward()

def detener():
    motor_left.stop()
    motor_right.stop()

def girar_izquierda():
    motor_left.backward()
    motor_right.forward()

def girar_derecha():
    motor_left.forward()
    motor_right.backward()

# Detectar color (rojo y verde)
def detectar_color(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Rango de colores en HSV para rojo
    rojo_bajo = np.array([0, 120, 70])
    rojo_alto = np.array([10, 255, 255])
    
    # Rango de colores en HSV para verde
    verde_bajo = np.array([36, 25, 25])
    verde_alto = np.array([86, 255, 255])
    
    mask_rojo = cv2.inRange(hsv, rojo_bajo, rojo_alto)
    mask_verde = cv2.inRange(hsv, verde_bajo, verde_alto)
    
    if np.sum(mask_rojo) > np.sum(mask_verde):
        return 'rojo'
    elif np.sum(mask_verde) > 0:
        return 'verde'
    else:
        return 'ninguno'

# Función para esquivar obstáculos
def esquivar(color):
    if color == 'rojo':
        girar_derecha()
        time.sleep(1)  # Ajusta el tiempo necesario para girar
    elif color == 'verde':
        girar_izquierda()
        time.sleep(1)
    avanzar()

# Función principal del coche
def main():
    start_time = time.time()
    vueltas = 0

    while vueltas < 3:
        for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
            image = frame.array
            raw_capture.truncate(0)
            
            # Detección de obstáculos
            distance = sensor_distance.distance * 100  # Convertir a cm
            if distance < 20:
                detener()
                color = detectar_color(image)
                esquivar(color)
            else:
                avanzar()
            
            # Comprobar si ha pasado un tiempo suficiente para contar una vuelta
            if time.time() - start_time > 30:  # Asumiendo que 30 segundos es una vuelta
                vueltas += 1
                start_time = time.time()
                print(f"Vuelta {vueltas} completada")
            
            if vueltas >= 3:
                detener()
                print("Punto de partida alcanzado")
                break
            
            time.sleep(0.1)  # Reducir la carga del CPU

    print("Completado")

if __name__ == "__main__":
    main()