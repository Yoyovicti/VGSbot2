from inventory.gimmick_inventory import GimmickInventory
from inventory.inventory import Inventory
from inventory.item_inventory import ItemInventory
from inventory.mission_inventory import MissionInventory
from inventory.quest_inventory import QuestInventory


class InventoryManager:
    def __init__(self, item_inventory: ItemInventory, mission_inventory: MissionInventory,
                 quest_inventory: QuestInventory, gimmick_inventory: GimmickInventory):
        self.item_inventory = item_inventory
        self.mission_inventory = mission_inventory
        self.quest_inventory = quest_inventory
        self.gimmick_inventory = gimmick_inventory

    def get_inventory(self, inv_type: str) -> Inventory | None:
        inventory = None
        if inv_type == "item":
            inventory = self.item_inventory
        elif inv_type == "mission":
            inventory = self.mission_inventory
        elif inv_type == "quest":
            inventory = self.quest_inventory
        elif inv_type == "gimmick":
            inventory = self.gimmick_inventory
        return inventory
