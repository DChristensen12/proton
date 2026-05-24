# PROTON

Physics-informed Radiation Operator and Time-series Optimized Network. This is a distributed scientific machine learning framework integrating physics-informed neural networks, stochastic quantum diffusion modeling, and spatiotemporal Fourier Neural Operators across a live ESP32 edge sensor mesh.

## Project Overview

This repository will host a distributed scientific machine learning framework designed to map space weather patterns and atmospheric cosmic ray transport. Instead of running calculations on decoupled simulations, PROTON handles continuous real-time data ingress from local hardware sensors and uses three distinct mathematical architectures to model, generate, and map physical particle fields.

The system leverages a centralized high-performance computing node (my local laptop) to handle the heavy neural tensor operations, while low-power microcontrollers act as a distributed network array to pipe spatial coordinates across a home network.

---

## Hardware Architecture

The physical system consists of a primary radiation instrument acting as a ground truth baseline, connected alongside a decentralized sensor array:

* **Primary Sensor Node:** FNIRSI GC-01 Geiger Counter running open-source Rad Pro firmware to expose its raw telemetry.
* **Data Ingress Pipeline:** High-speed USB-C to USB-A data interface operating at a 115200-baud serial communication rate.
* **Distributed Spatial Mesh Nodes:** Three ESP32 development boards configured as wireless edge devices communicating over a local Wi-Fi protocol.

---

## Mathematical and Machine Learning Framework

The codebase operates across three distinct mathematical modules to process the data stream:

### 1. 1D Physics-Informed Neural Network (PINN)

The initial module handles localized edge inference using continuous stream values from the primary sensor. We use PyTorch and its automatic differentiation engine (`torch.autograd`) to enforce known physics constraints directly into the loss function of the model.

Instead of tracking arbitrary numerical patterns, the network is restricted by the 1D Boltzmann transport equation and atmospheric attenuation parameters:

$$Loss = Loss_{Data} + \lambda Loss_{Physics}$$

### 2. Quantum-Driven Generative Diffusion Model

Nuclear decay and cosmic background strikes represent a true quantum Poisson process. This module extracts the exact inter-arrival timestamps ($\Delta t$) between individual high-energy particle collisions.

We implement a continuous-time autoregressive diffusion model that learns to reverse standard Gaussian noise profiles back into the non-Gaussian quantum uncertainty signatures unique to our local background radiation envelope. This allows us to generate infinite synthetic space weather tracks grounded in real physical distributions.

### 3. Spatiotemporal Fourier Neural Operator (FNO)

The final module expands the project into multi-dimensional spatial mapping. The three wireless ESP32 nodes stream coordinate data over a local MQTT broker to simulate high-altitude data collection profiles.

The framework processes these functional inputs using a Fourier Neural Operator. By applying Fast Fourier Transforms (FFTs), the model maps the inputs into the frequency domain, solves the continuous partial differential equations governing regional radiation transport, and projects an instantaneous 3D geographic space weather grid.

This project is a word in progress and will be updated throughout the year! Stay tuned!
