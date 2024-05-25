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

    def get_zone(self, region: str) -> str:
        return self.gimmicks[region].zone

    def get_pokemon(self, region: str) -> str:
        return self.gimmicks[region].pokemon

    def get_unlock(self, region: str) -> bool:
        return self.contents[region]["unlocked"]

    def unlock(self, region: str, state: bool = True):
        self.contents[region]["unlocked"] = state

    def get_seen(self, team_name: str, region: str) -> bool:
        if team_name not in self.seen:
            return False

        for gimmick in self.seen[team_name]:
            if gimmick.region == region:
                return True

        return False

    def see(self, team_name: str, gimmick: Gimmick, state: bool = True):
        if not state:
            if team_name in self.seen:
                for curr_gim in self.seen[team_name]:
                    if curr_gim.region == gimmick.region:
                        self.seen[team_name].remove(gimmick)
                        return
            return

        if team_name not in self.seen:
            self.seen[team_name] = []
        self.seen[team_name].append(gimmick)

    def is_found(self, region: str) -> bool:
        return self.contents[region]["found"] != "-"

    def get_valid_clairvoyance_gimmicks(self, seen_gimmicks: List[Gimmick]) -> List[Gimmick]:
        valid_gimmicks = []
        for region in self.contents:
            skip = False
            if self.is_found(region):
                continue
            for gimmick in seen_gimmicks:
                if gimmick.region == region:
                    skip = True
                    break
            if skip:
                continue

            valid_gimmicks.append(self.gimmicks[region])
        return valid_gimmicks


    def add_see_count(self, region: str, qty: int = 1):
        self.contents[region]["seen"] += qty

    def remove_see_count(self, region: str, qty: int = 1):
        self.add_see_count(region, qty=-qty)

    def serialize(self) -> str:
        data = {
            "message_id": self.message_id,
            "seen": {
                team: [
                    (gimmick.region, gimmick.zone, gimmick.pokemon)
                    for gimmick in self.seen[team]
                ]
                for team in self.seen
            },
            "contents": self.contents
        }
        return json.dumps(data, indent=4)

    def deserialize(self, data: str):
        json_data = json.loads(data)
        self.message_id = json_data["message_id"]
        self.seen = {
            team: [
                Gimmick(region, zone, pokemon)
                for (region, zone, pokemon) in json_data["seen"][team]
            ]
            for team in json_data["seen"]
        }
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
            for gimmick in self.seen[team]:
                string_seen += f"{gimmick.zone} ({gimmick.region}), "
            string_seen += "*\n"

        string += "\n" + string_seen
        return string[:2000]
