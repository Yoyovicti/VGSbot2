import numpy as np
from numpy import random

import roll_manager
from init_config import roll_manager, item_manager
from inventory.item_inventory import ItemInventory
from roll_manager import N_POS


class Roll:
    def __init__(self, item_inventory: ItemInventory, method: str, position: int):
        self.item_inventory = item_inventory
        self.method = roll_manager.method_drops[method]
        self.position = min(position, N_POS)

        self.item: str = ""
        self.mission = None
        self.quest = None

    def run(self):
        # TODO mission + quest
        self.item = self.run_item()

    def run_item(self) -> str:
        rng = random.Generator(random.MT19937())
        if rng.random() > self.method.item_drop:
            return ""

        pos_index = self.position - 1

        valid_items = []
        for item in item_manager.items:
            max_capacity = item_manager.items[item].max_capacity
            if max_capacity >= 0:
                total_qty = self.item_inventory.quantity(item) + self.item_inventory.quantity(item, safe=True)
                if total_qty >= max_capacity:
                    continue

            valid_items.append(item)

        # Compute weights (fix weights when some items are not valid)
        weights = [roll_manager.item_drops[item].drops[pos_index] for item in valid_items]
        probs = np.array(weights) * 1 / sum(weights)

        item = rng.choice(valid_items, p=probs)
        return item
