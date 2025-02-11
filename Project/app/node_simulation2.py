import paho.mqtt.client as mqtt
from paho.mqtt import client as mqtt_client
import json
import time
import random
import pandas as pd

# Leer el archivo de Excel con las ubicaciones
ubicaciones_df = pd.read_excel('app/BP.xlsx')
print(ubicaciones_df.head())
# Configuración del broker MQTT
mqtt_broker = "broker.emqx.io"
mqtt_port = 1883
mqtt_username = "emqx121233"
mqtt_password = "public"
topic = "basureros/datos"

# Crear cliente MQTT utilizando la nueva API
client_id = f'python-mqtt-{random.randint(0, 1000)}'
client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)

# Configurar credenciales (si es necesario)
client.username_pw_set(mqtt_username, mqtt_password)

# Conectar al broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado al broker MQTT")
    else:
        print(f"Error al conectar, código de retorno: {rc}")

client.on_connect = on_connect
client.connect(mqtt_broker, mqtt_port, 60)

# Función para enviar los datos
def send_data():
    for i in range(2, 21):  # Desde BP2 hasta BP20
        # Simulando datos de sensores
        nivel_ultrasonico = random.uniform(0, 100)
        peso_actual = random.uniform(0, 20)
        
        # Obtener latitud y longitud para el basurero BP{i}
        latitud = ubicaciones_df.loc[ubicaciones_df['id'] == f'BP{i}', 'latitud'].values[0]
        longitud = ubicaciones_df.loc[ubicaciones_df['id'] == f'BP{i}', 'longitud'].values[0]
        
        # Crear el payload (mensaje JSON)
        payload = {
            "id": f"BP{i}",
            "nivel_ultrasonico": int(nivel_ultrasonico),
            "peso_actual": int(peso_actual),
            "latitud": latitud,
            "longitud": longitud
        }
        
        # Mostrar los datos en consola
        print(f'Datos Enviados id: BP{i} nivel_ultrasonico: {nivel_ultrasonico} peso_actual: {peso_actual} latitud: {latitud} longitud: {longitud}')
    
        # Convertir el diccionario a JSON
        payload_json = json.dumps(payload)
    
        # Publicar los datos en el tópico
        client.publish(topic, payload_json)
        time.sleep(5)  # Esperar 5 segundos antes de enviar el siguiente dato

# Ejecutar el ciclo de envío de datos
try:
    client.loop_start()  # Inicia el loop del cliente MQTT
    while True:
        send_data()
        time.sleep(10)  # Esperar 10 segundos antes de enviar los siguientes datos
except KeyboardInterrupt:
    print("Interrupción manual. Cerrando cliente MQTT.")
finally:
    client.loop_stop()  # Detener el loop del cliente MQTT
    client.disconnect()  # Desconectar del broker
