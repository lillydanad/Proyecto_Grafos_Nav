import heapq
import math
import osmnx as ox
def heuristica(G, nodo, destino):
    lat1 = G.nodes[nodo]['y']
    lon1 = G.nodes[nodo]['x']
    lat2 = G.nodes[destino]['y']
    lon2 = G.nodes[destino]['x']
    return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111320
def astar(G, origen, destino):
    heap = [(0, origen)]
    g = {nodo: float('inf') for nodo in G.nodes()}
    g[origen] = 0
    predecesor = {nodo: None for nodo in G.nodes()}
    visitados = set()
    while heap:
        f_actual, nodo_actual = heapq.heappop(heap)

        if nodo_actual in visitados:
            continue

        visitados.add(nodo_actual)

        if nodo_actual == destino:
            break

        for vecino in G.neighbors(nodo_actual):
            peso = G[nodo_actual][vecino][0].get('length', 1)
            g_nuevo = g[nodo_actual] + peso
            if g_nuevo < g[vecino]:
                g[vecino] = g_nuevo

                h = heuristica(G, vecino, destino)
                f = g_nuevo + h

                predecesor[vecino] = nodo_actual
                heapq.heappush(heap, (f, vecino))
    camino = []
    nodo = destino
    while nodo is not None:
        camino.append(nodo)
        nodo = predecesor[nodo]

    camino.reverse()

    if camino[0] != origen:
        return float('inf'), [], set()

    return g[destino], camino, visitados
if __name__ == "__main__":
    print("📍 Cargando el mapa de Miraflores...")
    G_real = ox.load_graphml("data/miraflores.graphml")

    lista_nodos = list(G_real.nodes())
    origen_prueba = lista_nodos[0]
    destino_prueba = lista_nodos[500] 
    
    print(f"Calculando ruta A* desde {origen_prueba} hasta {destino_prueba}...")

    distancia_total, ruta_optima = astar(G_real, origen_prueba, destino_prueba)

    if distancia_total == float('inf'):
        print("No se encontró un camino posible.")
    else:
        print("Ruta encontrada")
        print(f"Distancia total: {distancia_total:.2f} metros")
        print(f"Cantidad de nodos en el camino: {len(ruta_optima)}")#astar.py
