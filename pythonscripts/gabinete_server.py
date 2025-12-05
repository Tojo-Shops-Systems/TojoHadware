from flask import Flask, Response
import serial
import time

app = Flask(__name__)

# Cambiar por tu COM real
# Se usa /dev/ttyACM0 porque parece que el usuario está en Linux/Raspberry ahora o lo cambió manualmente
try:
    arduino = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
except serial.SerialException:
    print("ADVERTENCIA: No se pudo conectar al Arduino en /dev/ttyACM0. Se usará modo SIMULACIÓN.")
    arduino = None


# ------------------------------------
# FUNCIÓN PARA ENVIAR COMANDOS
# ------------------------------------
def enviar(cmd):
    if arduino is None:
        # Modo simulación: devolver valores dummy
        if cmd == "T": return "Temp01: 25.00"
        if cmd == "H": return "Hum01: 60.00"
        if cmd == "P": return "Pir01: 0"
        if cmd == "G": return "Gas01: 100"
        if cmd == "S": return "Serv01: 90"
        if cmd == "K": return "Key01: 1234"
        return "CMD_SIMULADO"

    arduino.write(cmd.encode())
    time.sleep(0.2)

    if arduino.in_waiting:
        return arduino.readline().decode(errors="ignore").strip()

    return "SIN_RESPUESTA"


# ------------------------------------
# ENDPOINTS INDIVIDUALES (UN SENSOR)
# ------------------------------------

@app.route("/temperatura", methods=["GET"])
def temperatura():
    dato = enviar("T")  # Arduino ya manda: Temp01: xx.xx
    return Response(dato, mimetype="text/plain")

@app.route("/humedad", methods=["GET"])
def humedad():
    dato = enviar("H")  # Arduino manda: Hum01: xx.xx
    return Response(dato, mimetype="text/plain")

@app.route("/pir", methods=["GET"])
def pir():
    dato = enviar("P")  # Arduino manda: Pir01: 0/1
    return Response(dato, mimetype="text/plain")

@app.route("/gas", methods=["GET"])
def gas():
    dato = enviar("G")  # Arduino manda: Gas01: valor
    return Response(dato, mimetype="text/plain")

@app.route("/servo", methods=["GET"])
def servo_status():
    dato = enviar("S")  # Arduino manda: Serv01: <angulo>
    return Response(dato, mimetype="text/plain")

@app.route("/keypad", methods=["GET"])
def keypad():
    dato = enviar("K")  # Arduino manda: Key01: <cadena>
    return Response(dato, mimetype="text/plain")


# ------------------------------------
# ENDPOINTS PARA CONTROLAR EL SERVO
# ------------------------------------

@app.route("/abrir", methods=["GET"])
def abrir_servo():
    dato = enviar("O")  # Arduino abrirá la puerta
    return Response(dato, mimetype="text/plain")

@app.route("/cerrar", methods=["GET"])
def cerrar_servo():
    dato = enviar("C")  # Arduino cerrará la puerta
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