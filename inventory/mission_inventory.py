import json
import os
from typing import Dict

from definition.mission import Mission
from inventory.inventory import Inventory
from manager import save_manager


class MissionInventory(Inventory):
    def __init__(self, missions: Dict[str, Mission], message_id: str = "0"):
        super().__init__(message_id)
        self.missions = missions

        self.current = []
        self.completed = []

    def init(self, message_id: str):
        self.message_id = message_id
        self.clear()
        self.initialized = True

    def delete(self, base_path: str, team_name: str):
        folder_path = os.path.join(base_path, team_name)
        save_manager.delete(folder_path, "mission_inventory.json")

        self.message_id = "0"
        self.clear()
        self.initialized = False

    def clear(self):
        self.current = []
        self.completed = []

    def load(self, base_path: str, team_name: str):
        folder_path = os.path.join(base_path, team_name)
        data = save_manager.load(folder_path, "mission_inventory.json")
        if data == "":
            return

        self.deserialize(data)
        self.initialized = True

    def save(self, base_path: str, team_name: str):
        folder_path = os.path.join(base_path, team_name)
        save_manager.save(folder_path, "mission_inventory.json", self.serialize())

    def deserialize(self, data: str):
        json_data = json.loads(data)
        self.message_id = json_data["message_id"]
        self.current = json_data["current"]
        self.completed = json_data["completed"]

    def serialize(self) -> str:
        data = {
            "message_id": self.message_id,
            "current": self.current,
            "completed": self.completed
        }
        return json.dumps(data, indent=4)
