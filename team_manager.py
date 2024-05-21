import os
from typing import Dict

from gimmick import Gimmick
from inventory.gimmick_inventory import GimmickInventory
from inventory.inventory_manager import InventoryManager
from inventory.item_inventory import ItemInventory
from inventory.mission_inventory import MissionInventory
from inventory.quest_inventory import QuestInventory
from item import Item
from team import Team


class TeamManager:
    def __init__(self, vgs_path: str, team_path: str, items: Dict[str, Item], gimmicks: Dict[str, Dict[str, Gimmick]]):
        teams_path = os.path.join(vgs_path, "teams.txt")
        self.teams = {}
        with open(teams_path, "r") as teams_file:
            teams_file.readline()
            print("===== TeamManager =====")
            for team in teams_file:
                team_id, name, bot_channel_id, item_channel_id, shiny_channel_id = team.split()
                name = name.replace("_", " ")

                item_inventory = ItemInventory(items)
                item_inventory.load(team_path, team_id)

                gimmick_inventory = GimmickInventory(gimmicks[team_id])
                gimmick_inventory.load(team_path, team_id)

                inv_manager = InventoryManager(
                    item_inventory,
                    MissionInventory(),
                    QuestInventory(),
                    gimmick_inventory
                )

                team_inst = Team(team_id, name, bot_channel_id, item_channel_id, shiny_channel_id, inv_manager)
                self.teams[team_id] = team_inst
                print(f"Loaded team: {team_inst}")

    def get_team(self, channel_id: str) -> Team | None:
        for team in self.teams.values():
            if team.bot_channel_id == channel_id:
                return team
        return None

    def get_team_id(self, channel_id: str) -> str:
        for team_id in self.teams:
            if self.teams[team_id].bot_channel_id == channel_id:
                return team_id
        return ""
