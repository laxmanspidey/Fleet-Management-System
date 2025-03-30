# Fleet Management System with Multi-Robot Traffic Negotiation

![System Demo](demo.gif) <!-- Add a demo gif if available -->

## 🚀 Overview
A Python-based simulation system for managing multiple autonomous robots navigating through warehouse environments with:
- Real-time traffic negotiation
- Collision avoidance
- Dynamic task assignment
- Battery management with charging stations

## ✨ Features
- **3 Distinct Levels** with progressive difficulty
  - 🟢 Training Grounds (Beginner)
  - 🟡 Distribution Hub (Intermediate)
  - 🔴 Megawarehouse (Advanced)
- **Interactive GUI** with intuitive controls
- **Smart Robot Behaviors**:
  - Pathfinding with obstacle avoidance
  - Battery consumption/charging
  - Traffic deadlock resolution
- **Visualization Tools**:
  - Real-time robot tracking
  - Status indicators (moving, waiting, charging)
  - Conflict notifications

## 📦 Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fleet-management-system.git
   cd fleet-management-system

2. Install dependencies:
   ```bash
   pip install -r requirements.txt

## 🖥️ Usage
Run the main application:
    ```bash
    python main.py
  

## Controls:

1. Click on vertices to spawn robots
2. Select a robot then click destination to assign tasks
3. Ctrl+D decreases selected robot's battery (for testing)
4. View real-time logs in logs/fleet_logs.txt


## 🗺️ Level Designs
Level 1: 
Level 2:
Level 3:


🏗️ Project Structure
  
Copy
fleet_management_system/
├── data/               # Navigation graph datasets
├── src/
│   ├── models/         # Data models (Robots, Navigation)
│   ├── controllers/    # System logic (Traffic, Fleet)
│   ├── gui/            # User interface components
│   └── utils/          # Helper functions
├── logs/               # System operation logs
├── assets/             # Visual assets
├── main.py             # Application entry point
└── requirements.txt    # Dependencies


🛠️ Customization
Add new levels by creating JSON files in data/ following the existing format

Modify robot behaviors in src/models/robot.py

Adjust simulation parameters:

Robot speed

Battery consumption rates

Charging speeds

Developed with ❤️ by Laxman
