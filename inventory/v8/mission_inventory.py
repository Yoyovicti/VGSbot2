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
        self.n_slot = 3

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
        self.n_slot = 3

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

    def add_mission(self, mission_id: str):
        self.current.append(mission_id)
        if mission_id in self.completed:
            self.completed.remove(mission_id)

    def complete_mission(self, mission_id: str):
        self.completed.append(mission_id)
        if mission_id in self.current:
            self.current.remove(mission_id)

    def cancel_mission(self, mission_id: str):
        if mission_id in self.current:
            self.current.remove(mission_id)
            return
        if mission_id in self.completed:
            self.completed.remove(mission_id)

    def deserialize(self, data: str):
        json_data = json.loads(data)
        self.message_id = json_data["message_id"]
        self.current = json_data["current"]
        self.completed = json_data["completed"]
        self.n_slot = json_data["n_slot"]

    def serialize(self) -> str:
        data = {
            "message_id": self.message_id,
            "current": self.current,
            "completed": self.completed,
            "n_slot": self.n_slot
        }
        return json.dumps(data, indent=4)

    def format_discord(self, team_name: str) -> str:
        string = f"__**Missions de l'équipe {team_name} :**__\n"
        for mission in self.current:
            string += self.missions[mission].format_discord() + "\n"

        string_completed = f"__**Missions terminées :**__\n"
        n_completed = len(self.completed)
        for i in range(n_completed):
            if i > 0:
                string_completed += ", "
            string_completed += f"{self.completed[i]}"

        string += "\n" + string_completed
        return string[:2000]
