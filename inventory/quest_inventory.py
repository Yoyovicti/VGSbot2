import json
import os
from typing import Dict

from definition.quest import Quest
from inventory.inventory import Inventory
from manager import save_manager


class QuestInventory(Inventory):
    def __init__(self, quests: Dict[str, Quest], message_id: str = "0"):
        super().__init__(message_id)
        self.quests = quests

        self.current = {}
        self.completed = []

    def init(self, message_id: str):
        self.message_id = message_id
        self.clear()
        self.initialized = True

    def delete(self, base_path: str, team_name: str):
        folder_path = os.path.join(base_path, team_name)
        save_manager.delete(folder_path, "quest_inventory.json")

        self.message_id = "0"
        self.clear()
        self.initialized = False

    def clear(self):
        self.current = {}
        self.completed = []

    def load(self, base_path: str, team_name: str):
        folder_path = os.path.join(base_path, team_name)
        data = save_manager.load(folder_path, "quest_inventory.json")
        if data == "":
            return

        self.deserialize(data)
        self.initialized = True

    def save(self, base_path: str, team_name: str):
        folder_path = os.path.join(base_path, team_name)
        save_manager.save(folder_path, "quest_inventory.json", self.serialize())

    def add_quest(self, quest_id: str):
        self.current[quest_id] = 0
        if quest_id in self.completed:
            self.completed.remove(quest_id)

    def cancel_quest(self, quest_id: str):
        if quest_id in self.current:
            self.current.pop(quest_id)
            return
        if quest_id in self.completed:
            self.completed.remove(quest_id)

    def forward(self, quest_id: str):
        if quest_id not in self.current:
            return
        step = self.current[quest_id] + 1
        max_step = len(self.quests[quest_id].steps)
        if step >= max_step:
            self.current.pop(quest_id)
            self.completed.append(quest_id)
            return
        self.current[quest_id] = step

    def backward(self, quest_id: str):
        if quest_id in self.completed:
            self.completed.remove(quest_id)
            self.current[quest_id] = len(self.quests[quest_id].steps) - 1
            return
        if quest_id in self.current:
            if self.current[quest_id] <= 0:
                self.current.pop(quest_id)
                return
            self.current[quest_id] -= 1

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

    def format_discord(self, team_name: str) -> str:
        string = f"__**Quête(s) de l'équipe {team_name} :**__\n"
        for quest in self.current:
            string += self.quests[quest].format_discord(self.current[quest]) + "\n"

        string_completed = f"__**Quêtes terminées :**__\n"
        n_completed = len(self.completed)
        for i in range(n_completed):
            if i > 0:
                string_completed += ", "
            string_completed += f"{self.completed[i]}"

        string += "\n" + string_completed
        return string[:2000]
