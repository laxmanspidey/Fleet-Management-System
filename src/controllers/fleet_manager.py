import logging
from src.controllers.traffic_manager import TrafficManager
from src.models.robot import Robot

class FleetManager:
    def __init__(self, nav_graph):
        self.nav_graph = nav_graph
        self.robots = []
        self.traffic_manager = TrafficManager()
        self.robot_counter = 0
        self.log_file = "fleet_logs.txt"
        
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def spawn_robot(self, vertex_idx):
        robot_id = self.robot_counter
        self.robot_counter += 1
        
        robot = Robot(robot_id, vertex_idx, self.nav_graph)
        self.robots.append(robot)
        self.traffic_manager.reserve_vertex(vertex_idx, robot_id)
        
        logging.info(f"Robot {robot_id} spawned at {self.nav_graph.get_vertex_name(vertex_idx)}")
        return robot
    
    def assign_task(self, robot_id, target_vertex):
        if robot_id < 0 or robot_id >= len(self.robots):
            return False, "Invalid robot ID"
        
        robot = self.robots[robot_id]
        success, message = robot.assign_task(target_vertex)
        
        if success:
            logging.info(f"Robot {robot_id} assigned task to {self.nav_graph.get_vertex_name(target_vertex)}")
        else:
            logging.warning(f"Failed to assign task to Robot {robot_id}: {message}")
        
        return success, message
    
    def update_robots(self):
        for robot in self.robots:
            robot.update(self.traffic_manager)
            
            while robot.log_queue:
                log_entry = robot.log_queue.pop(0)
                logging.info(log_entry)
    
    def get_robot_status(self, robot_id):
        if robot_id < 0 or robot_id >= len(self.robots):
            return None
        return self.robots[robot_id].status
    
    def get_robot_position(self, robot_id):
        if robot_id < 0 or robot_id >= len(self.robots):
            return None
        
        robot = self.robots[robot_id]
        
        if robot.current_lane is None:
            return self.nav_graph.vertices[robot.current_vertex]
        
        v1, v2 = robot.current_lane
        x1, y1 = self.nav_graph.vertices[v1]
        x2, y2 = self.nav_graph.vertices[v2]
        
        x = x1 + (x2 - x1) * robot.progress
        y = y1 + (y2 - y1) * robot.progress
        
        return (x, y)