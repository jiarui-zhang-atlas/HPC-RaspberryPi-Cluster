#!/usr/bin/env python
# MPI part of Traffic_Simulation_RPi_Cluster

from logging import NOTSET
from mpi4py import MPI
from networkx.classes.function import edges
import osmnx as ox
import networkx as nx
import time

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
import math 
import pandas as pd
import numpy as np
from tqdm import tqdm
import sys
import time
import random

from Settings import settings
from Simulation import Simulation
#from StreetGraph import StreetGraph

class ClusterMPI(object):
    
    def __init__(self):
        # get process info from MPI
        rank= MPI.COMM_WORLD.Get_rank() 
        num_process = MPI.COMM_WORLD.Get_size()
        name_node = MPI.Get_processor_name()
        
        sys.stdout.write(
            "I am process %d of %d on node %s.\n"
            %(rank, num_process, name_node)
        )
        
        if rank == 0:
            start = time.time()
            
            #print("-------- Street network and agents are loading --------\n")

        G = ox.load_graphml('./data/Manhattan_graph.graphml')
        edges = ox.graph_to_gdfs(G, nodes= None)
        edges['traffic_load'] = 0
        edges['weight'] = 0
        edges['ori_travel_time'] = edges['travel_time']
        ori_travel_time = edges['ori_travel_time'].to_dict()
        nx.set_edge_attributes(G, ori_travel_time, 'ori_travel_time')

        all_agents = pd.read_csv('all_agents_datasets.csv')
        all_agents_df = pd.DataFrame(all_agents)
        # Time Series
        all_agents_df['tpep_pickup_datetime'] = pd.to_datetime(all_agents_df['tpep_pickup_datetime'])
        all_agents_df['tpep_dropoff_datetime'] = pd.to_datetime(all_agents_df['tpep_dropoff_datetime'])
        all_agents_df = all_agents_df.set_index('tpep_pickup_datetime')

        # timestamps  series: period: 20 mins
        time_series = pd.date_range(start="2016-01-06 08:00:00", end="2016-01-06 22:00:00", freq = "20T")
        RMSE_list = []
        steps_num = len(time_series) - 1

        for step in range(steps_num):
            
            print('Current Simulation Step is: ', step)

            start_simu_time = str(time_series[step])
            end_simu_time = str(time_series[step + 1])

            #sub_agents_df = all_agents_df.loc['2016-01-06 08:00:00':'2016-01-06 08:05:00']
            sub_agents_df = all_agents_df.loc[start_simu_time:end_simu_time]
            origs = sub_agents_df['origs'].values.tolist()
            dests = sub_agents_df['dests'].values.tolist()
            gt_travel_time = sub_agents_df['interval_seconds'].values.tolist()
            index = sub_agents_df['id'].values.tolist()
            
            send_data = None
            
            send_count = int(math.ceil(len(origs)/num_process))
            num_routes_info = int(send_count * num_process)
            #num_pairs = len(origs)

            if rank == 0:
                print("-------- Street network and agents...Done --------\n")
                edge_count_list = []
                edges_count_pd = edges[['osmid','traffic_load']]
                edges_count_pd['traffic_load'] = 0
                edge_count_list = edges_count_pd.values.tolist()
                
                # Generate all pairs(orig-dest) in rank=0 master node, create even sub-arrays after padding.
                simu_pairs = np.stack((origs,dests,gt_travel_time,index), axis = 1)
                padding = int((-len(simu_pairs))%num_process)
                pad_pairs = np.zeros((padding,4), dtype='int')
                send_pairs = np.concatenate((simu_pairs,pad_pairs),axis = 0, dtype='int64') # some index is too long

                send_data = send_pairs
                print("---- process {} scatter Orig-Dest pairs with the size of {} to other process, each process got {} items ---- \n".format(rank,len(send_data),send_count))
            
            else:
                send_data = None
                edge_count_list = []

            # ---------- Code below run on all nodes individually with respect to Recv/BCast data -------- #
            edge_count_list = MPI.COMM_WORLD.bcast(edge_count_list,root = 0)

            recv_buf = np.zeros(send_count*4,dtype='int64').reshape(send_count,4,order='C')

            MPI.COMM_WORLD.Scatter(send_data, recv_buf, root=0)
            print("-------- process {} recv orig-dest pairs with the size of {} ------ Start Simulation ------ at step {}\n".format(rank,send_count,step))
            time.sleep(1)
            #print("-------- Start simulation with the step of {} at rank {} --------\n".format(settings["max_simulation_step"], rank))
            #time.sleep(1)
            
            simulator = Simulation(G,recv_buf,rank,edge_count_list)
            # indicator threshold => travel_time,'weight' based on 'count'=> delta <0.0001
            # several primary roads =>
            simulator.sub_simu()
            # traffic load of each edge.
            total_traffic_load = np.zeros(len(simulator.traffic_load), dtype='i')
            routes_info = np.zeros(num_routes_info*6).reshape(num_routes_info,6,order='C')
            # route_info: travel_time, len
            #print("rank {} simulation_traffic load{}".format(rank,simulator.traffic_load))
            MPI.COMM_WORLD.Allreduce(simulator.traffic_load, total_traffic_load, op=MPI.SUM)
            MPI.COMM_WORLD.Allgather(simulator.route_info, routes_info)
            
            
            #print("all routes info{} with the size of {}\n".format(routes_info, len(routes_info)))
            update_edge_gdf(G,edges,total_traffic_load)

            # Error Distribution Plot and RMSE
            if rank == 0:
                print(" ------ Traffic infomation and route infos updated...Done ------")
                all_routes_info = np.array(routes_info)
                all_index = all_routes_info[:,0]
                all_err = []
                for i in range(len(all_routes_info)):
                    err = all_routes_info[i,4]
                    flag = all_routes_info[i,5]
                    if err < 2000 and flag == 1.0:
                        all_err.append(err)

                all_err = [err for err in all_routes_info[:,4] if err<2000]
                all_err_np = np.square(np.array(all_err))

                RMSE = math.sqrt(all_err_np.sum()/len(all_err_np))
                RMSE_list.append(RMSE)
                x_list = list(range(1,len(all_err)+1,1))
                
                fig = plt.hist(all_err, bins = 40)
                plt.title('error_histogram_{}_{} with RMSE {}'.format(start_simu_time, end_simu_time, round(RMSE,1)))
                plt.xlabel("error_value")
                plt.ylabel("num of error")
                plt.savefig('/home/pi/error_distribution/error_histogram_{}_{}'.format(start_simu_time, end_simu_time))
                plt.clf()

                #--------- Plot traffic load figure -------- #
                edges2 = ox.graph_to_gdfs(G, nodes= None)
                max_load = max(edges2['traffic_load'].values)
                min_load = min(edges2['traffic_load'].values)
                norm = plt.Normalize(vmin=min_load,vmax=max_load)

                ec = ox.plot.get_edge_colors_by_attr(G, attr="traffic_load", cmap="Oranges") #cmap: matplotlib colormap
                
                fig2, ax = ox.plot_graph(
                    G,node_color="w", node_size = 0, bgcolor='#696969', edge_color=ec, edge_linewidth=0.8, show = False)
                cb = fig2.colorbar(cm.ScalarMappable(norm=norm, cmap="Oranges"), ax = ax, orientation='vertical')
                cb.set_label('Traffic load from {} to {}'.format(start_simu_time, end_simu_time), fontsize = 10)
                
                #fig2.savefig('/home/pi/traffic_load_figures/Manhattan_traffic_load {}_{}.jpg'.format(start_simu_time, end_simu_time), dpi=1200)
            # --------------------------------------------------------------- #
            # -------------- Algorithm: update travel time ------------------ #
            # 1. How to set the convergence condition (threshold) for simulation.
            capacity_hour = 1500 # capacity 1 hour.
            capacity = 1500 # 20 mins AS 1ST STEP => 08:20-08:40
            
            for u,v,k,d in G.edges(keys=True, data=True):
    
             # running_time, step_size => 20mins
                # Measures:
                # step_size => 10mins, 20mins, 40mins, 1 hour,...
                # road_types => capacity
                # always calculate the error between simulated and real travel_time, line chart,...
                # error distribution, percentage 
                # taxi behaviourss
                ori_travel_time = d['ori_travel_time']
                
                if d['speed_kph'] < 20:
                    d['travel_time'] = ori_travel_time * (1 + 40* d['traffic_load']/(0.9*capacity))
                elif d['speed_kph'] > 20 and d['speed_kph'] < 60:
                    d['travel_time'] = ori_travel_time * (1 + 40* d['traffic_load']/(1 * capacity))
                else:
                    d['travel_time'] = ori_travel_time * (1 + 40* d['traffic_load']/(1.3 * capacity))
                
                #d['travel_time'] = (d['length'] * 3.6 / (d['speed_kph'])) * (1 + (d['traffic_load']/(1.3*capacity)))
                
                #d['travel_time'] = ori_travel_time
                d['travel_time'] = round(d['travel_time'],2)
                del_t = d['travel_time'] - ori_travel_time
            
            # Message output
            if rank == 0:

                new_edges = ox.graph_to_gdfs(G,nodes = None)
                print(new_edges.iloc[0][['travel_time','ori_travel_time','traffic_load']])


            # --------------------------------------------------------------- #
        if rank == 0:

            # print("Edges in Graph got updates \n {} with the sum {}".format(edges, total_traffic_load.sum()))
            end = time.time()
            running_time = end - start
            print("\n rungning time on cluster is {} s".format(running_time))
            x_axis = np.array(list(range(1,len(RMSE_list)+1,1)))
            RMSE_np = np.array(RMSE_list)
            plt.scatter(x_axis,RMSE_np)
            plt.show()


'''
            edges2 = ox.graph_to_gdfs(G, nodes= None)
            max_load = max(edges2['traffic_load'].values)
            min_load = min(edges2['traffic_load'].values)
            norm = plt.Normalize(vmin=min_load,vmax=max_load)

            ec = ox.plot.get_edge_colors_by_attr(G, attr="traffic_load", cmap="Oranges") #cmap: matplotlib colormap
            
            fig, ax = ox.plot_graph(
                G,node_color="w", node_size = 0, bgcolor='#696969', edge_color=ec, edge_linewidth=0.8)

            cb = fig.colorbar(cm.ScalarMappable(norm=norm, cmap="Oranges"), ax = ax, orientation='vertical')
            cb.set_label('Traffic load from 08:00 - 22:00', fontsize = 10)
            fig.savefig('Manhattan_08:00_22:00.jpg', dpi=1200)
'''
        
# update count column in edges
def update_edge_gdf (Graph, edges_gdf, traffic_load):

    edge_count_update_gdf = pd.DataFrame(traffic_load, columns= ['traffic_load'])

    del edges_gdf['traffic_load']

    edges_gdf['traffic_load'] = edge_count_update_gdf['traffic_load'].values
    edges_count_dict = edges_gdf['traffic_load'].to_dict()
    nx.set_edge_attributes(Graph, edges_count_dict, 'traffic_load')
    
    #edges_gdf = ox.graph_to_gdfs(Graph, nodes = False)
    
    return edges_gdf, Graph


if __name__ == "__main__":
    ClusterMPI()
