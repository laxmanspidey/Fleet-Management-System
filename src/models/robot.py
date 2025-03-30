import time
from datetime import datetime

# Constants
ROBOT_COLORS = ['red', 'blue', 'green', 'purple', 'orange', 'cyan', 'magenta', 'yellow']
ROBOT_SPEED = 0.1
ROBOT_WAIT_TIME = 2  # seconds to wait at intersections
BATTERY_DRAIN_RATE = 1    # % per movement
BATTERY_CHARGE_RATE = 2   # % per charge cycle
LOW_BATTERY_THRESHOLD = 20
CRITICAL_BATTERY = 5
CHARGE_COMPLETE_THRESHOLD = 95
MAX_PATH_RETRIES = 3  # Maximum attempts to find an alternative path
EMERGENCY_PATH_ATTEMPTS = 5  # Attempts to find path to any charger

class Robot:
    def __init__(self, robot_id, start_vertex, nav_graph):
        self.id = robot_id
        self.color = ROBOT_COLORS[robot_id % len(ROBOT_COLORS)]
        self.nav_graph = nav_graph
        self.current_vertex = start_vertex
        self.target_vertex = None
        self.path = []
        self.status = "idle"
        self.progress = 0
        self.current_lane = None
        self.wait_until = 0
        self.log_queue = []
        self.battery = 100  # Start with full battery
        self.emergency_charge_requested = False
        self.charge_progress = 0  # For charging animation
        self.waiting_reason = ""  # Track why robot is waiting
        self.path_attempts = 0    # Track attempts to find alternative paths
        self.emergency_path_attempts = 0  # Track attempts to find emergency paths
        
        self.log(f"Robot {self.id} spawned at {self.nav_graph.get_vertex_name(start_vertex)}")

    def decrease_battery(self, amount):
        """Manually reduce battery level for testing"""
        self.battery = max(0, self.battery - amount)
        if self.battery <= LOW_BATTERY_THRESHOLD and not self.emergency_charge_requested:
            self.log(f"Battery manually reduced to {self.battery}%")
    
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_queue.append(f"{timestamp} - {message}")
    
    def assign_task(self, target_vertex):
        if self.status == "charging":
            return False, "Robot is currently charging"
        if self.battery <= CRITICAL_BATTERY:
            return False, f"Critical battery ({self.battery}%), cannot assign tasks"
            
        if target_vertex == self.current_vertex:
            return False, "Robot is already at target location"
            
        path = self.nav_graph.find_shortest_path(self.current_vertex, target_vertex)
        if not path:
            return False, "No valid path to target"
            
        self.target_vertex = target_vertex
        self.path = path
        self.status = "moving"
        self.progress = 0
        self.current_lane = None
        self.emergency_charge_requested = False
        self.path_attempts = 0
        self.emergency_path_attempts = 0
        
        self.log(f"Assigned task: move to {self.nav_graph.get_vertex_name(target_vertex)}")
        return True, "Task assigned successfully"

    def find_alternative_path(self, traffic_manager):
        """Find an alternative path avoiding blocked lanes and vertices"""
        blocked_lanes = traffic_manager.get_blocked_lanes_for_robot(self.id)
        blocked_vertices = traffic_manager.get_blocked_vertices_for_robot(self.id)
        
        # Remove our current vertex from blocked vertices (we're already here)
        blocked_vertices.discard(self.current_vertex)
        
        # Try to find a path avoiding blocked resources
        new_path = self.nav_graph.find_shortest_path(
            self.current_vertex,
            self.target_vertex,
            blocked_lanes,
            blocked_vertices
        )
        
        if new_path:
            self.path = new_path
            self.path_attempts += 1
            self.log(f"Found alternative path (attempt {self.path_attempts}) to {self.nav_graph.get_vertex_name(self.target_vertex)}")
            return True
        return False

    def update(self, traffic_manager):
        # Handle charging when explicitly sent to charger as final destination
        if (self.status == "moving" and 
            not self.path and  # No more path remaining
            self.current_vertex == self.target_vertex and
            self.nav_graph.is_charger(self.current_vertex)):
            
            self.status = "charging"
            self.charge_progress = 0
            self.log(f"Started charging at {self.nav_graph.get_vertex_name(self.current_vertex)}")
            return

        # Handle ongoing charging process
        if self.status == "charging":
            self.battery = min(100, self.battery + BATTERY_CHARGE_RATE)
            self.charge_progress = (self.battery / CHARGE_COMPLETE_THRESHOLD) * 100
            
            if self.battery >= CHARGE_COMPLETE_THRESHOLD:
                self.status = "idle"
                self.charge_progress = 0
                self.log(f"Charging complete at {self.nav_graph.get_vertex_name(self.current_vertex)} (Battery: {self.battery}%)")
            return

        # Automatic emergency charging for low battery
        if not self.emergency_charge_requested and self.battery <= LOW_BATTERY_THRESHOLD:
            self.request_emergency_charge(traffic_manager)
            return

        # Safety check for critical battery
        if self.battery <= CRITICAL_BATTERY and self.status != "disabled":
            self.status = "disabled"
            self.log(f"Robot disabled due to critical battery ({self.battery}%)")
            return

        # State checks for non-moving robots
        if self.status in ["idle", "complete", "disabled"]:
            return

        # Handle waiting state
        if self.status == "waiting":
            if time.time() > self.wait_until:
                self.status = "moving"
                traffic_manager.remove_waiting_robot(self.current_vertex, self.id)
                self.log(f"Resumed moving after waiting at {self.nav_graph.get_vertex_name(self.current_vertex)}")
            return

        # Handle path completion
        if not self.path:
            if self.current_vertex == self.target_vertex:
                self.status = "complete"
                self.log(f"Task completed at {self.nav_graph.get_vertex_name(self.current_vertex)}")
            else:
                self.status = "idle"
            return

        # Normal movement processing
        next_vertex = self.path[0]
        
        # Check vertex occupancy before moving
        if traffic_manager.is_vertex_occupied(next_vertex, self.id):
            # For emergency charging, try harder to find alternative paths
            if self.emergency_charge_requested and self.emergency_path_attempts < EMERGENCY_PATH_ATTEMPTS:
                if self.find_alternative_emergency_path(traffic_manager):
                    return  # Found new path
                
            # For normal movement, try to find alternative path
            elif self.path_attempts < MAX_PATH_RETRIES and self.find_alternative_path(traffic_manager):
                return  # Found new path
            
            # If no alternative path found, wait
            self.status = "waiting"
            self.wait_until = time.time() + ROBOT_WAIT_TIME
            traffic_manager.add_waiting_robot(self.current_vertex, self.id)
            traffic_manager.add_conflict(f"Robot {self.id} waiting at vertex {self.current_vertex}")
            self.log(f"Waiting at {self.nav_graph.get_vertex_name(self.current_vertex)} due to vertex conflict")
            return
            
        if self.current_lane is None:
            self.current_lane = (self.current_vertex, next_vertex)
            # Battery drain only when starting new movement segment
            self.battery = max(0, self.battery - BATTERY_DRAIN_RATE)
            if self.battery <= LOW_BATTERY_THRESHOLD and not self.emergency_charge_requested:
                traffic_manager.add_conflict(f"Robot {self.id} low battery! ({self.battery}%)")
            if self.battery <= CRITICAL_BATTERY:
                self.status = "disabled"
                self.log(f"Robot disabled due to critical battery ({self.battery}%)")
                return
            self.log(f"Started moving from {self.nav_graph.get_vertex_name(self.current_vertex)} to {self.nav_graph.get_vertex_name(next_vertex)} (Battery: {self.battery}%)")
        
        # Handle lane occupancy
        if traffic_manager.is_lane_occupied(self.current_lane, self.id):
            # For emergency charging, try harder to find alternative paths
            if self.emergency_charge_requested and self.emergency_path_attempts < EMERGENCY_PATH_ATTEMPTS:
                if self.find_alternative_emergency_path(traffic_manager):
                    return  # Found new path
                
            # For normal movement, try to find alternative path
            elif self.path_attempts < MAX_PATH_RETRIES and self.find_alternative_path(traffic_manager):
                return  # Found new path
            
            # If no alternative path found, wait
            self.status = "waiting"
            self.wait_until = time.time() + ROBOT_WAIT_TIME
            traffic_manager.add_waiting_robot(self.current_vertex, self.id)
            traffic_manager.add_conflict(f"Robot {self.id} waiting on lane {self.current_lane}")
            self.log(f"Waiting at {self.nav_graph.get_vertex_name(self.current_vertex)} due to lane conflict")
            return
        
        # Reserve resources and move
        traffic_manager.reserve_lane(self.current_lane, self.id)
        traffic_manager.reserve_vertex(next_vertex, self.id)
        
        self.progress += ROBOT_SPEED
        if self.progress >= 1:
            self.progress = 0
            traffic_manager.release_vertex(self.current_vertex, self.id)
            self.current_vertex = next_vertex
            self.path.pop(0)
            traffic_manager.release_lane(self.current_lane, self.id)
            self.current_lane = None
            self.waiting_reason = ""
            self.path_attempts = 0  # Reset attempts when we successfully move
            self.emergency_path_attempts = 0
            
            # Final destination check
            if not self.path and self.current_vertex == self.target_vertex:
                self.status = "complete"
                self.log(f"Task completed at {self.nav_graph.get_vertex_name(self.current_vertex)}")

    def find_alternative_emergency_path(self, traffic_manager):
        """Special path finding for emergency charging that tries all chargers"""
        blocked_lanes = traffic_manager.get_blocked_lanes_for_robot(self.id)
        blocked_vertices = traffic_manager.get_blocked_vertices_for_robot(self.id)
        
        # Remove our current vertex from blocked vertices (we're already here)
        blocked_vertices.discard(self.current_vertex)
        
        # Try to find path to any charger
        nearest_charger, path = self.nav_graph.find_nearest_charger(
            self.current_vertex,
            blocked_lanes,
            blocked_vertices
        )
        
        if path:
            self.target_vertex = nearest_charger
            self.path = path
            self.emergency_path_attempts += 1
            self.log(f"Found emergency path (attempt {self.emergency_path_attempts}) to charger at {self.nav_graph.get_vertex_name(nearest_charger)}")
            return True
        
        return False

    def request_emergency_charge(self, traffic_manager):
        """Find nearest charger and navigate to it"""
        self.emergency_charge_requested = True
        
        # Check if we're already at a charger
        if self.nav_graph.is_charger(self.current_vertex):
            self.status = "charging"
            self.charge_progress = 0
            self.log(f"Low battery! Started charging at {self.nav_graph.get_vertex_name(self.current_vertex)}")
            return

        # Find nearest charger with path
        blocked_lanes = traffic_manager.get_blocked_lanes_for_robot(self.id)
        blocked_vertices = traffic_manager.get_blocked_vertices_for_robot(self.id)
        
        nearest_charger, path = self.nav_graph.find_nearest_charger(
            self.current_vertex,
            blocked_lanes,
            blocked_vertices
        )

        if nearest_charger is not None:
            self.target_vertex = nearest_charger
            self.path = path
            self.status = "moving"
            self.progress = 0
            self.current_lane = None
            self.path_attempts = 0
            self.emergency_path_attempts = 0
            traffic_manager.add_conflict(f"Robot {self.id} emergency routing to charger (Battery: {self.battery}%)")
            self.log(f"Low battery! Redirecting to charger at {self.nav_graph.get_vertex_name(nearest_charger)}")
        else:
            self.status = "disabled"
            traffic_manager.add_conflict(f"Robot {self.id} disabled - no charger available!")
            self.log(f"Critical battery! No charger available (Battery: {self.battery}%)")