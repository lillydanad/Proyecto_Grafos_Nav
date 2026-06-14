import os
import osmnx as ox

def main():
    # 1. Crear la carpeta data localmente si no existe
    os.makedirs('data', exist_ok=True)
    
    lugar = "Miraflores, Lima, Peru"
    print("🛰️ Descargando el mapa de Miraflores desde OpenStreetMap...")
    
    # 2. Descargar la red vial (filtrada para autos)
    G = ox.graph_from_place(lugar, network_type='drive')
    print(f"✅ ¡Descargado! El mapa tiene {len(G.nodes)} esquinas (nodos).")

    # 3. Guardar el archivo que necesita Hugo
    ruta_guardado = "data/miraflores.graphml"
    ox.save_graphml(G, filepath=ruta_guardado)
    print(f"💾 Archivo guardado con éxito en: {ruta_guardado}")
    
    # 4. Mostrar el mapa en pantalla para confirmar que todo está bien
    print("🎨 Dibujando el mapa...")
    ox.plot_graph(G)

if __name__ == "__main__":
    main()