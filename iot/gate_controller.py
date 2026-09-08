import time
import paho.mqtt.client as mqtt

# --- MODO SIMULACIÓN ---
from gpiozero.pins.mock import MockFactory
from gpiozero import Device
Device.pin_factory = MockFactory()

from gpiozero import OutputDevice

# Configuramos el Pin 17 de la Raspberry, que irá conectado al Relé
RELE_PIN = 17
puerta_rele = OutputDevice(RELE_PIN)

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TOPIC = "fiusac/puerta/abrir"

def on_connect(client, userdata, flags, reason_code, properties):
    print(f" Conectado al Broker MQTT (Código: {reason_code})")
    client.subscribe(TOPIC)
    print(f" Escuchando órdenes en el canal: {TOPIC}")

def on_message(client, userdata, msg):
    mensaje = msg.payload.decode('utf-8')
    print(f"\n[!] Orden recibida: {mensaje}")
    
    if mensaje == "ABRIR":
        abrir_puerta()

def abrir_puerta():
    print(" Abriendo la cerradura magnética (Mandando 3.3v al Relé)...")
    puerta_rele.on() 
    
    # La mantenemos abierta por 5 segundos para que la persona pase
    time.sleep(5)
    
    print(" Cerrando la puerta (Cortando corriente)...")
    puerta_rele.off() # Corta la corriente

# Configuración del Cliente MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

try:
    print(" Conectando al sistema de mensajería...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    # Loop infinito para que el script nunca se apague y siga escuchando
    client.loop_forever()
except KeyboardInterrupt:
    print("\n Apagando el controlador de la puerta.")
    client.disconnect()
