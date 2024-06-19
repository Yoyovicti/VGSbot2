import interactions

from commands.item_command import ItemCommand
from init_config import TEAM_FOLDER, mission_manager
from init_emoji import REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N, KEYCAP_NUMBERS, CROSS_MARK
from manager.reaction_manager import ReactionManager


class MissionCommand(ItemCommand):
    def __init__(self, bot: interactions.Client, ctx: interactions.SlashContext, param: str, mission_id: str = "",
                 n_slot: int = 3, enable_save: bool = True, use_slots: bool = False):
        super().__init__(bot, ctx)
        self.mission_inventory = None

        self.command_map = {
            "add": self.run_add,
            "complete": self.run_complete,
            "cancel": self.run_cancel,
            "slot": self.run_slot
        }

        self.param = param
        self.mission_id = mission_id

        self.enable_save = enable_save
        self.use_slots = use_slots
        self.n_slot = n_slot

    async def load_team_info(self) -> bool:
        if not await super().load_team_info():
            return False

        self.mission_inventory = self.team.inventory_manager.mission_inventory
        if not self.mission_inventory.initialized:
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

        if self.mission_id in self.mission_inventory.current:
            await self.ctx.send("Erreur: La mission est déjà en cours.")
            return

        if self.use_slots and len(self.mission_inventory.current) >= self.mission_inventory.n_slot:
            mission_string = (
                "Vous n'avez pas de place pour accueillir une nouvelle mission. Si vous désirez remplacer "
                "une mission en cours par la nouvelle, veuillez sélectionner la mission à remplacer :\n\n")
            mission_string += "❌ Garder les missions actuelles\n"

            n_missions = len(self.mission_inventory.current)
            for i in range(n_missions):
                mission = self.mission_inventory.current[i]
                mission_inst = self.mission_inventory.missions[mission]
                mission_string += f"{KEYCAP_NUMBERS[i]} {mission_inst.format_discord()}\n"
            mission_message = await self.item_channel.send(mission_string)

            reaction_choices = [CROSS_MARK] + KEYCAP_NUMBERS[:n_missions]
            reaction_manager = ReactionManager(mission_message, reaction_choices)
            selected_reaction = await reaction_manager.run()

            if selected_reaction == CROSS_MARK:
                cancel_message = "Missions conservées !"
                await mission_message.reply(cancel_message)
                await self.ctx.send(cancel_message)
                return

            replaced_mission = self.mission_inventory.current[KEYCAP_NUMBERS.index(selected_reaction)]
            self.mission_inventory.cancel_mission(replaced_mission)

        # Add mission to current missions and save
        self.mission_inventory.add_mission(self.mission_id)
        if self.enable_save:
            self.mission_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message and send to item channel for current team
        inv_msg = await self.item_channel.fetch_message(self.mission_inventory.message_id)
        await inv_msg.edit(content=self.mission_inventory.format_discord(self.team.name))
        message = f"*La mission {self.mission_id} a été ajoutée aux missions en cours.*"
        await self.item_channel.send(message)

        # Confirmation message
        await self.ctx.send(f"Mission {self.mission_id} ajoutée aux missions en cours !")

    async def run_complete(self):
        success = await self.load_team_info()
        if not success:
            return

        if self.mission_id in self.mission_inventory.completed:
            await self.ctx.send("Erreur: La mission est déjà validée.")
            return

        # Ask to give reward
        skip_reward = False
        message = await self.ctx.send("Voulez-vous proposer la récompense ?")
        reaction_manager = ReactionManager(message, [REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N])
        reaction = await reaction_manager.run()
        if reaction != REGIONAL_INDICATOR_O:
            skip_reward = True

        team_message = f"*La mission {self.mission_id} a été ajoutée aux missions validées.*"
        boss_message = f"Mission {self.mission_id} validée !"
        if not skip_reward:
            reward_str = (f"Félicitations pour avoir complété la mission {self.mission_id} !\n"
                          f"Plusieurs récompenses s'offrent à vous. Choisissez bien !\n\n")
            reward = mission_manager.missions[self.mission_id].reward
            n_rewards = len(reward.item_reward) + 1
            for i in range(n_rewards):
                reward_str += f"{KEYCAP_NUMBERS[i]} "
                if i == 0:
                    if reward.points < 0:
                        reward_str += "Nombre de points variables (voir avec un Boss)\n"
                        continue
                    reward_str += f"{reward.points} points\n"
                    continue
                reward_str += f"{reward.item_reward[i - 1]}\n"

            reward_msg = await self.item_channel.send(reward_str)
            reaction_manager = ReactionManager(reward_msg, KEYCAP_NUMBERS[:n_rewards])
            selected_reaction = await reaction_manager.run()

            # Standard message for points
            team_message = "Vous avez choisi les points. Ils seront ajoutés prochainement à votre score !"
            boss_message = f"Points sélectionnés pour la mission {self.mission_id}"

            r_index = KEYCAP_NUMBERS.index(selected_reaction)
            if r_index > 0:
                team_message = "Objet(s) ajouté(s) à l'inventaire !"
                boss_message = f"Mission {self.mission_id} validée, inventaire mis à jour !"

                # Add items to inventory and save
                item_reward = reward.item_reward[r_index - 1]
                for item in item_reward.item_reward:
                    for i in range(2):
                        self.item_inventory.add(item, qty=item_reward.item_reward[item][i], gold=(i == 1))
                self.item_inventory.save(TEAM_FOLDER, self.team.id)

            # Edit item inventory message
            item_inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
            await item_inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))

        # Send team message
        await self.item_channel.send(team_message)

        # Add mission to completed missions and save
        self.mission_inventory.complete_mission(self.mission_id)
        if self.enable_save:
            self.mission_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit mission inventory message
        mission_inv_msg = await self.item_channel.fetch_message(self.mission_inventory.message_id)
        await mission_inv_msg.edit(content=self.mission_inventory.format_discord(self.team.name))

        # Confirmation message
        await self.ctx.send(boss_message)

    async def run_cancel(self):
        success = await self.load_team_info()
        if not success:
            return

        if not (self.mission_id in self.mission_inventory.current or
                self.mission_id in self.mission_inventory.completed):
            await self.ctx.send("Erreur: La mission n'est pas dans les missions en cours ou validées.")
            return

        # Add mission to current missions and save
        self.mission_inventory.cancel_mission(self.mission_id)
        if self.enable_save:
            self.mission_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message and send to item channel for current team
        inv_msg = await self.item_channel.fetch_message(self.mission_inventory.message_id)
        await inv_msg.edit(content=self.mission_inventory.format_discord(self.team.name))
        message = f"*La mission {self.mission_id} a été annulée.*"
        await self.item_channel.send(message)

        # Confirmation message
        await self.ctx.send(f"Mission {self.mission_id} annulée !")

    async def run_slot(self):
        success = await self.load_team_info()
        if not success:
            return

        if self.n_slot == self.mission_inventory.n_slot:
            await self.ctx.send(f"Erreur: Le nombre de slots de missions est déjà de {self.n_slot}.")
            return

        if self.n_slot < len(self.mission_inventory.current):
            warning_msg = await self.ctx.send("Cette opération va supprimer et sauvegarder la dernière mission "
                                              "ajoutée.\nSouhaitez-vous continuer ?")
            reaction_manager = ReactionManager(warning_msg, [REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N])
            reaction = await reaction_manager.run()
            if reaction != REGIONAL_INDICATOR_O:
                await self.ctx.send("Opération annulée.")
                return

            # Cancel last mission added
            self.mission_inventory.cancel_mission(self.mission_inventory.current[-1])

            # Edit inventory message
            inv_msg = await self.item_channel.fetch_message(self.mission_inventory.message_id)
            await inv_msg.edit(content=self.mission_inventory.format_discord(self.team.name))

        self.mission_inventory.n_slot = self.n_slot
        if self.enable_save:
            self.mission_inventory.save(TEAM_FOLDER, self.team.id)

        # Send messages
        message = f"*Le nombre de slots pour les missions est passé à {self.n_slot}*"
        await self.item_channel.send(message)
        await self.ctx.send(message)
