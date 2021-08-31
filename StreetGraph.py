from networkx.classes.function import edges
import osmnx as ox
import networkx as nx

import pandas as pd
import numpy as np


place = "Manhattan, New York, USA"
G = ox.graph_from_place(place, network_type="drive")
'''
filter = ['secondary','tertiary','tertiatry_link','unclassified','trunk','trunk_link','primary']
e = [(u,v,k) for u, v, k, d in G.edges(keys=True, data=True) if d['highway'] not in filter]
G.remove_edges_from(e)
G = ox.utils_graph.get_largest_component(G)
'''

# add speed and travel time
G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)
ox.save_graphml(G,'./data/Manhattan_graph.graphml')
