from inventory.inventory_manager import InventoryManager


class Team:
    def __init__(self, team_id, name: str, bot_channel_id: str, item_channel_id: str, shiny_channel_id: str, inventory_manager: InventoryManager):
        self.id = team_id
        self.name = name
        self.bot_channel_id = bot_channel_id
        self.item_channel_id = item_channel_id
        self.shiny_channel_id = shiny_channel_id
        self.inventory_manager = inventory_manager

    def __str__(self):
        return f"{self.name} {self.bot_channel_id} {self.item_channel_id} {self.shiny_channel_id}"
