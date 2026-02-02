import paho.mqtt.client as mqtt
import psycopg2
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Credenciales del .env
broker = os.getenv('MQTT_BROKER')
user = os.getenv('MQTT_USER')
password = os.getenv('MQTT_PASS')
port = int(os.getenv('MQTT_PORT', 1883))

# Funcion que se ejecuta al conectar al broker
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Conectado a CloudAMQP exitosamente")
        client.subscribe("casa/energia")
        print("Suscrito al topico: casa/energia")
    else:
        print(f"Error de conexion al broker: {rc}")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        
        conn = psycopg2.connect(
            host=os.getenv('PG_HOST'),
            database='energy_project', 
            user=os.getenv('PG_USER'),
            password=os.getenv('PG_PASSWORD')
        )
        cur = conn.cursor()

        # Tabla 1
        cur.execute(
            "INSERT INTO consumo_energia (date, appliances, lights) VALUES (%s, %s, %s)",
            (data['date'], data['Appliances'], data['lights'])
        )

        # Tabla 2
        cur.execute(
            """INSERT INTO ambiente_interno (date, t1, rh_1, t2, rh_2, t3, rh_3, t4, rh_4, t5, rh_5, t6, rh_6, t7, rh_7, t8, rh_8, t9, rh_9) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (data['date'], data['T1'], data['RH_1'], data['T2'], data['RH_2'], data['T3'], data['RH_3'], 
             data['T4'], data['RH_4'], data['T5'], data['RH_5'], data['T6'], data['RH_6'], 
             data['T7'], data['RH_7'], data['T8'], data['RH_8'], data['T9'], data['RH_9'])
        )

        # Tabla 3
        cur.execute(
            "INSERT INTO clima_externo (date, t_out, press_mm_hg, rh_out, windspeed, visibility, tdewpoint) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (data['date'], data['T_out'], data['Press_mm_hg'], data['RH_out'], data['Windspeed'], data['Visibility'], data['Tdewpoint'])
        )

        conn.commit()
        print(f"Datos de {data['date']} guardados en Postgres")
        
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")

# Configuracion del cliente
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(user, password)
client.on_connect = on_connect
client.on_message = on_message

print(f"Iniciando Subscriber en {broker}...")

try:
    client.connect(broker, port)
    client.loop_forever()
except Exception as e:
    print(f"Error al iniciar: {e}")