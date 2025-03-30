import threading
import time

class TrafficManager:
    def __init__(self):
        self.occupied_lanes = {}
        self.occupied_vertices = {}  # Track vertex occupancy
        self.waiting_robots = {}     # Robots waiting at vertices
        self.lock = threading.Lock()
        self.conflicts = []          # Track current conflicts
        self.blocked_paths = {}      # Track blocked paths for robots
    
    def is_lane_occupied(self, lane, requesting_robot=None):
        with self.lock:
            if lane in self.occupied_lanes:
                return self.occupied_lanes[lane] != requesting_robot
            return False
    
    def is_vertex_occupied(self, vertex_id, requesting_robot=None):
        with self.lock:
            if vertex_id in self.occupied_vertices:
                return self.occupied_vertices[vertex_id] != requesting_robot
            return False
    
    def reserve_lane(self, lane, robot_id):
        with self.lock:
            self.occupied_lanes[lane] = robot_id
    
    def reserve_vertex(self, vertex_id, robot_id):
        with self.lock:
            self.occupied_vertices[vertex_id] = robot_id
    
    def release_lane(self, lane, robot_id):
        with self.lock:
            if lane in self.occupied_lanes and self.occupied_lanes[lane] == robot_id:
                del self.occupied_lanes[lane]
    
    def release_vertex(self, vertex_id, robot_id):
        with self.lock:
            if vertex_id in self.occupied_vertices and self.occupied_vertices[vertex_id] == robot_id:
                del self.occupied_vertices[vertex_id]
    
    def add_waiting_robot(self, vertex_id, robot_id):
        with self.lock:
            if vertex_id not in self.waiting_robots:
                self.waiting_robots[vertex_id] = []
            self.waiting_robots[vertex_id].append(robot_id)
    
    def remove_waiting_robot(self, vertex_id, robot_id):
        with self.lock:
            if vertex_id in self.waiting_robots and robot_id in self.waiting_robots[vertex_id]:
                self.waiting_robots[vertex_id].remove(robot_id)
    
    def add_conflict(self, message):
        with self.lock:
            self.conflicts.append((time.time(), message))
    
    def get_conflicts(self):
        with self.lock:
            return [msg for (t, msg) in self.conflicts if time.time() - t < 5]  # Show conflicts for 5 seconds
    
    def get_blocked_lanes_for_robot(self, robot_id):
        """Get all lanes blocked by other robots"""
        with self.lock:
            return {lane for lane, occupier in self.occupied_lanes.items() if occupier != robot_id}
    
    def get_blocked_vertices_for_robot(self, robot_id):
        """Get all vertices blocked by other robots"""
        with self.lock:
            return {vertex for vertex, occupier in self.occupied_vertices.items() if occupier != robot_id}