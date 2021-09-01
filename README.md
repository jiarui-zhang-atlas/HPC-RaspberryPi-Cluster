# HPC-RaspberryPi-Cluster
A RaspberryPi supercomputer for HPC Simulation 
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
* [Known limitations](#known-limitations)

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
* osmnx: 1.1.1
* networkx>=2.5
* numpy>=1.19
* pandas>=1.1
* geopandas>=0.9
* pyproj>=2.6
* matplotlib>=3.3
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
## Setup the whole cluster
## Introduction of Dataset
## Algorithm of Mobility Simulation
## Results
## Known Limitations
