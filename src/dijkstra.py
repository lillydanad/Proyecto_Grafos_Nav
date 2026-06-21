import networkx as nx
import heapq
def dijkstra(G, origen, destino):
    heap = [(0, origen)]

    distancias = {nodo: float('inf') for nodo in G.nodes()}
    distancias[origen] = 0

    predecesor = {nodo: None for nodo in G.nodes()}
    visitados = set()

    while heap:
        dist_actual, nodo_actual = heapq.heappop(heap)

        if nodo_actual in visitados:
            continue
        visitados.add(nodo_actual)

        if nodo_actual == destino:
            break
        for vecino in G.neighbors(nodo_actual):
            peso = G[nodo_actual][vecino].get('length', 1)
            nueva_dist = dist_actual + peso
            if nueva_dist < distancias[vecino]:
                distancias[vecino] = nueva_dist
                predecesor[vecino] = nodo_actual
                heapq.heappush(heap, (nueva_dist, vecino))
    camino = []
    nodo = destino
    while nodo is not None:
        camino.append(nodo)
        nodo = predecesor[nodo]
    camino.reverse()

    if camino[0] != origen:
        return float('inf'), [], set()
    return distancias[destino], camino, visitados

def main():
    G = nx.read_graphml("../data/miraflores.graphml")

    lista_nodos = list(G.nodes())

    nodo_inicio = lista_nodos[0]
    nodo_destino = lista_nodos[500]

    print(f"Buscando ruta desde {nodo_inicio} hasta {nodo_destino}")
    print("=====================================")
    print(dijkstra(G, nodo_inicio, nodo_destino))
main()
