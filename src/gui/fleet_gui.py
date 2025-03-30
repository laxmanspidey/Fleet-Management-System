from src.models.nav_graph import NavGraph
from src.controllers.fleet_manager import FleetManager
from src.controllers.traffic_manager import TrafficManager
LOW_BATTERY_THRESHOLD = 20
CRITICAL_BATTERY = 5

import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os

# Constants
ROBOT_RADIUS = 10
VERTEX_RADIUS = 8
LANE_WIDTH = 2
UPDATE_INTERVAL = 100  # ms

# Color scheme
COLORS = {
    'background': '#2D3748',
    'primary': '#4299E1',
    'secondary': '#2C5282',
    'accent': '#38B2AC',
    'text': '#E2E8F0',
    'error': '#F56565',
    'success': '#48BB78',
    'warning': '#ED8936',
    'dark_bg': '#1A202C',
    'light_bg': '#4A5568'
}

class FleetGUI:
    def __init__(self, master, nav_graph_file=None):
        self.master = master
        self.nav_graph_file = nav_graph_file
        self.running = True
        self.update_id = None
        
        # Initialize the appropriate screen
        if nav_graph_file is None:
            self.show_home_screen()
        else:
            self.initialize_simulation_screen()
    
    def initialize_simulation_screen(self):
        """Initialize the simulation screen with the given nav graph"""
        # Clear any existing widgets
        for widget in self.master.winfo_children():
            widget.destroy()
        
        try:
            self.nav_graph = NavGraph(self.nav_graph_file)
            self.fleet_manager = FleetManager(self.nav_graph)
            
            # Main container
            self.main_container = tk.Frame(self.master, bg=COLORS['background'])
            self.main_container.pack(fill=tk.BOTH, expand=True)
            
            # Control frame at top
            self.control_frame = tk.Frame(
                self.main_container, 
                bg=COLORS['dark_bg'],
                padx=10,
                pady=5
            )
            self.control_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Back to home button
            self.back_btn = tk.Button(
                self.control_frame,
                text="← Home",
                command=self.show_home_screen,
                bg=COLORS['secondary'],
                fg=COLORS['text'],
                activebackground=COLORS['primary'],
                relief='flat',
                borderwidth=0,
                padx=10,
                font=('Arial', 10, 'bold')
            )
            self.back_btn.pack(side=tk.LEFT, padx=5)
            
            # Clear selection button
            self.clear_selection_btn = tk.Button(
                self.control_frame,
                text="Clear Selection",
                command=self.clear_selection,
                bg=COLORS['accent'],
                fg='white',
                activebackground='#2C7A7B',
                relief='flat',
                borderwidth=0,
                padx=10,
                font=('Arial', 10)
            )
            self.clear_selection_btn.pack(side=tk.LEFT, padx=5)
            
            # Conflict display
            self.conflict_var = tk.StringVar()
            self.conflict_label = tk.Label(
                self.control_frame,
                textvariable=self.conflict_var,
                fg=COLORS['error'],
                bg=COLORS['dark_bg'],
                anchor='w',
                font=('Arial', 9, 'bold')
            )
            self.conflict_label.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)
            
            # Status frame below controls
            self.status_frame = tk.Frame(
                self.main_container,
                bg=COLORS['dark_bg'],
                padx=10,
                pady=5
            )
            self.status_frame.pack(fill=tk.X, padx=5, pady=5)
            
            self.status_label = tk.Label(
                self.status_frame,
                text="Ready",
                anchor='w',
                bg=COLORS['dark_bg'],
                fg=COLORS['text'],
                font=('Arial', 10)
            )
            self.status_label.pack(fill=tk.X)
            
            self.selected_robot_var = tk.StringVar()
            self.selected_robot_var.set("No robot selected")
            self.robot_label = tk.Label(
                self.status_frame,
                textvariable=self.selected_robot_var,
                anchor='w',
                bg=COLORS['dark_bg'],
                fg=COLORS['text'],
                font=('Arial', 10, 'bold')
            )
            self.robot_label.pack(fill=tk.X)
            
            # Canvas with scrollbars
            self.canvas_frame = tk.Frame(
                self.main_container,
                bg=COLORS['dark_bg']
            )
            self.canvas_frame.pack(fill=tk.BOTH, expand=True)
            
            self.vscroll = ttk.Scrollbar(
                self.canvas_frame,
                orient=tk.VERTICAL
            )
            self.vscroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            self.hscroll = ttk.Scrollbar(
                self.canvas_frame,
                orient=tk.HORIZONTAL
            )
            self.hscroll.pack(side=tk.BOTTOM, fill=tk.X)
            
            self.canvas = tk.Canvas(
                self.canvas_frame,
                width=800,
                height=600,
                bg=COLORS['light_bg'],
                xscrollcommand=self.hscroll.set,
                yscrollcommand=self.vscroll.set,
                scrollregion=(0, 0, 2000, 2000),
                highlightthickness=0
            )
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            self.hscroll.config(command=self.canvas.xview)
            self.vscroll.config(command=self.canvas.yview)
            
            # State variables
            self.selected_robot = None
            self.selected_vertex = None
            self.scale_factor = 40
            self.offset_x = 100
            self.offset_y = 100
            
            # Setup display
            self.setup_display()
            
            # Bind events
            self.canvas.bind("<Button-1>", self.on_canvas_click)
            # Bind keyboard shortcut (Ctrl+D) to decrease battery
            self.master.bind('<Control-d>', self.decrease_selected_robot_battery)
            # Start update loop
            self.start_update_loop()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize simulation: {str(e)}")
            self.show_home_screen()
    
    def start_update_loop(self):
        """Start the update loop for the simulation"""
        if self.update_id:
            self.master.after_cancel(self.update_id)
        self.running = True
        self.update()
    
    def stop_update_loop(self):
        """Stop the update loop"""
        self.running = False
        if self.update_id:
            self.master.after_cancel(self.update_id)
            self.update_id = None
    
    def show_home_screen(self):
        """Show the home screen with dataset selection"""
        # Stop any running simulation updates
        self.stop_update_loop()
        
        # Clear any existing widgets
        for widget in self.master.winfo_children():
            widget.destroy()
        
        # Create canvas for background
        self.home_canvas = tk.Canvas(
            self.master,
            width=self.master.winfo_screenwidth(),
            height=self.master.winfo_screenheight(),
            highlightthickness=0,
            bg=COLORS['background']  # Fallback background color
        )
        self.home_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Load and resize background image
        try:
            # Get the absolute path to the image
            image_path = os.path.join(os.path.dirname(__file__), "robotimg.jpg")
            
            # Open and resize image
            pil_image = Image.open(image_path)
            
            # Get screen dimensions
            screen_width = self.master.winfo_width() or 1200  # Default if not yet visible
            screen_height = self.master.winfo_height() or 800
            
            # Calculate aspect ratios
            img_width, img_height = pil_image.size
            screen_ratio = screen_width / screen_height
            img_ratio = img_width / img_height
            
            # Resize image to cover screen while maintaining aspect ratio
            if img_ratio > screen_ratio:
                # Image is wider than screen
                new_height = screen_height
                new_width = int(img_width * (screen_height / img_height))
            else:
                # Image is taller than screen
                new_width = screen_width
                new_height = int(img_height * (screen_width / img_width))
                
            pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(pil_image)
            
            # Create background image covering entire canvas
            self.home_canvas.create_image(
                screen_width//2, 
                screen_height//2, 
                image=self.bg_image, 
                anchor=tk.CENTER
            )
            
        except Exception as e:
            print(f"Error loading background image: {e}")
            # Fallback to solid color background (already set)
        
        # Create overlay frame (without alpha transparency)
        overlay = tk.Frame(
            self.home_canvas,
            bg=COLORS['dark_bg'],  # Use solid color instead of alpha
            bd=0,
            relief='flat'
        )
        overlay.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=600, height=500)
        
        # Title
        title_label = tk.Label(
            overlay,
            text="Fleet Management System",
            font=('Arial', 24, 'bold'),
            fg=COLORS['text'],
            bg=COLORS['dark_bg'],
            pady=20
        )
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(
            overlay,
            text="Select a Level to Start Simulation",
            font=('Arial', 14),
            fg=COLORS['text'],
            bg=COLORS['dark_bg'],
            pady=10
        )
        subtitle_label.pack()
        
        # Button frame
        button_frame = tk.Frame(
            overlay,
            bg=COLORS['dark_bg'],
            pady=30
        )
        button_frame.pack()
        
        # Dataset buttons
        datasets = [
            ("Level 1 ", r"C:\Users\Laxman Spidey\OneDrive\Desktop\djangorest\roboot\fleet_management_system\data\nav_graph_1.json"),
            ("Level 2 ", r"C:\Users\Laxman Spidey\OneDrive\Desktop\djangorest\roboot\fleet_management_system\data\nav_graph_2.json"),
            ("Level 3 ", r"C:\Users\Laxman Spidey\OneDrive\Desktop\djangorest\roboot\fleet_management_system\data\nav_graph_3.json")
        ]
        
        for text, file in datasets:
            btn = tk.Button(
                button_frame,
                text=text,
                command=lambda f=file: self.load_dataset(f),
                bg=COLORS['primary'],
                fg='white',
                activebackground=COLORS['secondary'],
                relief='flat',
                borderwidth=0,
                padx=20,
                pady=10,
                font=('Arial', 12),
                width=25
            )
            btn.pack(pady=10)
        
        # Footer
        footer_label = tk.Label(
            overlay,
            text="Developed by Laxman",
            font=('Arial', 10),
            fg=COLORS['text'],
            bg=COLORS['dark_bg'],
            pady=20
        )
        footer_label.pack(side=tk.BOTTOM)
    
    def load_dataset(self, filename):
        """Load a dataset and show the visualization screen"""
        try:
            self.nav_graph_file = filename
            self.initialize_simulation_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dataset: {str(e)}")
            self.show_home_screen()
    
    def decrease_selected_robot_battery(self, event=None):
        """Decrease selected robot's battery by 10%"""
        if self.selected_robot is not None:
            robot = self.fleet_manager.robots[self.selected_robot]
            robot.decrease_battery(10)  # Decrease by 10%
            self.update_status(f"Robot {robot.id} battery decreased to {robot.battery}%")
            self.draw_graph()
    
    def setup_display(self):
        graph_width = self.nav_graph.max_x - self.nav_graph.min_x
        graph_height = self.nav_graph.max_y - self.nav_graph.min_y
        
        scaled_width = graph_width * self.scale_factor + 2 * self.offset_x
        scaled_height = graph_height * self.scale_factor + 2 * self.offset_y
        self.canvas.config(scrollregion=(-self.offset_x, -self.offset_y, scaled_width, scaled_height))
        
        self.canvas.xview_moveto(0.5)
        self.canvas.yview_moveto(0.5)
    
    def scale_point(self, x, y):
        canvas_x = (x - self.nav_graph.min_x) * self.scale_factor + self.offset_x
        canvas_y = (y - self.nav_graph.min_y) * self.scale_factor + self.offset_y
        return canvas_x, canvas_y
    
    def draw_graph(self):
        if not hasattr(self, 'canvas'):
            return
            
        try:
            self.canvas.delete("all")
            
            # Draw lanes
            for v1, v2 in self.nav_graph.lanes:
                x1, y1 = self.nav_graph.vertices[v1]
                x2, y2 = self.nav_graph.vertices[v2]
                
                canvas_x1, canvas_y1 = self.scale_point(x1, y1)
                canvas_x2, canvas_y2 = self.scale_point(x2, y2)
                
                self.canvas.create_line(
                    canvas_x1, canvas_y1, canvas_x2, canvas_y2,
                    fill='#718096', width=LANE_WIDTH, tags="lane"
                )
            
            # Draw vertices
            for idx, (x, y) in enumerate(self.nav_graph.vertices):
                canvas_x, canvas_y = self.scale_point(x, y)
                vertex_data = self.nav_graph.vertex_data[idx]
                
                fill_color = '#38B2AC' if vertex_data['is_charger'] else '#4A5568'
                outline_color = '#F56565' if idx == self.selected_vertex else '#E2E8F0'
                outline_width = 3 if idx == self.selected_vertex else 2
                
                self.canvas.create_oval(
                    canvas_x - VERTEX_RADIUS, canvas_y - VERTEX_RADIUS,
                    canvas_x + VERTEX_RADIUS, canvas_y + VERTEX_RADIUS,
                    fill=fill_color, outline=outline_color, width=outline_width,
                    tags=f"vertex_{idx}"
                )
                
                display_text = vertex_data.get('name', str(idx))
                self.canvas.create_text(
                    canvas_x, canvas_y - VERTEX_RADIUS - 15,
                    text=display_text,
                    fill=COLORS['text'], font=('Arial', 9, 'bold'),
                    tags=f"vertex_label_{idx}"
                )
            
            # Draw robots
            for robot in self.fleet_manager.robots:
                pos = self.fleet_manager.get_robot_position(robot.id)
                if pos is None:
                    continue
                    
                x, y = pos
                canvas_x, canvas_y = self.scale_point(x, y)
                
                # Robot body
                outline_color = '#F6E05E' if robot.id == self.selected_robot else robot.color
                outline_width = 3 if robot.id == self.selected_robot else 1
                
                self.canvas.create_oval(
                    canvas_x - ROBOT_RADIUS, canvas_y - ROBOT_RADIUS,
                    canvas_x + ROBOT_RADIUS, canvas_y + ROBOT_RADIUS,
                    fill=robot.color, outline=outline_color, width=outline_width,
                    tags=f"robot_{robot.id}"
                )
                
                # Robot ID
                self.canvas.create_text(
                    canvas_x, canvas_y,
                    text=str(robot.id),
                    fill='white', font=('Arial', 8, 'bold'), 
                    tags=f"robot_label_{robot.id}"
                )
                
                # Status indicator
                status_x = canvas_x
                status_y = canvas_y + ROBOT_RADIUS + 15
                
                status_color = {
                    'idle': '#A0AEC0',
                    'moving': '#48BB78',
                    'waiting': '#ED8936',
                    'charging': '#4299E1',
                    'complete': '#9F7AEA',
                    'disabled': '#F56565'
                }.get(robot.status, '#000000')
                
                self.canvas.create_oval(
                    status_x - 5, status_y - 5,
                    status_x + 5, status_y + 5,
                    fill=status_color, outline='white', width=1,
                    tags=f"robot_status_{robot.id}"
                )
                
                # Battery status
                battery_text = f"{robot.battery}%"
                battery_color = ("#48BB78" if robot.battery > LOW_BATTERY_THRESHOLD 
                                else "#ED8936" if robot.battery > CRITICAL_BATTERY 
                                else "#F56565")
                
                self.canvas.create_text(
                    canvas_x, canvas_y + ROBOT_RADIUS + 30,
                    text=battery_text,
                    fill=battery_color,
                    font=('Arial', 8, 'bold'),
                    tags=f"robot_battery_{robot.id}"
                )
                
                # Waiting text (if waiting)
                if robot.status == "waiting":
                    self.canvas.create_text(
                        canvas_x, canvas_y + ROBOT_RADIUS + 50,
                        text="Waiting",
                        fill='white',
                        font=('Arial', 7),
                        tags=f"robot_waiting_{robot.id}"
                    )
                
                # Charging progress (if charging)
                if robot.status == "charging":
                    self.canvas.create_rectangle(
                        canvas_x - ROBOT_RADIUS, canvas_y + ROBOT_RADIUS + 40,
                        canvas_x - ROBOT_RADIUS + (2 * ROBOT_RADIUS * robot.charge_progress/100), 
                        canvas_y + ROBOT_RADIUS + 45,
                        fill='#4299E1',
                        outline='#2C5282',
                        tags=f"robot_charge_{robot.id}"
                    )
            
            # Draw conflict notifications
            conflicts = self.fleet_manager.traffic_manager.get_conflicts()
            if conflicts:
                self.conflict_var.set(" | ".join(conflicts))
            else:
                self.conflict_var.set("")
        except Exception as e:
            print(f"Error drawing graph: {e}")
    
    def on_canvas_click(self, event):
        # Get the actual canvas coordinates of the click
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # First check if we're clicking on an existing robot
        for robot in self.fleet_manager.robots:
            pos = self.fleet_manager.get_robot_position(robot.id)
            if pos:
                robot_x, robot_y = self.scale_point(pos[0], pos[1])
                distance = ((canvas_x - robot_x)**2 + (canvas_y - robot_y)**2)**0.5
                
                if distance <= ROBOT_RADIUS:
                    # Select this robot (unless we already have one selected)
                    if self.selected_robot != robot.id:
                        self.selected_robot = robot.id
                        self.selected_vertex = None
                        self.update_status(f"Selected Robot {robot.id}")
                        self.draw_graph()
                    return
        
        # Then check for vertex clicks
        for vertex_id, (x, y) in enumerate(self.nav_graph.vertices):
            # Convert to canvas coordinates
            vertex_x, vertex_y = self.scale_point(x, y)
            
            # Calculate distance from click to vertex center
            distance = ((canvas_x - vertex_x)**2 + (canvas_y - vertex_y)**2)**0.5
            
            # If click is within the vertex circle
            if distance <= VERTEX_RADIUS:
                if self.selected_robot is not None:
                    # Move selected robot to this vertex
                    robot = self.fleet_manager.robots[self.selected_robot]
                    success, message = robot.assign_task(vertex_id)
                    
                    if success:
                        self.update_status(f"Robot {robot.id} moving to vertex {vertex_id}")
                    else:
                        messagebox.showwarning("Movement Failed", message)
                    
                    self.selected_robot = None
                else:
                    # Check if vertex is empty before spawning
                    vertex_empty = True
                    for r in self.fleet_manager.robots:
                        if r.current_vertex == vertex_id and r.current_lane is None:
                            vertex_empty = False
                            break
                    
                    if vertex_empty:
                        # Spawn new robot only if vertex is empty
                        robot = self.fleet_manager.spawn_robot(vertex_id)
                        self.selected_vertex = vertex_id
                        self.update_status(f"Spawned Robot {robot.id} at vertex {vertex_id}")
                    else:
                        self.update_status(f"Vertex {vertex_id} already occupied")
                
                self.draw_graph()
                return
        
        # If we got here, click wasn't on any node or robot
        self.clear_selection()

    def clear_selection(self):
        self.selected_robot = None
        self.selected_vertex = None
        self.update_status("Ready")
        self.draw_graph()
    
    def update_status(self, message):
        self.status_label.config(text=message)
        
        if self.selected_robot is not None:
            robot = self.fleet_manager.robots[self.selected_robot]
            status_text = f"Robot {robot.id} - Status: {robot.status}"
            if robot.status == "moving" and robot.path:
                dest = self.nav_graph.get_vertex_name(robot.path[-1])
                status_text += f" (to {dest})"
            if robot.status == "charging":
                status_text += f" ({robot.battery}%)"
            self.selected_robot_var.set(status_text)
        else:
            self.selected_robot_var.set("No robot selected")
    
    def update(self):
        if not self.running:
            return
            
        try:
            self.fleet_manager.update_robots()
            self.draw_graph()
            self.update_id = self.master.after(UPDATE_INTERVAL, self.update)
        except Exception as e:
            print(f"Error in update loop: {e}")
            self.running = False