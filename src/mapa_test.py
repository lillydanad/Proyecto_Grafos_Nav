import osmnx as ox
import matplotlib.pyplot as plt

# Descargamos el grafo de un distrito pequeño para la demo del Hito 1
lugar = "Miraflores, Lima, Peru"
print(f"Descargando el mapa de {lugar}...")

# network_type="drive" filtra solo las calles por donde pasan autos
grafo = ox.graph_from_place(lugar, network_type="drive") 

# Dibujamos el grafo en pantalla
ox.plot_graph(grafo)