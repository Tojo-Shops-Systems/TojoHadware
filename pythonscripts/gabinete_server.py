from flask import Flask, Response
import serial
import time

app = Flask(__name__)

# ------------------------------------
# CONEXIÓN AL ARDUINO (CORREGIDO)
# ------------------------------------
try:
    arduino = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
    time.sleep(2)                # ← Espera a que Arduino reinicie
    arduino.reset_input_buffer() # ← Limpia "ARDUINO READY"
except serial.SerialException:
    print("ADVERTENCIA: No se pudo conectar al Arduino en /dev/ttyACM0. Se usará modo SIMULACIÓN.")
    arduino = None


# ------------------------------------
# FUNCIÓN PARA ENVIAR COMANDOS
# ------------------------------------
def enviar(cmd):
    if arduino is None:
        # --- Modo simulación ---
        fake = {
            "T": "Temp01: 25.00",
            "H": "Hum01: 60.00",
            "P": "Pir01: 0",
            "G": "Gas01: 100",
            "S": "Serv01: 90",
            "K": "Key01: 1234"
        }
        return fake.get(cmd, "CMD_SIMULADO")

    # Enviar comando real
    arduino.write(cmd.encode())
    time.sleep(0.2)

    if arduino.in_waiting:
        return arduino.readline().decode(errors="ignore").strip()

    return "SIN_RESPUESTA"


# ------------------------------------
# ENDPOINTS INDIVIDUALES
# ------------------------------------

@app.route("/temperatura", methods=["GET"])
def temperatura():
    dato = enviar("T")
    return Response(dato, mimetype="text/plain")


@app.route("/humedad", methods=["GET"])
def humedad():
    dato = enviar("H")
    return Response(dato, mimetype="text/plain")


@app.route("/pir", methods=["GET"])
def pir():
    dato = enviar("P")
    return Response(dato, mimetype="text/plain")


@app.route("/gas", methods=["GET"])
def gas():
    dato = enviar("G")
    return Response(dato, mimetype="text/plain")


@app.route("/servo", methods=["GET"])
def servo_status():
    dato = enviar("S")
    return Response(dato, mimetype="text/plain")


@app.route("/keypad", methods=["GET"])
def keypad():
    dato = enviar("K")
    return Response(dato, mimetype="text/plain")


# ------------------------------------
# CONTROL DE PUERTA (SERVO)
# ------------------------------------

@app.route("/abrir", methods=["GET"])
def abrir_servo():
    dato = enviar("O")
    return Response(dato, mimetype="text/plain")


@app.route("/cerrar", methods=["GET"])
def cerrar_servo():
    dato = enviar("C")
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

    return Response(texto, mimetype="text/plain")


# ------------------------------------
# INICIO API
# ------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
