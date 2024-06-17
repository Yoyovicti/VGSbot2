import interactions

from commands.item_command import ItemCommand
from init_config import TEAM_FOLDER, quest_manager, item_manager
from init_emoji import REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N
from manager.reaction_manager import ReactionManager


class QuestCommand(ItemCommand):
    def __init__(self, bot: interactions.Client, ctx: interactions.SlashContext, param: str, quest_id: str):
        super().__init__(bot, ctx)
        self.quest_inventory = None

        self.command_map = {
            "add": self.run_add,
            "cancel": self.run_cancel,
            "save": self.run_save,
            "forward": self.run_forward,
            "backward": self.run_backward
        }

        self.param = param
        self.quest_id = quest_id

    async def load_team_info(self) -> bool:
        if not await super().load_team_info():
            return False

        self.quest_inventory = self.team.inventory_manager.quest_inventory
        if not self.quest_inventory.initialized:
            await self.ctx.send("Erreur: L'inventaire n'est pas initialisé.")
            return False

        return True

    async def run(self):
        if self.param in self.command_map:
            await self.command_map[self.param]()

    async def run_add(self):
        success = await self.load_team_info()
        if not success:
            return

        if self.quest_id in self.quest_inventory.current or self.quest_id in self.quest_inventory.completed:
            await self.ctx.send("Erreur: La quête est déjà commencée ou terminée.")
            return

        # Add quest to current quests and save
        self.quest_inventory.add_quest(self.quest_id)
        self.quest_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message and send to item channel for current team
        inv_msg = await self.item_channel.fetch_message(self.quest_inventory.message_id)
        await inv_msg.edit(content=self.quest_inventory.format_discord(self.team.name))
        message = f"*La quête {self.quest_id} a été ajoutée aux missions en cours.*"
        await self.item_channel.send(message)

        # Confirmation message
        await self.ctx.send(f"Quête {self.quest_id} ajoutée aux missions en cours !")

    async def run_cancel(self):
        success = await self.load_team_info()
        if not success:
            return

        if not (self.quest_id in self.quest_inventory.current or
                self.quest_id in self.quest_inventory.completed):
            await self.ctx.send("Erreur: La quête n'est pas dans les quêtes en cours ou validées.")
            return

        # Cancel quest and save
        self.quest_inventory.cancel_quest(self.quest_id)
        self.quest_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message and send to item channel for current team
        inv_msg = await self.item_channel.fetch_message(self.quest_inventory.message_id)
        await inv_msg.edit(content=self.quest_inventory.format_discord(self.team.name))
        message = f"*La quête {self.quest_id} a été annulée.*"
        await self.item_channel.send(message)

        # Confirmation message
        await self.ctx.send(f"Quête {self.quest_id} annulée !")

    async def run_save(self):
        success = await self.load_team_info()
        if not success:
            return

        if self.quest_id not in self.quest_inventory.current:
            await self.ctx.send("Erreur: La quête n'est pas dans les quêtes en cours.")
            return

        # Save quest and save
        self.quest_inventory.save_quest(self.quest_id)
        self.quest_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message and send to item channel for current team
        inv_msg = await self.item_channel.fetch_message(self.quest_inventory.message_id)
        await inv_msg.edit(content=self.quest_inventory.format_discord(self.team.name))
        message = f"*La quête {self.quest_id} a été sauvegardée.*"
        await self.item_channel.send(message)

        # Confirmation message
        await self.ctx.send(f"Quête {self.quest_id} sauvegardée !")

    async def run_forward(self):
        success = await self.load_team_info()
        if not success:
            return

        if self.quest_id in self.quest_inventory.completed:
            await self.ctx.send("Erreur: La quête est déjà complétée.")
            return

        if self.quest_id not in self.quest_inventory.current:
            await self.ctx.send("Erreur: La quête n'a pas été commencée.")
            return

        curr_step = self.quest_inventory.current[self.quest_id]
        item_reward = quest_manager.quests[self.quest_id].steps[curr_step].reward.item_reward

        team_message = f"*La quête {self.quest_id} a été mise à jour.*"
        boss_message = f"Quête {self.quest_id} mise à jour !"
        if item_reward:
            skip_reward = False

            message = await self.ctx.send("Donner la récompense aux participants ?")
            reaction_manager = ReactionManager(message, [REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N])
            reaction = await reaction_manager.run()
            if reaction != REGIONAL_INDICATOR_O:
                skip_reward = True

            if not skip_reward:
                reward_str = f"Félicitations pour avoir complété l'étape {curr_step + 1} de la quête {self.quest_id} !\n"
                should_save = False
                reward_str += "Vous obtenez :\n"
                for item in item_reward:
                    for i in range(2):
                        if item_reward[item][i] > 0:
                            if i == 1 or not item_manager.items[item].instant:
                                self.item_inventory.add(item, qty=item_reward[item][i], gold=(i == 1))
                                should_save = True
                            reward_str += f"{item_manager.items[item].get_emoji(i == 1)}x{item_reward[item][i]}\n"
                if should_save:
                    self.item_inventory.save(TEAM_FOLDER, self.team.id)
                    # Edit item inventory message
                    item_inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
                    await item_inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))

                await self.item_channel.send(reward_str)

        # Forward quest and save
        self.quest_inventory.forward(self.quest_id)
        self.quest_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message and send to item channel for current team
        inv_msg = await self.item_channel.fetch_message(self.quest_inventory.message_id)
        await inv_msg.edit(content=self.quest_inventory.format_discord(self.team.name))

        # Send messages
        await self.item_channel.send(team_message)
        await self.ctx.send(boss_message)

    async def run_backward(self):
        success = await self.load_team_info()
        if not success:
            return

        if not (self.quest_id in self.quest_inventory.current or self.quest_id in self.quest_inventory.completed):
            await self.ctx.send("Erreur: La quête n'est pas commencée.")
            return

        team_message = f"*La quête {self.quest_id} a été mise à jour.*"
        boss_message = f"Quête {self.quest_id} mise à jour !"

        # Forward quest and save
        self.quest_inventory.backward(self.quest_id)
        self.quest_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message and send to item channel for current team
        inv_msg = await self.item_channel.fetch_message(self.quest_inventory.message_id)
        await inv_msg.edit(content=self.quest_inventory.format_discord(self.team.name))

        # Send messages
        await self.item_channel.send(team_message)
        await self.ctx.send(boss_message)
