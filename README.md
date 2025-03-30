# Fleet Management System with Multi-Robot Traffic Negotiation

<img src="./images/Fleet Management System 30-03-2025 21_53_35.png" width=700><br>

## 🚀 Overview
A Python-based simulation system for managing multiple autonomous robots navigating through warehouse environments with:
- Real-time traffic negotiation
- Collision avoidance
- Dynamic task assignment
- Battery management with charging stations

<img src="./images/level1.png" width=700><br>

## ✨ Features
- **3 Distinct Levels** with progressive difficulty
  - 🟢 Level 1: Basic Warehouse, Small network with 14 locations, 2 charging stations
  - 🟡 Level 2: Medium Facility, Medium network with 14 locations, 1 charging station 
  - 🔴 Level 3: Large Distribution Center, Medium network with 7 locations, 1 charging station 
- **Interactive GUI** with intuitive controls
- **Smart Robot Behaviors**:
  - Pathfinding with obstacle avoidance
  - Battery consumption/charging
  - Traffic deadlock resolution
- **Visualization Tools**:
  - Real-time robot tracking
  - Status indicators (moving, waiting, charging)
  - Conflict notifications

## Controls:

1. Click on vertices to spawn robots
2. Select a robot then click destination to assign tasks
3. Ctrl+D decreases selected robot's battery (for testing)
4. View real-time logs in logs/fleet_logs.txt

## 🗺️ Level Designs:

#### 1. Level 1 
<img src="./images/image_1.png" width=700><br>

#### 2. Level 2
<img src="./images/image_2.png" width=700><br>

#### 3. Level 3
<img src="./images/image_3.png" width=700><br>

## 🏗️ Project Structure
<img src="./images/projectstructure.png" width=700><br>


## Completed Features in Hackathon:
### 1. Visual Representation
✓ Environment Visualization:

Displayed all vertices (locations) and lanes clearly.
Marked locations with names and intersections.
Made vertices interactable (clickable) for spawning robots or assigning tasks.

✓ Robot Visualization:

  Used distinct colors/icons for robots.
  Implemented real-time movement visualization along lanes.
  Displayed robot statuses (moving, waiting, charging, task complete).

### 2. Robot Spawning
✓ Interactive GUI:

Enabled dynamic robot spawning by clicking vertices.
Assigned and displayed unique identifiers for each robot.

### 3. Navigation Task Assignment
✓ Interactive Task Assignment:

Allowed robot selection and destination assignment via clicks.
Robots started navigation immediately after task assignment.

### 4. Traffic Negotiation & Collision Avoidance
✓ Real-Time Traffic Management:

Implemented lane/intersection queuing to avoid collisions.
Visualized waiting status (e.g., color changes, icons).

### 5. Dynamic Interaction
✓ Runtime Flexibility:

Supported real-time robot spawning/task assignment without interrupting active robots.

### 6. Occupancy and Conflict Notifications
✓ User Alerts:

Provided visual/pop-up notifications for blocked paths/vertices.

### 7. Logging & Monitoring
✓ Detailed Logging:

Logged robot actions, paths, and statuses in fleet_logs.txt.


Bonus (If Applicable)
✓ Creative Enhancements:

[Specify any extra features, e.g., optimized pathfinding, priority lanes, etc.]


## 📦 Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fleet-management-system.git
   cd fleet-management-system

2. Install dependencies:
   ```bash
   pip install -r requirements.txt

## 🖥️ Usage
1. Run the main application::
   ```bash
   python main.py



## 🛠️ Customization
1. Add new levels by creating JSON files in data/ following the existing format
2. Modify robot behaviors in src/models/robot.py
3. Adjust simulation parameters:
    (a)Robot speed
    (b)Battery consumption rates
    

Developed with ❤️ by Laxman
