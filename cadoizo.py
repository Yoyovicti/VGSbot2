import numpy as np
from numpy import random

from init_config import roll_manager, item_manager
from inventory.item_inventory import ItemInventory


class Cadoizo:
    def __init__(self, item_inventory: ItemInventory, is_gold: bool = False):
        self.item_inventory = item_inventory
        self.n_items = 5 if is_gold else 3
        self.is_gold = is_gold

    def run(self):
        rng = random.Generator(random.MT19937())

        if self.is_gold:
            choices = rng.choice([kit for kit in roll_manager.gold_cadoizo], size=self.n_items, replace=False)
            return choices

        valid_items = []
        for item in item_manager.items:
            max_capacity = item_manager.items[item].max_capacity
            if max_capacity >= 0:
                total_qty = self.item_inventory.quantity(item) + self.item_inventory.quantity(item, safe=True)
                if total_qty >= max_capacity:
                    continue
            valid_items.append(item)

        # Compute weights (fix weights when some items are not valid)
        weights = [roll_manager.item_drops[item].cado for item in valid_items]
        probs = np.array(weights) * 1 / sum(weights)

        choices = list(rng.choice(valid_items, p=probs, size=self.n_items-1, replace=False))
        choices.insert(rng.choice(range(self.n_items)), "metamorph")
        return choices
