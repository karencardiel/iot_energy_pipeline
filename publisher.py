import paho.mqtt.client as mqtt
import pandas as pd
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

# Variables del .env
broker = os.getenv('MQTT_BROKER')
user = os.getenv('MQTT_USER')
pw = os.getenv('MQTT_PASS')
port = int(os.getenv('MQTT_PORT', 1883))

# Configuracion del cliente
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(user, pw)

try:
    print(f"Conectando al broker en {broker}...")
    client.connect(broker, port, 60)
    
    # Cargar datos
    df = pd.read_csv('energydata_complete.csv')
    print(f"CSV cargado con {len(df)} registros. Iniciando envío...")

    for i, row in df.iterrows():
        payload = row.to_dict()
        client.publish("casa/energia", json.dumps(payload))
        
        # Imprimimos cada 100 para no saturar la terminal
        if i % 100 == 0:
            print(f"Progreso: {i}/{len(df)} enviados...")
        
        # Velocidad de ráfaga: 0.01 segundos (100 msgs/seg)
        time.sleep(0.01) 

    print("¡Envío completado exitosamente!")

except Exception as e:
    print(f"Error en el Publisher: {e}")