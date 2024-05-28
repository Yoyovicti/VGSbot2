import json
import os
from typing import Dict, List

import save_manager
from gimmick import Gimmick
from init_emoji import WHITE_CHECK_MARK, CROSS_MARK
from inventory.inventory import Inventory
from item import Item


class GimmickInventory(Inventory):
    def __init__(self, gimmicks: Dict[str, Gimmick], items: Dict[str, Item]):
        super().__init__()
        self.gimmicks = gimmicks
        self.clairvoyance_emoji = items["clairvoyance"].get_emoji()
        self.seen = {}
        # TODO put found, seen, unlocked in gimmick object
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
        # TODO Clear seen gimmicks should update the counter for other teams
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

    def update_gimmicks(self, gimmicks: Dict[str, Gimmick]):
        self.gimmicks = gimmicks

    def get_zone(self, region: str) -> str:
        return self.gimmicks[region].zone

    def get_pokemon(self, region: str) -> str:
        return self.gimmicks[region].pokemon

    def get_unlock(self, region: str) -> bool:
        return self.contents[region]["unlocked"]

    def set_unlock(self, region: str, state: bool = True):
        self.contents[region]["unlocked"] = state

    def get_see_count(self, region: str) -> int:
        return self.contents[region]["seen"]

    def is_seen(self, team_name: str, region: str) -> bool:
        if team_name not in self.seen:
            return False

        for gimmick in self.seen[team_name]:
            if gimmick.region == region:
                return True

        return False

    def get_seen(self, team_name: str, region: str) -> Gimmick | None:
        for gimmick in self.seen[team_name]:
            if gimmick.region == region:
                return gimmick
        return None

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
        return self.get_found(region) != "-"

    def get_found(self, region: str) -> str:
        return self.contents[region]["found"]

    def set_found(self, region: str, team_name: str):
        self.contents[region]["found"] = team_name

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
        # TODO Add emojis
        string = f"__**Gimmicks de l'équipe {team_name} :**__\n"
        for region in self.contents:
            gimmick = self.gimmicks[region]

            found_team_name = self.get_found(region)
            see_count = self.get_see_count(region)
            unlocked = self.get_unlock(region)

            if found_team_name != "-":
                if found_team_name == team_name:
                    string += f"{WHITE_CHECK_MARK} "
                else:
                    string += f"{CROSS_MARK} ~~"

            elif see_count > 0:
                for i in range(see_count):
                    string += f"{self.clairvoyance_emoji}"
                string += " "

            else:
                string += "- "

            string += f"**{gimmick.region} :** *{gimmick.zone}"
            if unlocked:
                string += f" - {gimmick.pokemon}"
            string += "*"

            if found_team_name != "-" and found_team_name != team_name:
                string += f"~~ *Trouvé par* **{found_team_name}**"

            string += "\n"

        string_seen = f"__**Gimmicks observés :**__\n"
        for team in self.seen:
            n_seen = len(self.seen[team])
            if n_seen > 0:
                string_seen += f"**{team} :** *"
                for i in range(len(self.seen[team])):
                    if i > 0:
                        string_seen += ", "
                    gimmick = self.seen[team][i]
                    string_seen += f"{gimmick.region} - {gimmick.zone}"
                string_seen += "*\n"

        string += "\n" + string_seen
        return string[:2000]
