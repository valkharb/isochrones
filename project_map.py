import osmnx as ox
import sys


def project_map():
    ox.config(log_console=True, use_cache=True)
    G = ox.load_graphml('network.graphml')
    G = ox.project_graph(G)
    ox.save_graphml(G, filename='project.graphml')
    return 'Map was successfully projected and saved in project.graphml'


if __name__ == "__main__":
    project_map()