#!/usr/bin/env python3
import argparse
import requests
import sys
import time

class Opening:
    def __init__(self, ticket_id, cashier_id, degrees):
        self.ticket_id = ticket_id
        self.cashier_id = cashier_id
        self.degrees = degrees

        # --- ¡CAMBIO IMPORTANTE PARA WINDOWS! ---
        # Apunta a tu "php artisan serve"
        self.notification_url = f"http://127.0.0.1:8000/api/cabinet/notify-status/{self.ticket_id}"
        # ----------------------------------------

    def open_simulated_servo(self):
        try:
            print(f"Python (PC): Simulando... enviando '{self.degrees} GRADOS' para Ticket {self.ticket_id}")
            time.sleep(5) # Simula el hardware lento
            print("Python (PC): Simulación completada.")
            return True
        except Exception as e:
            print(f"Python (PC): Error en simulación: {e}")
            return False

    def notify_laravel_of_status(self, success: bool):
        if success:
            status = "opening_initiated"
        else:
            status = "opening_failed"
        payload = {'status': status, 'cashier_id': self.cashier_id}

        try:
            print(f"Python (PC): Enviando aviso a Laravel: {payload}")
            requests.patch(self.notification_url, json=payload)
            print("Python (PC): Aviso enviado a Laravel.")
        except Exception as e:
            print(f"Python (PC): ERROR. No se pudo conectar a {self.notification_url}. ¿Está 'php artisan serve' corriendo?")


# --- Punto de Entrada ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticket", required=True)
    parser.add_argument("--cashier", required=True)
    parser.add_argument("--grados", required=True)
    args = parser.parse_args()

    # 2. Crea la instancia
    processOpening = Opening(args.ticket, args.cashier, args.grados)
    
    # 3. Ejecuta la simulación
    exito_apertura = processOpening.open_simulated_servo()
    
    # 4. ¡Ahora SIEMPRE intentará notificar a Laravel!
    print("Python: Intentando notificar a Laravel...")
    processOpening.notify_laravel_of_status(exito_apertura)

    if exito_apertura:
        sys.exit(0)
    else:
        sys.exit(1)