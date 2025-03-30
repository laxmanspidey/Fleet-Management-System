import json
from queue import Queue

class NavGraph:
    def __init__(self, json_file):
        with open(json_file) as f:
            data = json.load(f)
        
        level_name = next(iter(data['levels']))
        level_data = data['levels'][level_name]
        
        self.vertices = []
        self.vertex_data = []
        self.chargers = []
        
        # Process vertices
        for idx, vertex in enumerate(level_data['vertices']):
            x, y, attributes = vertex
            self.vertices.append((x, y))
            self.vertex_data.append({
                'name': attributes.get('name', f'V{idx}'),
                'is_charger': attributes.get('is_charger', False),
                'index': idx
            })
            if attributes.get('is_charger', False):
                self.chargers.append(idx)
        
        # Process lanes (bidirectional)
        self.lanes = set()
        for lane in level_data['lanes']:
            v1, v2, _ = lane
            self.lanes.add((v1, v2))
            self.lanes.add((v2, v1))
        
        # Create adjacency list
        self.adjacency = {i: [] for i in range(len(self.vertices))}
        for v1, v2 in self.lanes:
            self.adjacency[v1].append(v2)
        
        # Calculate bounds for scaling
        self.min_x = min(v[0] for v in self.vertices)
        self.max_x = max(v[0] for v in self.vertices)
        self.min_y = min(v[1] for v in self.vertices)
        self.max_y = max(v[1] for v in self.vertices)
    
    def get_vertex_name(self, idx):
        return self.vertex_data[idx]['name']
    
    def is_charger(self, idx):
        return self.vertex_data[idx]['is_charger']
    
    def find_shortest_path(self, start, end, blocked_lanes=None, blocked_vertices=None):
        """Find shortest path using BFS, avoiding blocked lanes and vertices"""
        if start == end:
            return [start]
        
        blocked_lanes = blocked_lanes or set()
        blocked_vertices = blocked_vertices or set()
        
        visited = {start}
        queue = Queue()
        queue.put((start, [start]))
        
        while not queue.empty():
            current, path = queue.get()
            
            for neighbor in self.adjacency[current]:
                # Skip blocked lanes and vertices
                if (current, neighbor) in blocked_lanes or (neighbor, current) in blocked_lanes:
                    continue
                if neighbor in blocked_vertices:
                    continue
                
                if neighbor == end:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.put((neighbor, path + [neighbor]))
        
        return None  # No path found
    
    def find_nearest_charger(self, start, blocked_lanes=None, blocked_vertices=None):
        """Find the nearest charger with a valid path"""
        blocked_lanes = blocked_lanes or set()
        blocked_vertices = blocked_vertices or set()
        
        # BFS to find nearest charger
        visited = {start}
        queue = Queue()
        queue.put((start, [start]))
        
        while not queue.empty():
            current, path = queue.get()
            
            # Check if current vertex is a charger (and not blocked)
            if (self.is_charger(current) and 
                current not in blocked_vertices and
                not any((path[i], path[i+1]) in blocked_lanes for i in range(len(path)-1))):
                return current, path
            
            for neighbor in self.adjacency[current]:
                # Skip blocked lanes and vertices
                if (current, neighbor) in blocked_lanes or (neighbor, current) in blocked_lanes:
                    continue
                if neighbor in blocked_vertices:
                    continue
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.put((neighbor, path + [neighbor]))
        
        return None, None  # No charger found