import tkinter as tk
import sys
from src.gui.fleet_gui import FleetGUI

def main():
    root = tk.Tk()
    root.title("Fleet Management System")
    root.geometry("1200x800")
    
    # Check if a JSON file was provided as command line argument
    if len(sys.argv) > 1:
        gui = FleetGUI(root, sys.argv[1])
    else:
        gui = FleetGUI(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()