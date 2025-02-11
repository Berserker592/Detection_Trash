from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
import paho.mqtt.client as mqtt
from fastapi.responses import HTMLResponse, FileResponse
from datetime import datetime
import osmnx as ox
import networkx as nx
import folium

app = FastAPI()

# CORS y rutas estáticas
app.mount("/static", StaticFiles(directory="/app/static"), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def get_frontend():
    return FileResponse("/static/index.html")

id_select = "None"
#Simulacion de Dispositivos
#node_simulation.start_sending_data()

# SQLite setup
db_name = "basureros.db"
def init_db():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS basureros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            basurero_id TEXT,
            nivel_ultrasonico INTEGER,
            peso_actual REAL,
            latitud FLOAT,
            longitud FLOAT,
            timestamp TEXT
        )
    """)
    #timestamp DATETIME DEFAULT (DATETIME('now'))
    #timestamp DATETIME DEFAULT CURRENT_TIMESTAMP

    conn.commit()
    conn.close()

init_db()

# MQTT setup
broker = "broker.emqx.io"
port = 1883
username = "emqx121233"
password = "public"
topic = "basureros/datos"

mqtt_client = mqtt.Client()

@app.on_event("startup")
async def startup_event():
    def on_connect(client, userdata, flags, rc):
        print(f"Conectado al Broker MQTT {rc}")
        client.subscribe(topic)

    def on_message(client, userdata, msg):
        try:
            import json
            data = json.loads(msg.payload.decode())
            save_data(
                basurero_id=data["id"],
                nivel_ultrasonico=data["nivel_ultrasonico"],
                peso_actual=data["peso_actual"],
                latitud = data["latitud"],
                longitud = data["longitud"]
            )
            print(f'Datos guardados id: {data["id"]} NU: {data["nivel_ultrasonico"]}  PA: {data["peso_actual"]}')
        except Exception as e:
            print(f"Error: {e}")

    mqtt_client.username_pw_set(username, password)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(broker, port, 60)

    loop = asyncio.get_event_loop()
    loop.create_task(run_mqtt())

async def run_mqtt():
    mqtt_client.loop_start()

@app.on_event("shutdown")
async def shutdown_event():
    mqtt_client.loop_stop()
    mqtt_client.disconnect()

# Save data to SQLite
def save_data(basurero_id, nivel_ultrasonico, peso_actual, latitud, longitud):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        INSERT INTO basureros (basurero_id, nivel_ultrasonico, peso_actual, latitud, longitud, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (basurero_id, nivel_ultrasonico, peso_actual, latitud, longitud, current_time))
    conn.commit()
    conn.close()

# REST API Endpoints
class Basurero(BaseModel):
    basurero_id: str
    nivel_ultrasonico: int
    peso_actual: float

@app.get("/basureros")
def get_basureros():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT basurero_id FROM basureros")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

@app.get("/basureros/{basurero_id}")
def get_basurero_details(basurero_id: str):
    global id_select
    id_select = basurero_id
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nivel_ultrasonico, peso_actual, timestamp
        FROM basureros
        WHERE basurero_id = ?
        ORDER BY timestamp DESC
        LIMIT 10
    """, (basurero_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"nivel_ultrasonico": r[0], "peso_actual": r[1], "timestamp": r[2]} for r in rows]

class LocationRequest(BaseModel):
    latitude: float
    longitude: float

@app.post("/get_location")
async def get_location(location: LocationRequest):
    global id_select
    #print(f'el basurero es: {id_select}')
    #print(f'Si se recibio datos {location}')
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT latitud, longitud FROM basureros WHERE basurero_id = ?
    """, (id_select,))
    basurero = cursor.fetchone()
    conn.close()

#    return {"message": "Ubicación recibida", "latitude": location.latitude, "longitude": location.longitude}
    
    # Cargar el grafo desde un archivo OSM
    file_path = "/app/map.osm"
    G = ox.graph_from_xml(file_path)
    
    # Coordenadas del usuario (origen)

 
    #lat_origen = -1.662635  # Ejemplo de latitud (ubicación actual)
    #lon_origen = -78.674129  # Ejemplo de longitud (ubicación actual)
    
    lat_origen = location.latitude  # Ejemplo de latitud (ubicación actual)
    lon_origen = location.longitude  # Ejemplo de longitud (ubicación actual)
    
    # Encontrar el nodo más cercano al origen (ubicación del usuario)
    origen_node = ox.distance.nearest_nodes(G, X=lon_origen, Y=lat_origen)
    
    # Coordenadas del destino
    lat_destino = basurero[0]  # Ejemplo de latitud (destino)
    lon_destino = basurero[1]  # Ejemplo de longitud (destino)
    
    # Encontrar el nodo más cercano al destino
    destino_node = ox.distance.nearest_nodes(G, X=lon_destino, Y=lat_destino)
    
    # Usar Dijkstra para encontrar la ruta más corta desde el origen hasta el destino
    ruta_optima = nx.dijkstra_path(G, source=origen_node, target=destino_node, weight='length')
    
    # Obtener las coordenadas de los nodos de la ruta
    ruta_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in ruta_optima]
    
    # Crear un mapa centrado en el origen
    m = folium.Map(location=[lat_origen, lon_origen], zoom_start=14)
    
    # Añadir la ruta al mapa (de origen a destino)
    ruta_latitudes = [coord[0] for coord in ruta_coords]
    ruta_longitudes = [coord[1] for coord in ruta_coords]
    
    # Crear una línea de la ruta
    folium.PolyLine(locations=list(zip(ruta_latitudes, ruta_longitudes)), color='blue', weight=5, opacity=0.7).add_to(m)
    
    # Añadir marcadores para el origen y el destino
    folium.Marker([lat_origen, lon_origen], popup='Origen', icon=folium.Icon(color='green')).add_to(m)
    folium.Marker([lat_destino, lon_destino], popup='Destino', icon=folium.Icon(color='red')).add_to(m)
    
    # Añadir una capa de mapa base de Google Maps
    folium.TileLayer('cartodb positron').add_to(m)
    
    # Guardar el mapa como un archivo HTML
    m.save('/app/static/ruta_map.html')

