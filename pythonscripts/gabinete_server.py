from flask import Flask, Response
import serial
import time
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Cambiar por tu COM real
arduino = serial.Serial("COM4", 9600, timeout=1)


# ------------------------------------
# FUNCIÓN PARA ENVIAR COMANDOS
# ------------------------------------
def enviar(cmd):
    arduino.write(cmd.encode())
    time.sleep(0.2)

    if arduino.in_waiting:
        return arduino.readline().decode(errors="ignore").strip()

    return "SIN_RESPUESTA"


# ------------------------------------
# FUNCIÓN PARA ENVIAR A LARAVEL
# ------------------------------------
def send_to_laravel(data):
    """
    Envía el dato obtenido a los endpoints de Laravel (Local y Cloud).
    """
    laravel_api_url = os.getenv("LARAVEL_API_URL")
    laravel_cloud_url = os.getenv("LARAVEL_CLOUD_URL")
    endpoint_laravel = os.getenv("ENDPOINT_LARAVEL")
    endpoint_laravel_cloud = os.getenv("ENDPOINT_LARAVEL_CLOUD")

    # Validar que existan las variables
    if not all([laravel_api_url, laravel_cloud_url, endpoint_laravel, endpoint_laravel_cloud]):
        print("Faltan variables de entorno para los endpoints de Laravel.")
        return

    url_local = f"{laravel_api_url}{endpoint_laravel}"
    url_cloud = f"{laravel_cloud_url}{endpoint_laravel_cloud}"

    # Payload - Asumiendo que se envía como JSON con la clave 'data'
    # Ajustar según lo que espere el backend de Laravel
    payload = {"data": data}

    # 1. Enviar a Local
    try:
        print(f"Enviando a Local: {url_local} | Data: {payload}")
        resp_local = requests.post(url_local, json=payload, timeout=2)
        print(f"Respuesta Local: {resp_local.status_code} - {resp_local.text}")
    except Exception as e:
        print(f"Error enviando a Local: {e}")

    # 2. Enviar a Cloud
    try:
        print(f"Enviando a Cloud: {url_cloud} | Data: {payload}")
        resp_cloud = requests.post(url_cloud, json=payload, timeout=2)
        print(f"Respuesta Cloud: {resp_cloud.status_code} - {resp_cloud.text}")
    except Exception as e:
        print(f"Error enviando a Cloud: {e}")


# ------------------------------------
# ENDPOINTS INDIVIDUALES (UN SENSOR)
# ------------------------------------

@app.route("/temperatura", methods=["GET"])
def temperatura():
    dato = enviar("T")  # Arduino ya manda: Temp01: xx.xx
    send_to_laravel(dato)
    return Response(dato, mimetype="text/plain")

@app.route("/humedad", methods=["GET"])
def humedad():
    dato = enviar("H")  # Arduino manda: Hum01: xx.xx
    send_to_laravel(dato)
    return Response(dato, mimetype="text/plain")

@app.route("/pir", methods=["GET"])
def pir():
    dato = enviar("P")  # Arduino manda: Pir01: 0/1
    send_to_laravel(dato)
    return Response(dato, mimetype="text/plain")

@app.route("/gas", methods=["GET"])
def gas():
    dato = enviar("G")  # Arduino manda: Gas01: valor
    send_to_laravel(dato)
    return Response(dato, mimetype="text/plain")

@app.route("/servo", methods=["GET"])
def servo_status():
    dato = enviar("S")  # Arduino manda: Serv01: <angulo>
    send_to_laravel(dato)
    return Response(dato, mimetype="text/plain")

@app.route("/keypad", methods=["GET"])
def keypad():
    dato = enviar("K")  # Arduino manda: Key01: <cadena>
    send_to_laravel(dato)
    return Response(dato, mimetype="text/plain")


# ------------------------------------
# ENDPOINTS PARA CONTROLAR EL SERVO
# ------------------------------------

@app.route("/abrir", methods=["GET"])
def abrir_servo():
    dato = enviar("O")  # Arduino abrirá la puerta
    send_to_laravel(dato)
    return Response(dato, mimetype="text/plain")

@app.route("/cerrar", methods=["GET"])
def cerrar_servo():
    dato = enviar("C")  # Arduino cerrará la puerta
    send_to_laravel(dato)
    return Response(dato, mimetype="text/plain")


# ------------------------------------
# ENDPOINT GENERAL - TODOS LOS SENSORES
# ------------------------------------
@app.route("/sensores", methods=["GET"])
def sensores_todos():
    temp = enviar("T")
    hum  = enviar("H")
    pir  = enviar("P")
    gasV = enviar("G")
    servo = enviar("S")
    keyp  = enviar("K")

    texto = (
        f"{temp}\n"
        f"{hum}\n"
        f"{pir}\n"
        f"{gasV}\n"
        f"{servo}\n"
        f"{keyp}"
    )
    
    # En este caso, enviamos todo el bloque de texto
    send_to_laravel(texto)

    return Response(texto, mimetype="text/plain")


# ------------------------------------
# INICIO API
# ------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)