from networkx.classes.function import edges
import osmnx as ox
import networkx as nx

import matplotlib.pyplot as plt
import math 
import pandas as pd
import numpy as np
from tqdm import tqdm
import sys
import time
from Settings import settings

class Simulation(object):

    def __init__(self, Graph, pairs, rank, count_list):
        self.Graph = Graph
        self.pairs = pairs
        self.rank = rank
        self.step_count = 0
        self.traffic_load = []
        self.route_info = []
        self.count_list = count_list
        self.cur_route_dict = dict()
    
    def sub_simu(self):
        self.step_count += 1
        
        # Routes calculation
        if self.rank == 0:
            print("-------- Cluster Calculating valid routes -------- \n".format(self.rank))
        curr_valid_routes = []
        
        curr_valid_routes, curr_route_info = route_finding(self.Graph,self.pairs,curr_valid_routes,self.rank)
        self.route_info = np.array(curr_route_info)
   
        #Traffic Load Counting
        if self.rank == 0:
            print("\n --------Cluster Calculating the traffic load -------- \n")

        self.count_list = edge_count_route(self.Graph,curr_valid_routes,self.count_list)
        count_col = [i[1] for i in self.count_list]
        self.traffic_load = np.array(count_col,dtype='i')
        
        if self.rank == 0:
            print("\n-------- Traffic Load Calculation and update...Done --------\n")
        
        
def route_finding(G,pairs_buf,curr_valid_routes,rank):
    curr_origs = pairs_buf[:,0]
    curr_dests = pairs_buf[:,1]
    curr_gt_time = pairs_buf[:,2]    
    index = pairs_buf[:,3]

    curr_routes = ox.shortest_path(G,curr_origs, curr_dests, weight="travel_time", cpus = 1)

    cols = ['osmid','length','travel_time']
    route_info = []
    for i in range(len(curr_routes)):

        if curr_routes[i] is not None and len(curr_routes[i]) is not 1:
            # valid_routes
            curr_valid_route = curr_routes[i]
            #print("curr_valid_route is",curr_valid_route)
            curr_valid_routes.append(curr_valid_route)

            # route_info
            curr_gt_travel_time = round(int(curr_gt_time[i]),1)
            attrs = ox.utils_graph.get_route_edge_attributes(G,curr_valid_route)
            length_time_df = pd.DataFrame(attrs)[cols]
            # ---- travel time of route from all travel time of edges ---- #
            curr_simu_travel_time = round(int(length_time_df['travel_time'].sum()),1)
            curr_simu_length = round(length_time_df['length'].sum(),1)
            err_travel_time = round((curr_gt_travel_time - curr_simu_travel_time),1)
            # index, route_len, GT_travel_time, simulated_time, error_travel_time, route is not None -> 1
            route_info.append([int(index[i]),curr_simu_length,curr_gt_travel_time,curr_simu_travel_time,err_travel_time,1])
        # keep the same buffer size for route_infos on each process

        elif curr_routes[i] is None or len(curr_routes[i]) is 1:
            route_info.append([int(index[i]),0,0,0,0,0])

    #print("process {} calculate routes with the size of {} routes and the size of {} route infos\n".format(rank,len(curr_valid_routes),len(route_info)))

    #print("process {} calculate routes with the size of {} \n".format(rank,len(curr_valid_routes)))
    return curr_valid_routes, route_info

def edge_count_route(graph,valid_routes,count_list):
    
    for curr_route in valid_routes:
        edge_osmid = ox.utils_graph.get_route_edge_attributes(graph,curr_route,attribute='osmid',minimize_key='length')
        for i in range(len(count_list)):
            curr_osmid = count_list[i][0]
            if curr_osmid in edge_osmid:
                count_list[i][1] += 1

    return count_list


if __name__ == "__main__":
    # initial Graph with small size
    Graph = ox.load_graphml('./data/Manhattan_graph.graphml')
    pairs = None
    rank = 0
    count_list= None
    simu = Simulation(Graph,pairs,rank,count_list)
    simu.sub_simu()
