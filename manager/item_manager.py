import os

from definition.item import Item


class ItemManager:
    def __init__(self, base_path: str):
        items_path = os.path.join(base_path, "items.txt")
        self.items = {}
        with open(items_path, "r") as items_file:
            items_file.readline()

            print("===== ItemManager =====")
            for item in items_file:
                item_id, name, stealable, max_capacity, instant, hidden, emote_id, gold_emote_id = item.split()
                name = name.replace("_", " ")

                item_inst = Item(item_id, name, bool(int(stealable)), int(max_capacity), bool(int(instant)), bool(int(hidden)), emote_id, gold_emote_id)
                self.items[item_id] = item_inst
                print(f"Loaded item: {item_inst}")
