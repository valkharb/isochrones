import osmnx as ox
import sys


def load_map(place, type):
    ox.config(log_console=True, use_cache=True)
    G = ox.graph_from_place(place, network_type=type)
    ox.save_graphml(G, filename='network.graphml')
    with open('network_type.yml', 'w') as file:
        file.write(type)
    print('Map is downloaded and saved in network.graphml')


if __name__ == "__main__":
    place = sys.argv[1]
    type = sys.argv[2]
    load_map(place, type)