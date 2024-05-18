import os.path
from typing import Dict

import save_manager
from inventory.inventory import Inventory
from item import Item

CLASSIC_ITEM = 0
SAFE_ITEM = 1
GOLD_ITEM = 2


class ItemInventory(Inventory):
    def __init__(self, items: Dict[str, Item], message_id: str = "0"):
        super().__init__(message_id)
        self.items = items

        self.contents = {
            item: [0, 0, 0]
            for item in items
        }

    def init(self, message_id: str):
        self.message_id = message_id
        self.clear()
        self.initialized = True

    def delete(self, base_path: str, team_name: str):
        folder_path = os.path.join(base_path, team_name)
        save_manager.delete(folder_path, "item_inventory.txt")

        self.message_id = "0"
        self.clear()
        self.initialized = False

    def clear(self):
        self.contents = {
            item: [0, 0, 0]
            for item in self.items
        }

    def load(self, base_path: str, team_name: str):
        folder_path = os.path.join(base_path, team_name)
        data = save_manager.load(folder_path, "item_inventory.txt")
        if data == "":
            return

        self.deserialize(data)
        self.initialized = True

    def save(self, base_path: str, team_name: str):
        folder_path = os.path.join(base_path, team_name)
        save_manager.save(folder_path, "item_inventory.txt", self.serialize())

    def add(self, item_id: str, qty: int = 1, gold: bool = False, safe: bool = False):
        if gold:
            self.contents[item_id][GOLD_ITEM] += qty
        elif safe:
            self.contents[item_id][SAFE_ITEM] += qty
        else:
            self.contents[item_id][CLASSIC_ITEM] += qty

    def remove(self, item_id: str, qty: int = 1, gold: bool = False, safe: bool = False):
        if gold:
            self.contents[item_id][GOLD_ITEM] -= qty
        elif safe:
            self.contents[item_id][SAFE_ITEM] -= qty
        else:
            self.contents[item_id][CLASSIC_ITEM] -= qty

    def quantity(self, item: str, gold: bool = False, safe: bool = False):
        if gold:
            return self.contents[item][GOLD_ITEM]
        if safe:
            return self.contents[item][SAFE_ITEM]
        return self.contents[item][CLASSIC_ITEM]

    def serialize(self) -> str:
        data = f"{self.message_id}\n"
        for item, elems in self.contents.items():
            data += f"{item} {elems[CLASSIC_ITEM]} {elems[SAFE_ITEM]} {elems[GOLD_ITEM]}\n"
        return data

    def deserialize(self, data: str):
        data = data.splitlines()
        self.message_id = data[0]
        for line in data[1:]:
            item, classic, safe, gold = line.split()
            self.contents[item] = [int(classic), int(safe), int(gold)]

    def format_discord(self, team_name: str):
        string = f"__**Inventaire de l'équipe {team_name} :**__\n"
        safe_string, gold_string = "", ""

        for item in self.items.values():
            if self.contents[item.id][CLASSIC_ITEM] > 0 or not item.hidden:
                string += f"{item.get_emoji()} x{self.contents[item.id][CLASSIC_ITEM]}\n"
            if self.contents[item.id][SAFE_ITEM] > 0:
                safe_string += f"{item.get_emoji()} x{self.contents[item.id][SAFE_ITEM]}\n"
            if self.contents[item.id][GOLD_ITEM] > 0:
                gold_string += f"{item.get_emoji(True)} x{self.contents[item.id][GOLD_ITEM]}\n"

        if safe_string != "":
            safe_string = f"__**Objets non volables :**__\n" + safe_string
            string += "\n" + safe_string
        if gold_string != "":
            gold_string = f"__**Objets dorés :**__\n" + gold_string
            string += "\n" + gold_string

        return string[:2000]
