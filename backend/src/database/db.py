import json
from datetime import datetime
import os

class ProcessesDB:
    def __init__(self):
        self.path = "processes.json"
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump({}, f)

    def load_processes(self):
        try:
            with open(self.path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def add_process(self, response):
        processes = self.load_processes()
        timestamp = datetime.now().isoformat()
        processes[timestamp] = response
        self.save_processes(processes)
        return timestamp
    
    def save_processes(self, processes):
        with open(self.path, "w") as f:
            json.dump(processes, f, indent=4)
