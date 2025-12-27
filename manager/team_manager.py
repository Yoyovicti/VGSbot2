import os
from typing import Dict

from definition.v10.item import Item
from definition.mission import Mission
from definition.quest import Quest
from definition.team import Team
from inventory.item_inventory import ItemInventory
from inventory.quest_inventory import QuestInventory
from manager.inventory_manager import InventoryManager


class TeamManager:
    def __init__(self, vgs_path: str, team_path: str, quests: Dict[str, Quest]):
        boss_roles_path = os.path.join(vgs_path, "boss.txt")
        self.boss_roles = []
        with open(boss_roles_path, "r") as boss_file:
            for role_id in boss_file:
                self.boss_roles.append(role_id.rstrip())

        teams_path = os.path.join(vgs_path, "teams.txt")
        self.teams = {}
        with open(teams_path, "r") as teams_file:
            teams_file.readline()
            print("===== TeamManager =====")
            for team in teams_file:
                team_id, name, bot_channel_id, item_channel_id, shiny_channel_id, role_id = team.split()
                name = name.replace("_", " ")

                item_inventory = ItemInventory()
                item_inventory.load(team_path, team_id)

                # mission_inventory = MissionInventory(missions)
                # mission_inventory.load(team_path, team_id)

                quest_inventory = QuestInventory(quests)
                quest_inventory.load(team_path, team_id)

                # gimmick_inventory = GimmickInventory(gimmicks[team_id], items)
                # gimmick_inventory.load(team_path, team_id)

                # shassercouler_grid = ShasserCoulerGrid(8, 12)
                # shassercouler_grid.load(team_path, team_id)

                inv_manager = InventoryManager(
                    item_inventory,
                    # mission_inventory,
                    quest_inventory,
                    # gimmick_inventory,
                    # shassercouler_grid
                )

                team_inst = Team(team_id, name, bot_channel_id, item_channel_id, shiny_channel_id, role_id, inv_manager)
                self.teams[team_id] = team_inst
                print(f"Loaded team: {team_inst}")

    def get_team(self, channel_id: str) -> Team | None:
        for team in self.teams.values():
            print(team.bot_channel_id, channel_id)
            if team.bot_channel_id == channel_id:
                return team
        return None

    def get_team_id(self, channel_id: str) -> str:
        for team_id in self.teams:
            if self.teams[team_id].bot_channel_id == channel_id:
                return team_id
        return ""

    def get_boss_mention(self) -> str:
        boss_mention = ""
        for role_id in self.boss_roles:
            boss_mention += f"<@&{role_id}> "
        return boss_mention
