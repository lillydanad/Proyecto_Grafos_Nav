import osmnx as ox
from astar import astar 

def main():
    ruta_archivo = "data/miraflores.graphml"
    
    print("Cargando el mapa local de Miraflores...")

    G = ox.load_graphml(ruta_archivo)
    print("¡Mapa cargado al instante!")
    lista_nodos = list(G.nodes())
    origen = lista_nodos[0]
    destino = lista_nodos[500]
    
    print(f"Calculando la ruta más corta con A*...")
    distancia, camino_optimo = astar(G, origen, destino)
    
    if camino_optimo:
        print(f"¡Ruta encontrada! Distancia: {distancia:.2f} metros.")
        print("Dibujando el mapa con la ruta trazada (cierra la ventana para terminar)...")
        
        fig, ax = ox.plot_graph_route(G, camino_optimo, route_color='red', route_linewidth=4, node_size=0)
    else:
        print("No se encontró ningún camino entre esos puntos.")

if __name__ == "__main__":
    main()