# HPC-RaspberryPi-Cluster
A RaspberryPi supercomputer for HPC Simulation 
## Table of contents
* [Introduction](#introduction)
* [Background info](#background-info)
* [Hardware Components](#hardware-components)
* [Technologies and Environment](#technologies-and-environment)
* [Setup master node](#setup-master-node)
* [Setup the whole cluster](#setup-the-whole-cluster)
* [Introduction of Dataset](#introduction-of-dataset)
* [Algorithm of Mobility Simulation](#algorithm-of-mobility-simulation)
* [Results](#results)
* [Known Limitations](#known-limitations)

## Introduction
Parallel and distributed computing is an interesting topic, but building a High Performance Computing (HPC) supercomputer/cluster has often required the usage of expensive hardware and complex machine setups. Thanks to the Raspberry Pi's low costs, small physical size and powerful performance, It's easier and cheaper for users to explore the parallel computing even with industry standard and learn both software and hardware technologies. The main goal of this project is to build a 8-node distributed computing cluster system using the Raspberry Pi 4B single-board computers for some simple simulations. 
## Background info

* **Raspberry Pi and Raspberry Pi OS** <br>

Raspberry Pi is a tiny and inexpensive single-board computer that is capable of running Linux or other operating systems based on the ARM processor. With the help of expansion provided by the sufficient built-in ports: Gigabit Ethernet, USB 3.0, Mirco HDMI Ports and GPIO, Raspberry Pi can be used in robotics, smart home hub, media centre factory controller and some IoT projects. Other benefit of the Raspberry Pi is that it also uses MicroSD cards as secondary storage, which can be easily written and flashed by different operating systems and allowing you to create an image and then clone it for multiple machines.<br>
   
   <div align=center><img src="https://github.com/Atlaszjr-star/HPC-RaspberryPi-Cluster/blob/main/figures/raspberry-pi.webp" width="300px" />
   
* **Parallel Computing and MPI** <br>
   
The basic concept of parallel computing is that a large problem can be divided into smaller chunks, which can be distributed and computed separately on different computers (nodes) within the cluster. In this project, the parallel computing technology I used is MPICH, which is an implementation of Message Passing Interface (MPI) stardard. MPICH allows users running the distributed chunks on different processes of the CPU separately from the single computer (node) or all processes from the computers (nodes) in the cluster.
   
* **OSMnx**
* **NetworkX**

## Hardware Components

* 8 Raspberry Pi 4B computer single-boards, 4GB RAM, 4-cores CPU, one of them is used as master node in cluster.
* 8 microSD cards with 64GB as the hard disk of Raspberry Pi.
* 8 sets of cooling cubes for cooling the RAM and processor.
* 2 sets of case shelf and cooling fans.
* 1 Gigabit Switch for message communication between the nodes in the local network.
* 1 Powerstation with 10 ports.
* 8 Gigabit Ethernet cables.
* 8 USB-C power cables.
   <div align=center><img src="https://github.com/Atlaszjr-star/HPC-RaspberryPi-Cluster/blob/main/figures/before.jpg" width="400px" />

## Technologies and Environment
## Setup master node
## Setup the whole cluster
## Introduction of Dataset
## Algorithm of Mobility Simulation
## Results
## Known Limitations
