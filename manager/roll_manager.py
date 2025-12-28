import json
import os
from typing import List, Dict

from definition.method import Method, MethodItemDrop

N_POS = 6

class RollManager:
    def __init__(self, base_path: str):
        print("===== RollManager =====")

        method_items_path = os.path.join(base_path, "v10/method_item_drop.json")
        self.methods : Dict[str, Method] = {}
        with open(method_items_path, "r") as method_items_file:
            data = json.load(method_items_file)

            item_ids = data["items"]
            cat_ids = data["drop_categories"]
            method_data = data["methods"]
            for method_id in method_data:
                self.methods[method_id] = Method(
                    method_id, method_data[method_id]["name"],
                    cat_ids, method_data[method_id]["drop_rates"],
                    item_ids, method_data[method_id]["drop_table"])

                print(f"Loaded method: {method_id}")

        gold_cadoizo_path = os.path.join(base_path, "goldcadoizo.json")
        self.gold_cadoizo = {}
        with open(gold_cadoizo_path, "r") as gold_cadoizo_file:
            self.gold_cadoizo = json.load(gold_cadoizo_file)
        print(f"Loaded gold cadoizo drops: {self.gold_cadoizo}")

    def get_item_drops(self, method_id: str, cadoizo: bool, pos_index: int) -> List[MethodItemDrop]:
        method = self.methods[method_id]
        return method.get_item_drops(cadoizo, pos_index)
