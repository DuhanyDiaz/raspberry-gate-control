"""
Cliente Ligero Edge IoT para Raspberry Pi
Proyecto: Control de Accesos FIUSAC / EMI
-----------------------------------------------------------
Este script corre exclusivamente en la Raspberry Pi en la puerta física.
No necesita base de datos ni servidores web. Solo consulta a la API en la nube
(Render) cada 1.5 segundos y, al recibir una orden de apertura autorizada,
activa el Pin GPIO 17 por 4 segundos.
"""

import time
import json
import os
import urllib.request
import urllib.error

# Configuración del servidor en la nube (Render) o local
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
POLL_INTERVAL = 1.5 # segundos entre consultas
PIN_CHAPA = 17
TIEMPO_APERTURA = 4

# Detectar hardware GPIO real en la Raspberry Pi
try:
    import RPi.GPIO as GPIO
    HAVE_GPIO = True
except (ImportError, RuntimeError):
    HAVE_GPIO = False


def inicializar_gpio():
    if HAVE_GPIO:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        print("[HARDWARE] Pines GPIO inicializados (Pin BCM 17).")
    else:
        print("[HARDWARE] Modo simulacion (sin modulo RPi.GPIO fisico).")


def activar_chapa():
    print(f"\n[IOT] ORDEN RECIBIDA: Liberando chapa por {TIEMPO_APERTURA} segundos...")
    if HAVE_GPIO:
        try:
            GPIO.setup(PIN_CHAPA, GPIO.OUT)
            GPIO.output(PIN_CHAPA, GPIO.HIGH)
            time.sleep(TIEMPO_APERTURA)
            GPIO.setup(PIN_CHAPA, GPIO.IN)
            print("[IOT] Chapa asegurada nuevamente.")
        except Exception as e:
            print(f"[IOT] Error en GPIO: {e}")
    else:
        time.sleep(TIEMPO_APERTURA)
        print("[IOT] Simulacion completada. Chapa cerrada.")


def consultar_servidor():
    url = f"{API_URL}/api/iot/poll"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "RaspberryPi-GateController/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                contenido = response.read().decode("utf-8")
                datos = json.loads(contenido)
                if datos.get("abrir"):
                    detalles = datos.get("detalles", {})
                    nombre = detalles.get("nombre", "Usuario Autorizado")
                    carne = detalles.get("carne", "")
                    print(f"[ACCESO] Permitido para: {nombre} ({carne})")
                    activar_chapa()
    except urllib.error.URLError:
        pass
    except Exception as e:
        print(f"Error al consultar API: {e}")


def main():
    print("=" * 60)
    print("Control de Acceso EMI - Cliente Edge IoT")
    print(f"Servidor objetivo: {API_URL}")
    print(f"Intervalo de sondeo: {POLL_INTERVAL}s")
    print("=" * 60)

    inicializar_gpio()
    print("Escuchando ordenes de la nube...")

    try:
        while True:
            consultar_servidor()
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\nCliente IoT detenido por el usuario.")
    finally:
        if HAVE_GPIO:
            GPIO.cleanup()


if __name__ == "__main__":
    main()
