import os
import json
import warnings

from definition.item_drop import ItemDrop
from definition.method import Method

N_POS = 6


class RollManager:
    def __init__(self, base_path: str):
        method_path = os.path.join(base_path, "method_drop.txt")
        item_path = os.path.join(base_path, "item_drop.txt")
        gold_cadoizo_path = os.path.join(base_path, "goldcadoizo.json")

        print("===== RollManager =====")
        self.method_drops = {}
        with open(method_path, "r") as method_file:
            method_file.readline()
            print("> Methods")
            for method in method_file:
                method_id, name, item_drop, mission_drop, quest_drop, charm_roll = method.split()
                name = name.replace("_", " ")

                method_inst = Method(method_id, name, float(item_drop), float(mission_drop), float(quest_drop),
                                     float(charm_roll))
                self.method_drops[method_id] = method_inst
                print(f"Loaded method: {method_inst}")

        self.item_drops = {}
        with open(item_path, "r") as item_file:
            item_file.readline()
            print("> Items")
            for item_drop in item_file:
                item_drop_data = item_drop.split()
                item_id = item_drop_data[0]
                cado = float(item_drop_data[1])
                regular = [float(drop) for drop in item_drop_data[2:]]

                item_drop_inst = ItemDrop(item_id, cado, regular)
                self.item_drops[item_id] = item_drop_inst
                print(f"Loaded item drop: {item_drop_inst}")

        self.gold_cadoizo = {}
        with open(gold_cadoizo_path, "r") as gold_cadoizo_file:
            self.gold_cadoizo = json.load(gold_cadoizo_file)
        print(f"Loaded gold cadoizo drops: {self.gold_cadoizo}")

        # Check sum of item drops
        sum_cado = sum([self.item_drops[item].cado for item in self.item_drops])
        if not 0.999 < sum_cado < 1.001:
            warnings.warn(f"Cadoizo: Invalid item table")
        for i in range(N_POS):
            sum_weights = sum([self.item_drops[item].drops[i] for item in self.item_drops])
            if not 0.999 < sum_weights < 1.001:
                warnings.warn(f"Position {i + 1}: Invalid item table")
