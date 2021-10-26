# HPC-RaspberryPi-Cluster
A RaspberryPi supercomputer for HPC simulation, code in master branch. 
## Table of contents
* [Introduction](#introduction)
* [Background info](#background-info)
* [Hardware components](#hardware-components)
* [Setup environment](#setup-environment)
* [Setup master node](#setup-master-node)
* [Setup the whole cluster](#setup-the-whole-cluster)
* [Introduction of dataset](#introduction-of-dataset)
* [Algorithm of mobility simulation](#algorithm-of-mobility-simulation)
* [Results](#results)
* [Summary](#summary)

## Introduction
Parallel and distributed computing is an interesting topic, but building a High Performance Computing (HPC) supercomputer/cluster has often required the usage of expensive hardware and complex machine setups. Thanks to the Raspberry Pi's low costs, small physical size and powerful performance, It's easier and cheaper for users to explore the parallel computing even with industry standard and learn both software and hardware technologies. The main goal of this project is to build a 8-node distributed computing cluster system using the Raspberry Pi 4B single-board computers for some simple simulations. 
## Background info

* **Raspberry Pi and Raspberry Pi OS** <br>
Raspberry Pi is a tiny and inexpensive single-board computer that is capable of running Linux or other operating systems based on the ARM processor. With the help of expansion provided by the sufficient built-in ports: Gigabit Ethernet, USB 3.0, Mirco HDMI Ports and GPIO, Raspberry Pi can be used in robotics, smart home hub, media centre factory controller and some IoT projects. Other benefit of the Raspberry Pi is that it also uses MicroSD cards as secondary storage, which can be easily written and flashed by different operating systems and allowing you to create an image and then clone it for multiple machines. <br>

   <div align="center"><img src="https://github.com/Atlaszjr-star/HPC-RaspberryPi-Cluster/blob/main/figures/raspberry-pi.webp" width="300px" /></div>

* **Parallel Computing and MPI** <br>
The basic concept of parallel computing is that a large problem can be divided into smaller chunks, which can be distributed and computed separately on different computers (nodes) within the cluster. In this project, the parallel computing technology I used is MPICH, which is an implementation of Message Passing Interface (MPI) stardard. MPICH allows users running the distributed chunks on different processes of the CPU separately from the single computer (node) or all processes from the computers (nodes) in the cluster.
   
* **OSMnx** <br>
OSMnx is a Python package that lets you download geospatial data from OpenStreetMap and model, project, visualized, and analyzed real-world street networks and any other geospatial geometries.

* **NetworkX** <br>
NetworkX is a Python package for the creation, manupulation, and study of the structure, dynamics, and functions of complex networks. With NetworkX you can load and store networks in standard and nonstandard data formats, generate many types of random and classic networks, analyze network structure, build network models, design new network algotithms, draw networks, and much more.


## Hardware Components

* 8 Raspberry Pi 4B computer single-boards, 4GB RAM, 4-cores CPU, one of them is used as master node in cluster.
* 8 microSD cards with 64GB as the hard disk of Raspberry Pi.
* 8 sets of cooling cubes for cooling the RAM and processor.
* 2 sets of case shelf and cooling fans.
* 1 Gigabit Switch for message communication between the nodes in the local network.
* 1 Powerstation with 10 ports.
* 8 Gigabit Ethernet cables.
* 8 USB-C power cables.
   <br>
   <div align="center">
   <img src="https://github.com/Atlaszjr-star/HPC-RaspberryPi-Cluster/blob/main/figures/before.jpg" width="380px" height="250px" />
   <img src="https://github.com/Atlaszjr-star/HPC-RaspberryPi-Cluster/blob/main/figures/all_Devices.jpg" width="380px" height="250px" />
   </div>
   <div align="center">
   </div> 
      <br>
   <div align="center">
   <img src="https://github.com/Atlaszjr-star/HPC-RaspberryPi-Cluster/blob/main/figures/details-night.jpg" width="380px"/>
   <img src="https://github.com/Atlaszjr-star/HPC-RaspberryPi-Cluster/blob/main/figures/masternode.jpg" width="380px" />
   </div>

## Setup Environment
* Operating System image: Raspberry Pi OS with desktop, 32 bit, kernel version: 5.10
* Python: 3.7
* MPICH: 3.4.2
* mpipy: 2.0.0
* osmnx: 1.1.1 and its dependencies: 
   * networkx>=2.5
   * numpy>=1.19
   * pandas>=1.1
   * geopandas>=0.9
   * pyproj>=2.6
   * matplotlib>=3.3
   * requests>=2.25
   * Rtree>=0.9
   * Shapely>=1.7

## Setup master node
1. Flash the 64GB microSD card with Raspberry Pi OS, 32 bit, then master node gets a clean RPi Linux OS
2. Install python 3.7
3. Install MPICH: 3.4.2
```shell
# --------------------- Install MPICH ----------------- #
$ sudo apt-get update
$ mkdir mpich3
$ cd mpich3
$ wget http://www.mpich.org/static/downloads/3.4.2/mpich-3.4.2.tar.gz
$ tar xfz mpich-3.4.2.tar.gz
$ mkdir build install
$ cd build
# --disable-fortran since we don't use fortran for programming
$ /home/pi/mpich3/mpich-3.4.2/configure --disable-fortran --with-device=ch4:ofi -prefix=/home/pi/mpich3/install
# takes a while...
$ make
$ make install
$ export PATH=$PATH:/home/pi/mpich3/install/bin # or the path you installed
$ sudo nano /home/pi/.profile
# add your MPICH path to .profile
$ export = PATH="$PATH:/home/pi/mpich3/install/bin"
# test installation
$ mpiexec -n 1 hostname
```
4. Install mpi4py: 2.0.0, mpi4py is a wrapper of MPICH
```shell
$ sudo apt install python-pip python-dev libopenmpi-dev
$ sudo apt install python3-mpi4py
$ pip3 list
$ mpipy 2.0.0
# test
$ mkdir mpi4py
$ cd mpi4py
$ sudo nano test.py
# copy following code and paste to test.py
# ------------------ Python --------------- #
from mpi4py import MPI
import sys

size = MPI.COMM_WORLD.Get_size()
rank = MPI.COMM_WORLD.Get_rank()
name = MPI.Get_processor_name()

sys.stdout.write(
     "Hello, World! I am process %d of %d on %s.\n"
     % (rank, size, name))
-----------------------------------------------
$ mpirun -np 4 python3 test.py
# output: 
# Hello, World! I am process 0 of 4 on raspberrypi.
# Hello, World! I am process 1 of 4 on raspberrypi.
# Hello, World! I am process 2 of 4 on raspberrypi.
# Hello, World! I am process 3 of 4 on raspberrypi.
```
5. Enable SSH for master node
```shell
# Enable SSH in configuration page 
$ sudo raspi-config
# Find the IP address, in this project, we use Ethernet port (eth0) instead of wireless connection
$ ifconfig 
# install xrdp for remote access from other PC in the same local network
$ sudo apt-get install xrdp
# Setting DNS
$ sudo apt-get update
$ sudo nano /etc/dhcpcd.conf
# modify static domain_name_servers = 8.8.8.8
$ sudo nano /etc/resolv.conf
# add two lines
   # nameserver 8.8.8.8
   # nameserver 8.8.4.4
# restart the networking service
$ sudo server dhcpcd restart
$ sudo systemctl daemon-reload
$ sudo /etc/init.d/networking restart
```
6. Install OSMnx via pip instead of conda, Raspberry Pi has no the stable version of conda. Make sure you have already installed all dependencies.
7. Now you create a RPi OS with all packages and dependencies we need.
8. Prepare at least 64GB space in your computer (or mobile hard disk). Convert the created OS to an image file, the size of the image file will be approximately 64GB, which depends the size of microSD card you used in the master node.

## Setup the whole cluster
1. Flash the converted image to the 7 microSD cards for the other 7 worker nodes, now the other 7 nodes also get the same RPi OS with all packages and dependencies as master node.
2. Log in each node individually, in your local network, change the certain static eth0 IP address for each node. Static IP can be changed in the file. In case of IP address conflicts in your local network, please check all the IP address used by the other devices before you change the IP address as static ip, 
```shell
sudo nano /etc/dhcpcd.conf
```
3. Create a file named "machinefile" in master node, record the static IP address of all nodes.
```
192.168.x.xxx        (node 0, master node)
192.168.x.xxx        (node 1, worker node)
192.168.x.xxx        (node 2, worker node)
192.168.x.xxx        (node 3, worker node)
192.168.x.xxx        (node 4, worker node)
192.168.x.xxx        (node 5, worker node)
192.168.x.xxx        (node 6, worker node)
192.168.x.xxx        (node 7, worker node)
```
4. Now you can login any other nodes from one node via SSH after SSH authentications, even without password if you configure the master's SSH keys to other nodes. You can also change the username of each node (I change it to "pi"). You can login the other node from master node like this:
```shell
# 192.168.x.xxx, the ip address of the node you want to login.
$ ssh pi@192.168.x.xxx
```
5. Now, create your working space (my folder is called Simulation_MPI) at master node, then you can develop your MPI application in this working space. Each worker node need the same working space at the same path from master node, so you can distribute your master node's working space with all the files to each worker node at the same path:
```shell
scp -r /home/pi/Simulation_MPI pi@192.168.x.xxx:/home/pi
scp -r /home/pi/Simulation_MPI pi@192.168.x.xxx:/home/pi
scp -r /home/pi/Simulation_MPI pi@192.168.x.xxx:/home/pi
scp -r /home/pi/Simulation_MPI pi@192.168.x.xxx:/home/pi
scp -r /home/pi/Simulation_MPI pi@192.168.x.xxx:/home/pi
scp -r /home/pi/Simulation_MPI pi@192.168.x.xxx:/home/pi
scp -r /home/pi/Simulation_MPI pi@192.168.x.xxx:/home/pi
```
6. "Hello world" in the cluster with 8 nodes, 32 processes.

```shell
Run the following script in the cluster:
--------------------- Python ----------------------
from mpi4py import MPI
import sys

size = MPI.COMM_WORLD.Get_size()
rank = MPI.COMM_WORLD.Get_rank()
name = MPI.Get_processor_name()

sys.stdout.write(
     "Hello, World! I am process %d of %d on the node %s.\n"
     % (rank, size, name))

----------------------------------------------------
# btl_tcp_if_include: configure with TCP connection
# eth0: ethernet ip address
# -np 32: define the number of processes used
# machinefile: ip address of nodes
$ mpirun --mca btl_tcp_if_include eth0 -np 32 -machinefile /home/pi/machinefile python3 /home/pi/Simulation_MPI/test.py

# output
# Hello, World! I am process 0 of 32 on node master
# Hello, World! I am process 1 of 32 on node master
# Hello, World! I am process 2 of 32 on node master
# Hello, World! I am process 3 of 32 on node master
# Hello, World! I am process 4 of 32 on node node1
# Hello, World! I am process 5 of 32 on node node1
# Hello, World! I am process 6 of 32 on node node1
# Hello, World! I am process 7 of 32 on node node1
# Hello, World! I am process 8 of 32 on node node2
# ...
# Hello, World! I am process 28 of 32 on node node7
# Hello, World! I am process 29 of 32 on node node7
# Hello, World! I am process 30 of 32 on node node7
# Hello, World! I am process 31 of 32 on node node7
```
7. Now a Raspberry Pi supercomputer with 8 nodes is done ;-)

## Introduction of Dataset
For the simple mobility simulations, the dataset is taxi 237120 pickup-dropoff pairs from Manhattan, 2016-06-01, from 08:00-22:00.
   <div align = "center"> 
      <img src="https://github.com/Atlaszjr-star/HPC-RaspberryPi-Cluster/blob/main/figures/Datasets.png" width="600px" height="100px" /> 
      <br>
      <img src="https://github.com/Atlaszjr-star/HPC-RaspberryPi-Cluster/blob/main/figures/Manhattan.png" width="380px" height="250px" />
   </div>
   
## Algorithm of Mobility Simulation
The Workflow of Mobility simulation is shown below.
   <div align = "center"> 
      <img src="https://github.com/Atlaszjr-star/HPC-RaspberryPi-Cluster/blob/main/figures/Workflow.png" width="800px" height="450px" /> 
   </div>
   
## Results
1. After the distributed calculation of traffic load on each edge in the network, the travel time of the shortest route has been recalculated based on the current traffic load information provided by last step.
   <div align = "center"> 
      <img src="https://github.com/Atlaszjr-star/HPC-RaspberryPi-Cluster/blob/main/figures/heatmap.png" width="800px" height="350px" /> 
   </div>
2. The traffic load of all agents within one hour (08:00 - 09:00) and within the whole day (08:00-22:00) are calculated on both 4 processes of master node and 32 processes on the cluster. The comparison of running time is shown below:
   <div align = "center"> 
      <img src="https://github.com/Atlaszjr-star/HPC-RaspberryPi-Cluster/blob/main/figures/compare.png" width="700px" height="400px" /> 
   </div>
## Summary
The aims of this project are:

-  Set up a Raspberry Pi supercomputer cluster with 8 nodes and 32 processes.
-  Set up the work environment for parallel computing based on MPI standard in the cluster
-  Explore the possibility of HPC application development in the cluster by running simple mobility simulations.

