import time
import os

PIN_CHAPA = 17
TIEMPO_APERTURA = 4

# Detectar si estamos ejecutando en la Raspberry Pi con pines GPIO disponibles
try:
    import RPi.GPIO as GPIO
    HAVE_GPIO = True
except (ImportError, RuntimeError):
    HAVE_GPIO = False


def abrir_chapa():
    """
    Activa el pin GPIO 17 para energizar el rele y liberar la chapa/cerradura.
    Mantiene el pulso durante TIEMPO_APERTURA segundos y luego libera el pin.
    """
    print(f"[HARDWARE] Liberando chapa por {TIEMPO_APERTURA} segundos...")
    if HAVE_GPIO:
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            # Configurar pin como salida y enviar senal activa
            GPIO.setup(PIN_CHAPA, GPIO.OUT)
            GPIO.output(PIN_CHAPA, GPIO.HIGH)
            time.sleep(TIEMPO_APERTURA)
            # Liberar el pin completamente
            GPIO.setup(PIN_CHAPA, GPIO.IN)
            print("[HARDWARE] Pulso completado, chapa asegurada.")
        except Exception as e:
            print(f"[HARDWARE] Error al controlar GPIO: {e}")
    else:
        # Modo simulacion para entornos sin hardware GPIO (ej. macOS/desarrollo local)
        print("[HARDWARE] Modo simulacion activo (sin RPi.GPIO detectado).")
        time.sleep(TIEMPO_APERTURA)
        print("[HARDWARE] Simulacion completada, chapa cerrada.")
