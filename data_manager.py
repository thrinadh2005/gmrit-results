"""
Data management module for storing and loading hall ticket numbers
"""
import os
from config import HALLTICKETS_FILE

class DataManager:
    """Manage hall ticket numbers storage"""
    
    @staticmethod
    def save_halltickets(halltickets):
        """Save hall ticket numbers to file"""
        with open(HALLTICKETS_FILE, 'w') as f:
            for ht in halltickets:
                f.write(f"{ht}\n")
    
    @staticmethod
    def load_halltickets():
        """Load hall ticket numbers from file"""
        if os.path.exists(HALLTICKETS_FILE):
            with open(HALLTICKETS_FILE, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        return []
    
    @staticmethod
    def add_hallticket(hallticket):
        """Add a single hall ticket to the file"""
        halltickets = DataManager.load_halltickets()
        if hallticket not in halltickets:
            halltickets.append(hallticket)
            DataManager.save_halltickets(halltickets)
            return True
        return False
    
    @staticmethod
    def remove_hallticket(hallticket):
        """Remove a hall ticket from the file"""
        halltickets = DataManager.load_halltickets()
        if hallticket in halltickets:
            halltickets.remove(hallticket)
            DataManager.save_halltickets(halltickets)
            return True
        return False
    
    @staticmethod
    def clear_halltickets():
        """Clear all hall tickets"""
        if os.path.exists(HALLTICKETS_FILE):
            os.remove(HALLTICKETS_FILE)
    
    @staticmethod
    def list_halltickets():
        """List all saved hall tickets"""
        return DataManager.load_halltickets()
