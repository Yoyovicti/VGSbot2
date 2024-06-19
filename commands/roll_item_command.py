import interactions
import numpy
from numpy import random

from commands.item_command import ItemCommand
from commands.mission_command import MissionCommand
from commands.quest_command import QuestCommand
from commands.usable_item_command import UsableItemCommand
from init_config import TEAM_FOLDER, item_manager, roll_manager, team_manager, quest_manager
from manager.roll_manager import N_POS


class RollItemCommand(ItemCommand):
    def __init__(self, bot: interactions.Client, ctx: interactions.SlashContext, method: str, position: int,
                 qty: int = 1, charm: bool = False):
        super().__init__(bot, ctx)

        self.quest_inventory = None
        self.mission_inventory = None

        self.method = roll_manager.method_drops[method]
        self.position = min(position, N_POS)
        self.qty = qty
        self.charm = charm

    async def load_team_info(self) -> bool:
        if not await super().load_team_info():
            return False

        self.quest_inventory = self.team.inventory_manager.quest_inventory
        if not self.quest_inventory.initialized:
            await self.ctx.send("Erreur: La liste de quêtes n'est pas initialisée.")
            return False

        self.mission_inventory = self.team.inventory_manager.mission_inventory
        if not self.mission_inventory.initialized:
            await self.ctx.send("Erreur: La liste de missions n'est pas initialisée.")
            return False

        return True

    async def run(self):
        # TODO semi-random ?
        success = await self.load_team_info()
        if not success:
            return

        global_save_item = False
        global_save_quest = False
        global_save_mission = False
        for _ in range(self.qty):
            save_item, save_quest, save_mission = await self.run_roll()
            if save_item:
                global_save_item = True
            if save_quest:
                global_save_quest = True
            if save_mission:
                global_save_mission = True

        # Save inventory
        if global_save_item:
            self.item_inventory.save(TEAM_FOLDER, self.team.id)
        if global_save_quest:
            self.quest_inventory.save(TEAM_FOLDER, self.team.id)
        if global_save_mission:
            self.mission_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message and send to item channel
        inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
        await inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))

    async def run_roll(self, enable_charm: bool = True):
        message = "*Aucun objet tiré*\n"
        save_item = False
        save_quest = False
        save_mission = False
        item = ""
        quest = ""
        mission = ""

        # Roll method
        meth_rng = random.Generator(random.MT19937())
        if meth_rng.random() < self.method.item_drop:
            item = self.roll_item()
            message = f"*Objet tiré:* {item_manager.items[item].get_emoji()}\n"

            if not item_manager.items[item].instant:
                self.item_inventory.add(item)
                save_item = True

        # Quests
        if self.method.quest_drop > 0:
            quest_message = "*Pas de quête tirée*"
            quest_rng = random.Generator(random.MT19937())
            if quest_rng.random() < self.method.quest_drop:
                quest = self.roll_quest()
                q_step = 0
                if quest in self.quest_inventory.saved:
                    q_step = self.quest_inventory.saved[quest]
                if quest != "":
                    quest_message = f"{self.quest_inventory.quests[quest].format_discord(q_step)}\n"
            message += quest_message

        # Missions
        if self.method.mission_drop > 0:
            mission_message = "*Pas de mission tirée*"
            mission_rng = random.Generator(random.MT19937())
            if mission_rng.random() < self.method.mission_drop:
                mission = self.roll_mission()
                if mission != "":
                    mission_message = f"{self.mission_inventory.missions[mission].format_discord()}\n"
            message += mission_message

        team_message = message
        boss_message = message

        if item == "champinocif":
            target_team = await self.run_champi()
            team_message += f"*Vos points s'envolent vers d'autres cieux...*\n"
            boss_message += (f"{item_manager.items[item].get_emoji()} *Les points du shiny s'en vont vers "
                             f"l'équipe* **{team_manager.teams[target_team].name}**\n")

        await self.item_channel.send(team_message)
        await self.ctx.send(boss_message)

        if item == "carapacebleue" or item == "eclair":
            await self.ctx.channel.send(team_manager.get_boss_mention())

        # Run Cadoizo after sending message
        if item == "cadoizo":
            command = UsableItemCommand(self.bot, self.ctx, "cadoizo", enable_save=False)
            await command.run()
            save_item = True

        # Quest
        if quest != "":
            command = QuestCommand(self.bot, self.ctx, "add", quest, enable_save=False, use_slots=True)
            await command.run()
            save_quest = True

        # Mission
        if mission != "":
            command = MissionCommand(self.bot, self.ctx, "add", mission, enable_save=False, use_slots=True)
            await command.run()
            save_mission = True

        if enable_charm and self.charm:
            charm_rng = random.Generator(random.MT19937())
            if charm_rng.random() < self.method.charm_roll:
                message = "*Le charme* **Cupidité irréversible** s'active, vous obtenez un tirage supplémentaire."
                await self.item_channel.send(message)
                await self.ctx.send(message)

                charm_save_item, charm_save_quest, charm_save_mission = await self.run_roll(enable_charm=False)
                if charm_save_item:
                    save_item = True
                if charm_save_quest:
                    save_quest = True
                if charm_save_mission:
                    save_mission = True

        return save_item, save_quest, save_mission

    def roll_item(self) -> str:
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
        probs = numpy.array(weights) * 1 / sum(weights)

        rng = random.Generator(random.MT19937())
        item = rng.choice(valid_items, p=probs)
        return item

    def roll_quest(self) -> str:
        valid_quests = []
        for quest in self.quest_inventory.quests:
            if quest in self.quest_inventory.current or quest in self.quest_inventory.completed:
                continue
            valid_quests.append(quest)

        if len(valid_quests) <= 0:
            return ""

        rng = random.Generator(random.MT19937())
        return rng.choice(valid_quests)

    def roll_mission(self) -> str:
        valid_missions = []
        for mission in self.mission_inventory.missions:
            if mission in self.mission_inventory.current or mission in self.mission_inventory.completed:
                continue
            valid_missions.append(mission)

        if len(valid_missions) <= 0:
            return ""

        rng = random.Generator(random.MT19937())
        return rng.choice(valid_missions)

    async def run_champi(self):
        # TODO merge with champi command
        valid_teams = [team for team in team_manager.teams if team != self.team.id]
        rng = random.Generator(random.MT19937())
        target_team = rng.choice(valid_teams)
        return target_team

