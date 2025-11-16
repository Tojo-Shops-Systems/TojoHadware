#!/usr/bin/env python3
import requests
import time
import sys
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

LARAVEL_BASE_URL = os.getenv("LARAVEL_API_URL")

# RUN THIS CODE WITH C:\Users\jaret\AppData\Local\Programs\Python\Python313\python.exe pythonscripts\gabinete_server.py
class Opening:
    def __init__(self, ticket_id, cashier_id, degrees):
        self.ticket_id = ticket_id
        self.cashier_id = cashier_id
        self.degrees = degrees
        
        self.notification_url = f"{LARAVEL_BASE_URL}/api/cabinet/notify-status/{self.ticket_id}"

    def open_simulated_servo(self):
        try:
            print(f"Flask (Hardware): Simulando... enviando '{self.degrees} GRADOS' para Ticket {self.ticket_id}")
            time.sleep(5)
            print("Flask (Hardware): Simulación completada.")
            return True
        except Exception as e:
            print(f"Flask (Hardware): Error en simulación: {e}")
            return False

    def notify_laravel_of_status(self, success: bool):
        if success:
            status = "opening_realized"
        else:
            status = "opening_failed"
        payload = {'status': status, 'cashier_id': self.cashier_id}
        
        try:
            print(f"Flask (Hardware): Enviando aviso a Laravel: {payload}")
            requests.patch(self.notification_url, json=payload)
            print("Flask (Hardware): Aviso enviado a Laravel (Pi).")
        except Exception as e:
            print(f"Flask (Hardware): No se pudo conectar a la API de aviso de Laravel: {e}")

app = Flask(__name__)

LARAVEL_USER_ENDPOINT = f"{LARAVEL_BASE_URL}/api/user"

@app.route("/api/gabinete/open", methods=["POST"])
def handle_gabinete_opening():
    print("Flask (Hardware): ¡Recibida petición en /api/gabinete/abrir!")
    
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"msg": "Falta el token de autorización"}), 401

    try:
        response = requests.get(
            LARAVEL_USER_ENDPOINT, 
            headers={'Authorization': auth_header, 'Accept': 'application/json'}
        )
        if response.status_code != 200:
            return jsonify({"msg": "Token inválido o expirado"}), 401
        
        user_data = response.json()
        cashier_id = user_data.get('id')
        print(f"Flask (Hardware): Token validado. Cajero ID: {cashier_id}")

    except Exception as e:
        print(f"Flask (Hardware): Error al contactar Laravel para auth: {e}")
        return jsonify({"msg": "Error interno del servidor de hardware"}), 500

    data = request.get_json()
    ticket_id = data.get('ticket_id')
    grados = "90"

    processOpening = Opening(ticket_id, cashier_id, grados)
    exito_apertura = processOpening.open_simulated_servo()
    
    processOpening.notify_laravel_of_status(exito_apertura)

    if exito_apertura:
        return jsonify({"msg": "Gabinete abierto y notificado"}), 200
    else:
        return jsonify({"msg": "Error al abrir el gabinete"}), 500

if __name__ == "__main__":
    print("Iniciando servidor de Hardware (Flask) en http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)