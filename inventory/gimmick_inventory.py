import json
import os
from typing import Dict

import save_manager
from gimmick import Gimmick
from inventory.inventory import Inventory


class GimmickInventory(Inventory):
    def __init__(self, gimmicks: Dict[str, Gimmick]):
        super().__init__()
        self.gimmicks = gimmicks
        self.seen = {}
        self.contents = {
            region: {
                "found": "-",
                "seen": 0,
                "unlocked": False
            }
            for region in gimmicks
        }

    def init(self, message_id: str):
        self.message_id = message_id
        self.clear()
        self.initialized = True

    def delete(self, base_path: str, team_name: str):
        folder_path = os.path.join(base_path, team_name)
        save_manager.delete(folder_path, "gimmick_inventory.json")

        self.message_id = "0"
        self.clear()
        self.initialized = False

    def clear(self):
        self.seen = {}
        self.contents = {
            region: {
                "found": "-",
                "seen": 0,
                "unlocked": False
            }
            for region in self.gimmicks
        }

    def load(self, base_path: str, team_name: str):
        folder_path = os.path.join(base_path, team_name)
        data = save_manager.load(folder_path, "gimmick_inventory.json")
        if data == "":
            return

        self.deserialize(data)
        self.initialized = True

    def save(self, base_path: str, team_name: str):
        folder_path = os.path.join(base_path, team_name)
        save_manager.save(folder_path, "gimmick_inventory.json", self.serialize())

    def serialize(self) -> str:
        data = {
            "message_id": self.message_id,
            "seen": self.seen,
            "contents": self.contents
        }
        return json.dumps(data, indent=4)

    def deserialize(self, data: str):
        json_data = json.loads(data)
        self.message_id = json_data["message_id"]
        self.seen = json_data["seen"]
        self.contents = json_data["contents"]

    def format_discord(self, team_name: str) -> str:
        string = f"__**Gimmicks de l'équipe {team_name} :**__\n"
        string_seen = f"__**Gimmicks observés :**__\n"

        for region in self.contents:
            gimmick = self.gimmicks[region]
            string += f"**{gimmick.region} :** *{gimmick.zone}"
            if self.contents[region]["unlocked"]:
                string += f" - {gimmick.pokemon}"
            string += "*\n"

        for team in self.seen:
            string_seen += f"**{team} :** *"
            for zone in self.seen[team]:
                string_seen += f"{zone}, "
            string_seen += "*\n"

        string += "\n" + string_seen
        return string[:2000]
