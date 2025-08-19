import json
import os

from definition.gimmick import Gimmick, GimmickList
from inventory.gimmick_list_inventory import GimmickListInventory


class GimmickManager:
    def __init__(self, base_path: str):
        self.base_path = base_path
        gimmick_path = os.path.join(base_path, "gimmicks.json")

        self.gimmicks = {}
        with open(gimmick_path, "r") as gimmick_file:
            data = json.load(gimmick_file)

            print("===== GimmickManager =====")
            for gimmick_list in data:
                self.gimmicks[gimmick_list] = {}

                img_path = data[gimmick_list]["img_path"]
                full_img_path = os.path.join(base_path, img_path)
                self.gimmicks[gimmick_list]["img_path"] = full_img_path

                self.gimmicks[gimmick_list]["gimmicks"] = []
                gimmicks = []

                for gimmick in data[gimmick_list]["gimmicks"]:
                    pokemon = gimmick["pokemon"]
                    version = gimmick["version"] if "version" in gimmick else ""
                    method = gimmick["method"] if "method" in gimmick else ""
                    zone = gimmick["zone"] if "zone" in gimmick else ""
                    bonus = gimmick["bonus"]
                    note = gimmick["note"]
                    gimmick = Gimmick(pokemon, version, method, zone, bonus, note)
                    gimmicks.append(gimmick)

                self.gimmicks[gimmick_list] = GimmickList(gimmicks, img_path)
                print(f"Loaded gimmick list: {gimmick_list}")

        self.gimmick_list_inventory = GimmickListInventory(self.gimmicks)
        self.gimmick_list_inventory.load(base_path)