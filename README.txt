ROUTE EFFICIENCY COMPARATOR: DIJKSTRA VS A* IN MIRAFLORES

1. Project Overview
This project provides a comprehensive platform for evaluating the performance and optimizing vehicular routes in high-density urban environments, using the district of Miraflores in Lima, Peru, as a case study. By extracting real-world road networks from OpenStreetMap, the application empirically compares the algorithmic efficiency of the classic Dijkstra algorithm against the heuristic-driven search of the A* (A-Star) algorithm. 

The core system analyzes how using an admissible and consistent heuristic mitigates the impact of traffic congestion and asymmetrical road networks, drastically reducing processing latency and search space in local compute nodes.

2. Features
- Dynamic Map Download: Automatically retrieves the road network filtered specifically for cars (network_type='drive') directly from OpenStreetMap using OSMnx.
- Optimized Algorithms: Implements both search engines guided by an efficient binary min-heap priority queue structure.
- Corrected Admissible Heuristic: Integrates a corrected Euclidean distance calculation adjusted for the latitude of Miraflores (~12 degrees South) to prevent overestimation and guarantee A*'s optimality.
- Interactive Control Panel: Features a web interface built on Streamlit that allows previewing nodes and intersections by their nearest adjacent street names.
- Advanced Geographic Visualization: Generates side-by-side comparative plots mapping explored search spaces (visited nodes) over real basemaps provided by Contextily.
- Benchmark Exporting: Tracks real-time performance metrics (execution times in milliseconds, search space reduction percentage, speedup factors) with options to download in CSV and Excel formats.

3. Prerequisites
To execute the simulation environment and the interactive application smoothly, a development environment based on Python 3.10.11 or higher is required, along with the following software dependencies:

- osmnx (For geographic graph downloading and manipulation)
- networkx (For graph data structure modeling)
- matplotlib (For rendering static maps and scatter layers)
- streamlit (For deploying the interactive web dashboard)
- pandas (For manipulating search history data)
- contextily (For overlaying real map tiles and basemaps)
- openpyxl (Required natively for Excel file exporting)

4. Installation & Usage

Step 1: Set up the environment and install dependencies
Install the required packages using your package manager:
pip install osmnx networkx matplotlib streamlit pandas contextily openpyxl

Step 2: Download map network data
Before starting the graphical interface, you must generate the serialized base map of the district locally. Run the map visualization script to initialize the data folder:
python visualize_district.py
This will create a 'data/' directory and save the processed topology inside 'data/miraflores.graphml'.

Step 3: Launch the interactive application
To initialize the web visualization suite and perform real-time comparisons of speed and search space benchmarks, execute:
streamlit run app_v3.py

5. Project Structure
The software modules are organized as follows:

data/
    └── miraflores.graphml          # Downloaded structured road graph dataset.
src/
    ├── __init__.py
    ├── astar.py                    # Core A* algorithm and corrected admissible heuristic function.
    └── dijkstra.py                 # Core blind Dijkstra algorithm using min-heap.
visualize_district.py               # Utility script to fetch and save the map from OpenStreetMap API.
visualize_route.py                  # Standalone script to compare route calculation times.
app_v3.py                           # Streamlit interactive dashboard and web interface visualization.

6. Authors
The methodological development, empirical analysis, and algorithmic implementation of this smart mobility ecosystem were conducted by the engineering team at Universidad ESAN:

- Daniela Ricapa - Software Engineering, Universidad ESAN (25100739@ue.edu.pe)
- Cielo Valle - ITIS Engineering, Universidad ESAN (25102283@ue.edu.pe)
- Hugo Barboza - Software Engineering, Universidad ESAN (25101714@ue.edu.pe)
- Gabriel Moscoll - Software Engineering, Universidad ESAN (25102267@ue.edu.pe)
