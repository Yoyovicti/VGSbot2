from inventory.inventory import Inventory
from inventory.item_inventory import ItemInventory
from inventory.quest_inventory import QuestInventory


class InventoryManager:
    def __init__(self, item_inventory: ItemInventory, quest_inventory: QuestInventory):
        self.item_inventory = item_inventory
        self.quest_inventory = quest_inventory

    def get_inventory(self, inv_type: str) -> Inventory | None:
        inventory = None
        if inv_type == "item":
            inventory = self.item_inventory
        elif inv_type == "quest":
            inventory = self.quest_inventory
        return inventory
