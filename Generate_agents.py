#!/usr/bin/env python

from networkx.classes.function import edges
import osmnx as ox
import networkx as nx
from Settings import settings
import numpy as np
import pandas as pd

G = ox.load_graphml('./data/Manhattan_graph.graphml')

# add speed and travel time
G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)
nodes, edges = ox.graph_to_gdfs(G)
# Geodataframe, update travel_time based on count column from simulation
edges['traffic_load'] = 0
edges['weight'] = 0

sub_agents = pd.read_csv('new_agents_manhattan.csv')
sub_agents_df = pd.DataFrame(sub_agents)

orig_lon = sub_agents_df['pickup_longitude'].values.tolist()
orig_lat = sub_agents_df['pickup_latitude'].values.tolist()
dest_lon = sub_agents_df['dropoff_longitude'].values.tolist()
dest_lat = sub_agents_df['dropoff_latitude'].values.tolist()

origs = ox.distance.nearest_nodes(G,orig_lon,orig_lat)
dests = ox.distance.nearest_nodes(G,dest_lon,dest_lat)

sub_agents_df['origs'] = pd.Series(origs)
sub_agents_df['dests'] = pd.Series(dests)

sub_agents_df.to_csv('all_agents_datasets.csv')
np.savetxt("all_agent_origs.txt",origs, fmt='%d')
np.savetxt("all_agent_dests.txt",dests,fmt='%d')

'''
G = ox.load_graphml('./data/Munich_graph.graphml')

num_agents =settings["num_agent"] -> test the upper limit:  time/memory/ 
# Generate random (orig-dest) pairs in first step as simulation agents
origs = np.random.choice(G.nodes, size=num_agents, replace = True)
dests = np.random.choice(G.nodes, size=num_agents, replace = True)
agents = dict()
for i in range(len(origs)):
    agents[i] = origs[i], dests[i]

file = open('agents.txt','w')
file.write(str(agents))
file.close

np.savetxt("agent_origs.txt",origs, fmt='%d')
np.savetxt("agent_dests.txt",dests,fmt='%d')
'''