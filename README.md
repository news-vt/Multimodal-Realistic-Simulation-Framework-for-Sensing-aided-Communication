# Multimodal Realistic Simulation Framework for Sensing-Aided Communication 

This repository provides the code for a **multimodal realistic simulation framework** using **CARLA** and **MATLAB**. CARLA is used to generate realistic **autonomous driving sensor data**, while MATLAB is employed for **wireless communication simulations**. This framework enables **multimodal sensing data collection**, **3D digital reconstruction**, and **ray-tracing-based wireless channel modeling** to facilitate **beamforming and channel analysis**.  

---

## **🛠️ Workflow Overview**  
![Framework Overview](img/framework.png)

### **1️⃣ Environment Setup**  
- **Simulated urban scenarios** with multiple vehicles and base stations in CARLA.  
- Vehicles navigate autonomously, following road layouts and traffic signals.  
- Generates **realistic mobility patterns** and **dynamic sensing conditions** for beamforming and channel evaluation.  

### **2️⃣ Multimodal Sensing Data Generation**  
- At the base station, multiple sensors are deployed to collect multimodal data:  
  - **LiDAR**: Captures 3D point cloud data.  
  - **Radar**: Detects moving objects and their velocities.  
  - **RGB Cameras**: Provides visual scene understanding.  
- CARLA’s API is used to **synchronize sensor data** with vehicle movements and environmental factors.  

### **3️⃣ 3D Digital Reconstruction for Communication Simulation**  
- The **CARLA environment is imported into MATLAB** for wireless communication simulation.  
- Since CARLA and MATLAB use different map formats, we employ the **Blender API** for format conversion.  
- This ensures **geometric consistency** between the simulation environments, maintaining accuracy in wireless modeling.  

### **4️⃣ Wireless Channel Simulation with Ray Tracing**  
- The reconstructed 3D environment is used for **ray-tracing-based wireless channel simulations**.  
- **Beamforming impact on RSS (Received Signal Strength)** is analyzed by tracing signal paths and reflections.  
- Enables **precise evaluation of beam selection strategies** in complex urban environments.  

#### **📌 Key Features**  
✅ **Realistic multimodal sensing**: LiDAR, Radar, RGB Cameras integrated into an urban driving environment.  
✅ **Seamless 3D environment conversion**: CARLA to MATLAB using Blender API.  
✅ **Accurate wireless channel modeling**: Ray tracing for beamforming evaluation.  

---

## **📌 Requirements**  

- **OS**: Windows 10 / Linux (Ubuntu 18.04)  
- **CARLA Simulator**: Version **0.9.15** [(Download)](https://github.com/carla-simulator/carla/releases)  
- **MATLAB**: Version **R2024a**  
- **Python**: **3.7.12**  
- **Blender**: **4.2**  

---

## **📥 Installation**  

Clone the repository and install the required packages:  
```bash
git clone https://github.com/news-vt/Multimodal-Realistic-Simulation-Framework-for-Sensing-aided-Communication.git
cd your-repo
python -m pip install -r requirements.txt
```
You can verify that the installation was successful by running:  
```bash
python -c "import carla; print('CARLA successfully imported')"
```

---

## **🚀 Getting Started**

---

## **📊 Dataset**  
The dataset generated using this framework is available on **Kaggle**:  
🔗 [Multimodal Sensing Dataset for Beam Prediction](https://www.kaggle.com/datasets/whateveruwant/multimodal-sensing-dataset-for-beam-prediction)  

---

## **👥 Authors**

---

## **📝 Citation**

---

## **📚 References**

---