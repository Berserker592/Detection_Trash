#import paho.mqtt.client as mqtt
from paho.mqtt import client as mqtt_client
import json
import time
import random

# Configuración del broker MQTT
mqtt_broker = "broker.emqx.io"
mqtt_port = 1883
mqtt_username = "emqx121233"
mqtt_password = "public"
topic = "basureros/datos"

# Crear cliente MQTT utilizando la nueva API
#client = mqtt.Client()
client_id = f'python-mqtt-{random.randint(0, 1000)}'
#client = mqtt_client.Client(client_id)
client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)

print("funciona 1")
# Configurar credenciales (si es necesario)
client.username_pw_set(mqtt_username, mqtt_password)
print("funciona 2")

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
    i=2
    while i<=20:
        nivel_ultrasonico = random.uniform(0, 100)  # Simulando un nivel ultrasonico entre 0 y 100
        peso_actual = random.uniform(0, 20)  # Simulando un peso actual entre 0 y 20
        value = int(random.uniform(2,10 ))
        # Crear el payload (mensaje JSON)
        payload = {
            "id": f"BP{i}",
            "nivel_ultrasonico": int(nivel_ultrasonico),
            "peso_actual": int(peso_actual)
        }
        print(f'Datos Enviados id: BP{i} nivel_ultrasonico: {nivel_ultrasonico} peso_actual: {peso_actual}')
    
        # Convertir el diccionario a JSON
        payload_json = json.dumps(payload)
    
        # Publicar los datos en el tópico
        client.publish(topic, payload_json)
        time.sleep(5)
        i+=1
        #print(f"Datos enviados: {payload_json}")


# Ejecutar el ciclo de envío de datos
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