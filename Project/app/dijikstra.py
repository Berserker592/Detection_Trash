import folium
from geopy.geocoders import Nominatim
from IPython.display import display, HTML

location_name = input("Ingrese la ubicacion: ")
geolocator = Nominatim(user_agent="geoapi")
location = geolocator.geocode(location_name)

if location:
    latitude = location.latitude
    print(latitude)
    longitud = location.longitude
    print(longitud)
    
    clcoding = folium.Map(location=[latitude,longitud],zoom_start=12)
    
    marker = folium.Marker([latitude,longitud],popup=location_name)
    marker.add_to(clcoding)
    
    map_filename = "mapa_ubicacion.html"
    clcoding.save(map_filename)
    
    display(HTML(clcoding._repr_html_()))
else:
    print("Ubicacion no encontrada")
    