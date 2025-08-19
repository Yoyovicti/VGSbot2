import json
from datetime import datetime
from typing import Dict

import pytz

from definition.gimmick import GimmickList
from inventory.gimmick_inventory import GimmickInventory
from manager import save_manager


class GimmickListInventory:
    def __init__(self, gimmicks: Dict[str, GimmickList]):
        self.initialized = False
        self.gimmicks = gimmicks

        self.contents = {
            gimmick_list: GimmickInventory(gimmick_list, gimmicks[gimmick_list])
            for gimmick_list in gimmicks
        }

    def init(self):
        self.clear()
        self.initialized = True

    def delete(self, base_path: str):
        save_manager.delete(base_path, "gimmick_inventory.json")

        self.clear()
        self.initialized = False

    def clear(self):
        for gimmick_list in self.contents:
            self.contents[gimmick_list].clear()

    def load(self, base_path: str):
        data = save_manager.load(base_path, "gimmick_inventory.json")
        if data == "":
            return

        self.deserialize(data)
        self.initialized = True

    def save(self, base_path: str):
        save_manager.save(base_path, "gimmick_inventory.json", self.serialize())

    def serialize(self) -> str:
        data = {
            "contents": {
                gimmick_list: self.contents[gimmick_list].get_raw_data()
                for gimmick_list in self.gimmicks
            }
        }
        print("data save: ", data)
        return json.dumps(data, indent=4)

    def deserialize(self, data: str):
        json_data = json.loads(data)
        self.contents = {}
        for gimmick_list in self.gimmicks:
            gimmick_inv = GimmickInventory(gimmick_list, self.gimmicks[gimmick_list])
            gimmick_inv.deserialize(json_data["contents"][gimmick_list])
            self.contents[gimmick_list] = gimmick_inv

    def set_observed(self, list_name: str, team: str):
        self.contents[list_name].see(team)

    def set_found(self, list_name: str, team: str, step: int):
        self.contents[list_name].set_found(step, team, datetime.now(pytz.timezone("Europe/Paris")))

    def get_found(self, list_name: str, step: int):
        return self.contents[list_name].get_found(step)

    def get_unlock(self, team: str, list_name: str):
        return self.contents[list_name].get_unlock(team)

    def set_unlock(self, team: str, list_name: str):
        self.contents[list_name].unlock(team)

    def get_current_step(self, list_name: str) -> int:
        return self.contents[list_name].current_step

    def next_step(self, list_name: str):
        self.contents[list_name].next_step()

    def clear_seen(self, list_name: str):
        self.contents[list_name].clear_seen()

    def clear_unlocked(self, list_name: str):
        self.contents[list_name].clear_unlocked()