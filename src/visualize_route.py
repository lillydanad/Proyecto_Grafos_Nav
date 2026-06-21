import osmnx as ox
import matplotlib.pyplot as plt
import time  # <--- NUEVO: Módulo para controlar el tiempo
from dijkstra import dijkstra
from astar import astar

def main():
    ruta_archivo = "../data/miraflores.graphml"
    print("🛰️  Cargando el mapa local de Miraflores...")
    G = ox.load_graphml(ruta_archivo)
    
    lista_nodos = list(G.nodes())
    origen = lista_nodos[100]    
    destino = lista_nodos[1200]
    
    # --- CRONÓMETRO PARA DIJKSTRA ---
    print("⚡ Corriendo Dijkstra desde módulo original...")
    inicio_dijkstra = time.perf_counter()  # Arranca cronómetro
    _, _, visitados_dijkstra = dijkstra(G, origen, destino)
    fin_dijkstra = time.perf_counter()     # Detiene cronómetro
    
    # --- CRONÓMETRO PARA A* ---
    print("⚡ Corriendo A* desde módulo original...")
    inicio_astar = time.perf_counter()     # Arranca cronómetro
    distancia, camino_optimo, visitados_astar = astar(G, origen, destino)
    fin_astar = time.perf_counter()        # Detiene cronómetro
    
    # Calcular tiempos exactos en milisegundos (multiplicando por 1000)
    tiempo_dijkstra = (fin_dijkstra - inicio_dijkstra) * 1000
    tiempo_astar = (fin_astar - inicio_astar) * 1000
    
    # 2. Imprimir métricas (Ahora con Tiempos)
    print("\n📊 --- RESULTADOS DE LA COMPARACIÓN ---")
    print(f"Nodos explorados por Dijkstra: {len(visitados_dijkstra)}")
    print(f"Nodos explorados por A*: {len(visitados_astar)}")
    ahorro = 100 - (len(visitados_astar) / len(visitados_dijkstra) * 100)
    print(f"Reducción del espacio de búsqueda: {ahorro:.1f}%")
    print("-" * 40)
    print(f"⏱️  Tiempo de ejecución Dijkstra: {tiempo_dijkstra:.2f} ms")
    print(f"⏱️  Tiempo de ejecución A*: {tiempo_astar:.2f} ms")
    print(f"🚀 A* fue {tiempo_dijkstra / tiempo_astar:.1f} veces más rápido.")

    # 3. Dibujar las capas (El resto del código de Matplotlib queda idéntico)
    print("\n🎨 Generando mapa comparativo visual...")
    fig, ax = ox.plot_graph(G, node_size=0, edge_color='#444444', edge_linewidth=0.6, show=False, close=False)
    
    x_dij = [G.nodes[n]['x'] for n in visitados_dijkstra]
    y_dij = [G.nodes[n]['y'] for n in visitados_dijkstra]
    ax.scatter(x_dij, y_dij, c='yellow', s=15, alpha=0.3, label='Explorado por Dijkstra')
    
    x_ast = [G.nodes[n]['x'] for n in visitados_astar]
    y_ast = [G.nodes[n]['y'] for n in visitados_astar]
    ax.scatter(x_ast, y_ast, c='cyan', s=8, alpha=0.8, label='Explorado por A*')
    
    ox.plot_graph_route(G, camino_optimo, route_color='red', route_linewidth=3, node_size=0, ax=ax, show=False, close=False)
    ax.set_title("Dijkstra vs A* en Miraflores (Espacio de Búsqueda)", fontsize=12, fontweight='bold')
    plt.legend(loc='upper right')
    plt.show()

if __name__ == "__main__":
    main()