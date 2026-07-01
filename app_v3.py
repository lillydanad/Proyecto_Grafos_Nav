import os
import io
import time

import streamlit as st
import osmnx as ox
import matplotlib.pyplot as plt
import pandas as pd
import contextily as cx

from src.astar import astar
from src.dijkstra import dijkstra

# ---------------- CONFIGURACIÓN ----------------

st.set_page_config(
    page_title="Comparador Dijkstra vs A*",
    layout="wide"
)

st.title("🚗 Comparador de Rutas - Miraflores")
st.write("Proyecto de Grafos - Dijkstra vs A*")

# ---------------- CARGAR MAPA ----------------

ruta = os.path.join(
    os.path.dirname(__file__),
    "data",
    "miraflores.graphml"
)

@st.cache_resource
def cargar_grafo():
    return ox.load_graphml(ruta)

@st.cache_resource
def proyectar_grafo(_G):
    """Versión proyectada a Web Mercator (EPSG:3857), solo para dibujar
    con mapa base real. Los algoritmos siguen corriendo sobre el grafo
    original en lat/lon (_G), porque la heurística de A* asume grados."""
    return ox.project_graph(_G, to_crs="EPSG:3857")

G = cargar_grafo()
G_proj = proyectar_grafo(G)

lista_nodos = list(G.nodes())

st.success(f"Mapa cargado correctamente ({len(lista_nodos)} nodos)")

# ---------------- ETIQUETAS DE NODOS (nombre de calle más cercana) ----------------
# OSMnx no le pone "nombre de lugar" a los nodos (son solo intersecciones),
# pero sí podemos usar el nombre de la calle de alguna arista que toque ese nodo.
# Esto se calcula UNA sola vez y se cachea, para no recalcular en cada interacción.

@st.cache_data
def construir_nombres_calle(_G):
    nombres = {}
    for nodo in _G.nodes():
        nombre_calle = None

        for _, _, datos in _G.edges(nodo, data=True):
            nombre = datos.get("name")
            if nombre:
                if isinstance(nombre, list):
                    nombre_calle = nombre[0]
                else:
                    nombre_calle = nombre
                break

        nombres[nodo] = nombre_calle  # puede quedar en None si no hay nombre

    return nombres

nombres_calle = construir_nombres_calle(G)

def formatear_nodo(nodo_id):
    nombre = nombres_calle.get(nodo_id)
    if nombre:
        return f"{nombre} (nodo {nodo_id})"
    return f"Nodo {nodo_id}"

def etiqueta_corta(nodo_id):
    """Texto breve para anotar sobre el mapa (sin el 'nodo XXXX')."""
    nombre = nombres_calle.get(nodo_id)
    return nombre if nombre else f"Nodo {nodo_id}"

# ---------------- DETALLES TÉCNICOS (expander) ----------------

with st.expander("🔧 Detalles técnicos del proyecto"):
    st.markdown(
        f"""
        **Grafo de Miraflores**
        - Nodos (intersecciones): `{G.number_of_nodes()}`
        - Aristas (tramos de calle): `{G.number_of_edges()}`
        - CRS original: `{G.graph.get("crs", "desconocido")}`

        **Dijkstra**
        - Explora nodos por distancia acumulada real (`length` de cada arista, en metros).
        - Garantiza el camino más corto, pero explora en todas direcciones por igual.

        **A\\***
        - Usa la misma distancia acumulada real, más una heurística admisible:
          distancia euclidiana en línea recta al destino, convertida de grados a
          metros aproximados (`× 111320`).
        - Esto le permite "apuntar" hacia el destino y explorar muchos menos nodos.
        """
    )

# ---------------- SELECCIÓN DE NODOS ----------------

st.subheader("Selecciona los nodos")
st.caption(
    "Puedes escribir para buscar por nombre de calle. "
    "Como el grafo no trae nombres de lugares (POIs), se muestra "
    "la calle más cercana a cada intersección como referencia."
)

col1, col2 = st.columns(2)

with col1:
    origen = st.selectbox(
        "Origen",
        lista_nodos,
        index=120,
        format_func=formatear_nodo
    )

with col2:
    destino = st.selectbox(
        "Destino",
        lista_nodos,
        index=950,
        format_func=formatear_nodo
    )

# ---------------- HISTORIAL DE SESIÓN ----------------

if "historial" not in st.session_state:
    st.session_state.historial = []

# ---------------- DIBUJO DE MAPA (con basemap real) ----------------

def dibujar_resultado(ax, G_plot, camino, visitados, origen, destino, color_ruta, titulo):
    # IMPORTANTE: cuando se le pasa un ax propio a ox.plot_graph_route,
    # OSMnx NO dibuja el grafo de fondo (solo el punto de origen/destino
    # y la línea de ruta), y por lo tanto el zoom queda determinado por
    # autoscale de matplotlib según lo que SÍ se dibuje. Como A* visita
    # muchos menos nodos que Dijkstra, su mapa terminaba "zoomeado" a esa
    # zona chica. Por eso dibujamos el grafo completo primero, fijando
    # el mismo extent en ambos mapas.
    ox.plot_graph(
        G_plot,
        ax=ax,
        show=False,
        close=False,
        node_size=0,
        edge_color="#999999",
        edge_linewidth=0.5,
        bgcolor="none",
    )

    # Guardamos los límites del grafo completo para reimponerlos al final
    # (por si algún scatter/plot posterior los vuelve a autoescalar).
    xlim_completo = ax.get_xlim()
    ylim_completo = ax.get_ylim()

    x = [G_plot.nodes[n]["x"] for n in visitados]
    y = [G_plot.nodes[n]["y"] for n in visitados]

    ax.scatter(x, y, c="cyan", s=10, alpha=0.5, label="Visitados", zorder=3)

    ox.plot_graph_route(
        G_plot,
        camino,
        route_color=color_ruta,
        route_linewidth=3,
        node_size=0,
        ax=ax,
        show=False,
        close=False
    )

    x_origen, y_origen = G_plot.nodes[origen]["x"], G_plot.nodes[origen]["y"]
    x_destino, y_destino = G_plot.nodes[destino]["x"], G_plot.nodes[destino]["y"]

    ax.scatter(x_origen, y_origen, c="green", s=120, label="Origen", zorder=5)
    ax.scatter(x_destino, y_destino, c="red", s=120, label="Destino", zorder=5)

    ax.annotate(
        etiqueta_corta(origen),
        xy=(x_origen, y_origen), xytext=(0, 10), textcoords="offset points",
        ha="center", fontsize=8, fontweight="bold", color="darkgreen",
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="green", alpha=0.9),
        zorder=6,
    )
    ax.annotate(
        etiqueta_corta(destino),
        xy=(x_destino, y_destino), xytext=(0, 10), textcoords="offset points",
        ha="center", fontsize=8, fontweight="bold", color="darkred",
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="red", alpha=0.9),
        zorder=6,
    )

    # Reimponemos el extent del grafo completo (por si el scatter de
    # visitados o la ruta lo volvieron a autoescalar), así ambos mapas
    # (Dijkstra y A*) quedan siempre con el mismo nivel de zoom.
    ax.set_xlim(xlim_completo)
    ax.set_ylim(ylim_completo)

    # Mapa base real (calles/tiles) detrás de todo lo demás
    try:
        cx.add_basemap(
            ax,
            crs=G_plot.graph["crs"],
            source=cx.providers.CartoDB.Positron,
            zorder=-1,
        )
    except Exception as e:
        st.warning(f"No se pudo cargar el mapa base (¿sin conexión a internet?): {e}")

    ax.set_axis_off()
    ax.set_title(titulo, fontsize=12, fontweight="bold")
    ax.legend(loc="upper right", fontsize=8)


if st.button("Calcular Ruta"):

    if origen == destino:
        st.error("Origen y destino no pueden ser iguales.")
        st.stop()

    inicio = time.perf_counter()
    dist_dij, camino_dij, visitados_dij = dijkstra(G, origen, destino)
    tiempo_dij = (time.perf_counter() - inicio) * 1000

    inicio = time.perf_counter()
    dist_astar, camino_astar, visitados_astar = astar(G, origen, destino)
    tiempo_astar = (time.perf_counter() - inicio) * 1000

    if len(camino_dij) == 0 or len(camino_astar) == 0:
        st.error("No existe una ruta entre esos dos nodos.")
        st.stop()

    speedup = tiempo_dij / tiempo_astar if tiempo_astar > 0 else float("inf")

    # --- Guardar en el historial de la sesión ---
    st.session_state.historial.append({
        "Origen": etiqueta_corta(origen),
        "Destino": etiqueta_corta(destino),
        "Distancia Dijkstra (m)": round(dist_dij, 1),
        "Distancia A* (m)": round(dist_astar, 1),
        "Tiempo Dijkstra (ms)": round(tiempo_dij, 2),
        "Tiempo A* (ms)": round(tiempo_astar, 2),
        "Nodos explorados Dijkstra": len(visitados_dij),
        "Nodos explorados A*": len(visitados_astar),
        "Speedup (A* vs Dijkstra)": round(speedup, 2),
    })

    st.success("Rutas encontradas. Comparando ambos algoritmos:")

    # --- Badge de ganador ---
    if tiempo_astar < tiempo_dij:
        st.info(f"🏆 **A\\*** fue más rápido: {speedup:.2f}x respecto a Dijkstra "
                f"({len(visitados_dij) - len(visitados_astar)} nodos menos explorados).")
    elif tiempo_dij < tiempo_astar:
        st.info(f"🏆 **Dijkstra** fue más rápido esta vez, por {1/speedup:.2f}x "
                f"respecto a A* (poco común, puede pasar en rutas muy cortas).")
    else:
        st.info("🤝 Empate técnico en tiempo de ejecución.")

    # --- Métricas ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tiempo Dijkstra (ms)", f"{tiempo_dij:.2f}")
    m2.metric("Tiempo A* (ms)", f"{tiempo_astar:.2f}")
    m3.metric("Speedup (A* vs Dijkstra)", f"{speedup:.2f}x")
    m4.metric("Nodos explorados (Dij / A*)", f"{len(visitados_dij)} / {len(visitados_astar)}")

    m5, m6 = st.columns(2)
    m5.metric("Distancia Dijkstra", f"{dist_dij:.1f} m")
    m6.metric("Distancia A*", f"{dist_astar:.1f} m")

    # --- Mapas lado a lado ---
    st.subheader("🗺️ Espacio de búsqueda")
    col_izq, col_der = st.columns(2)

    with col_izq:
        fig1, ax1 = plt.subplots(figsize=(7, 7))
        dibujar_resultado(
            ax1, G_proj, camino_dij, visitados_dij, origen, destino,
            color_ruta="red", titulo="Dijkstra"
        )
        st.pyplot(fig1)

    with col_der:
        fig2, ax2 = plt.subplots(figsize=(7, 7))
        dibujar_resultado(
            ax2, G_proj, camino_astar, visitados_astar, origen, destino,
            color_ruta="orange", titulo="A*"
        )
        st.pyplot(fig2)

# ---------------- HISTORIAL Y DESCARGA (persiste entre corridas) ----------------

if st.session_state.historial:
    st.divider()
    st.subheader("📜 Historial de esta sesión")

    df_historial = pd.DataFrame(st.session_state.historial)
    st.dataframe(df_historial, use_container_width=True)

    col_csv, col_xlsx, col_reset = st.columns([1, 1, 1])

    with col_csv:
        csv_bytes = df_historial.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Descargar CSV",
            data=csv_bytes,
            file_name="benchmark_rutas_miraflores.csv",
            mime="text/csv",
        )

    with col_xlsx:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_historial.to_excel(writer, index=False, sheet_name="Benchmark")
        st.download_button(
            "⬇️ Descargar Excel",
            data=buffer.getvalue(),
            file_name="benchmark_rutas_miraflores.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    with col_reset:
        if st.button("🗑️ Limpiar historial"):
            st.session_state.historial = []
            st.rerun()