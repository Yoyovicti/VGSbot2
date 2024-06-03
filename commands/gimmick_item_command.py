from typing import Dict, List

import interactions
from numpy import random

from commands.usable_item_command import UsableItemCommand
from gimmick import Gimmick
from init_config import team_manager, TEAM_FOLDER, item_manager, gimmick_manager
from init_emoji import REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N, KEYCAP_NUMBERS, CROSS_MARK
from reaction_manager import ReactionManager


class GimmickItemCommand(UsableItemCommand):
    def __init__(self, bot: interactions.Client, ctx: interactions.SlashContext, param: str, qty: int = 1,
                 gold: bool = False, safe: bool = False, region: str = "", zone: str = "", pokemon: str = ""):
        super().__init__(bot, ctx, param, qty=qty, gold=gold, safe=safe)

        self.command_map["d6"] = self.run_d6_command
        self.command_map["clairvoyance"] = self.run_clairvoyance_command

        self.gimmick_inventory = None

        self.region = region
        self.zone = zone
        self.pokemon = pokemon

    async def load_team_info(self) -> bool:
        if not await super().load_team_info():
            return False

        self.gimmick_inventory = self.team.inventory_manager.gimmick_inventory
        if not self.gimmick_inventory.initialized:
            await self.ctx.send("Erreur: La liste de gimmicks n'est pas initialisée.")
            return False

        return True

    async def run_d6_command(self):
        success = await self.load_team_info()
        if not success:
            return

        # Verify quantity, ask to use safe items if needed
        if self.item_inventory.quantity(self.param) < 1:
            await self.ctx.send("Erreur: L'inventaire ne contient pas assez de cet objet.")
            return

        # Check if gimmick has not been found
        if self.gimmick_inventory.is_found(self.region):
            await self.ctx.send("Erreur. Impossible de modifier un gimmick déjà validé.")
            return

        # Update seen list for other teams
        if self.gimmick_inventory.get_see_count(self.region) > 0:
            warning_msg = await self.ctx.send("Attention ! La zone gimmick a déjà été observée par d'autres équipes. "
                                              "Cette opération va indiquer le changement aux équipes concernées.\n"
                                              "Souhaitez-vous continuer ?")
            reaction_manager = ReactionManager(warning_msg, [REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N])
            reaction = await reaction_manager.run()
            if reaction != REGIONAL_INDICATOR_O:
                await self.ctx.send("Opération annulée.")
                return

            gimmick = Gimmick(self.region, self.zone, self.pokemon)
            # Edit other teams
            for team in team_manager.teams:
                if self.team.id == team:
                    continue
                gimmick_inv = team_manager.teams[team].inventory_manager.gimmick_inventory
                if gimmick_inv.is_seen(self.team.name, self.region):
                    # Update and save
                    gimmick_inv.see(self.team.name, gimmick_inv.get_seen(self.team.name, self.region), state=False)
                    gimmick_inv.see(self.team.name, gimmick)
                    gimmick_inv.save(TEAM_FOLDER, team)

                    # Send message
                    item_channel = await self.bot.fetch_channel(team_manager.teams[team].item_channel_id)
                    if item_channel is None:
                        await self.ctx.send(f"Erreur: Salon objets non trouvé pour l'équipe {team}")
                        return False
                    inv_msg = await item_channel.fetch_message(gimmick_inv.message_id)
                    await inv_msg.edit(content=gimmick_inv.format_discord(team_manager.teams[team].name))
                    message = (f"{item_manager.items[self.param].get_emoji()} *Le gimmick de la région* "
                               f"**{self.region}** *observé chez l'équipe {self.team.name} a été modifié.\n"
                               f"La zone est désormais* **{self.zone}**.")
                    await item_channel.send(message)

        # Edit gimmick for current team (with lock)
        self.edit_gimmick(lock=True)

        # Edit inventory message and send to item channel for current team
        inv_msg = await self.item_channel.fetch_message(self.gimmick_inventory.message_id)
        await inv_msg.edit(content=self.gimmick_inventory.format_discord(self.team.name))
        message = (f"{item_manager.items[self.param].get_emoji()} *Le gimmick de la région **{self.region}** a été "
                   f"modifié.\nLa zone est désormais* **{self.zone}**.")
        await self.item_channel.send(message)

        # Remove d6 from inventory, save inventories
        self.item_inventory.remove(self.param)
        self.item_inventory.save(TEAM_FOLDER, self.team.id)
        self.gimmick_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory messages and send to item channel
        gimmick_inv_msg = await self.item_channel.fetch_message(self.gimmick_inventory.message_id)
        await gimmick_inv_msg.edit(content=self.gimmick_inventory.format_discord(self.team.name))
        item_inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
        await item_inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))

        # Confirmation message
        await self.ctx.send(f"{item_manager.items[self.param].get_emoji()} Gimmick modifié !")

    def edit_gimmick(self, lock: bool = False):
        # Update gimmick manager and gimmick inventory
        gimmick_manager.edit_gimmick(self.team.id, self.region, self.zone, self.pokemon)
        self.gimmick_inventory.update_gimmicks(gimmick_manager.gimmicks[self.team.id])
        self.gimmick_inventory.set_unlock(self.region, state=(not lock))

    async def run_clairvoyance_command(self):
        success = await self.load_team_info()
        if not success:
            return

        # Verify quantity, ask to use safe items if needed
        if self.item_inventory.quantity(self.param, self.gold, self.safe) < self.qty:
            classic_qty = self.item_inventory.quantity(self.param)
            safe_qty = self.item_inventory.quantity(self.param, safe=True)
            if self.gold or self.safe or classic_qty + safe_qty < self.qty:
                await self.ctx.send("Erreur: L'inventaire ne contient pas assez de cet objet.")
                return

            # Ask for confirmation in case safe items will be removed
            warning_msg = await self.ctx.send("Cette opération va retirer des objets non volables de l'inventaire. "
                                              "Souhaitez-vous continuer ?")
            reaction_manager = ReactionManager(warning_msg, [REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N])
            reaction = await reaction_manager.run()
            if reaction != REGIONAL_INDICATOR_O:
                await self.ctx.send("Opération annulée.")
                return

        # Run each clairvoyance
        for _ in range(self.qty):
            await self.run_clairvoyance()

        # Save inventories, edit message
        self.item_inventory.save(TEAM_FOLDER, self.team.id)
        self.gimmick_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory messages and send to item channel
        gimmick_inv_msg = await self.item_channel.fetch_message(self.gimmick_inventory.message_id)
        await gimmick_inv_msg.edit(content=self.gimmick_inventory.format_discord(self.team.name))
        item_inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
        await item_inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))

        # Confirmation message
        await self.ctx.send(f"{item_manager.items['clairvoyance'].get_emoji(self.gold)} Inventaires mis à jour !")

    async def run_clairvoyance(self):
        # TODO Make use of gimmick commands
        # TODO Gold clairvoyance on self team ?
        # Load valid teams
        valid_regions = self.get_valid_clairvoyance_regions()
        valid_teams = list(valid_regions)

        # Get number of loops
        n_loop = 1
        if self.gold:
            n_loop = len(valid_teams)

        while n_loop > 0:
            # Select team
            team_select_string = "Veuillez sélectionner l'équipe visée:\n\n"
            for i in range(len(valid_teams)):
                team_select_string += f"{KEYCAP_NUMBERS[i]} {team_manager.teams[valid_teams[i]].name}\n"
            team_select_message = await self.item_channel.send(team_select_string)
            team_reaction_manager = ReactionManager(team_select_message,
                                                    [CROSS_MARK] + KEYCAP_NUMBERS[:len(valid_teams)])
            selected_reaction = await team_reaction_manager.run()

            # Cancel
            if selected_reaction == CROSS_MARK:
                await team_select_message.reply("Opération annulée.")
                await self.ctx.send("Opération annulée.")
                if self.gold:
                    continue
                return

            # Remove target from valid teams (for gold clairvoyance)
            target_team = valid_teams[KEYCAP_NUMBERS.index(selected_reaction)]
            valid_teams.remove(target_team)

            # Get target team instance
            target_team = team_manager.teams[target_team]

            # Check target item channel
            target_item_channel = await self.bot.fetch_channel(target_team.item_channel_id)
            if target_item_channel is None:
                await team_select_message.reply("Opération annulée.")
                await self.ctx.send("Erreur: Salon objets non trouvé pour la cible.")
                continue

            # Remove clairvoyance from inventory on last pass
            if n_loop <= 1:
                if self.gold or self.safe:
                    self.item_inventory.remove("clairvoyance", gold=self.gold, safe=self.safe)
                else:
                    classic_qty = self.item_inventory.quantity(self.param)
                    if classic_qty <= 0:
                        self.item_inventory.remove("clairvoyance", safe=True)
                    else:
                        self.item_inventory.remove("clairvoyance")

            # Choose random region in valid regions
            rng = random.Generator(random.MT19937())
            selected_region = rng.choice(valid_regions[target_team.id])

            # For team that use Clairvoyance, unlock gimmick of selected region
            # No need to save and edit inventory message, it will be done later anyway
            if target_team.id == self.team.id:
                self.gimmick_inventory.set_unlock(selected_region)

                # Send message
                message = (
                    f"*Le Pokémon gimmick de la zone* **{self.gimmick_inventory.get_zone(selected_region)} "
                    f"({selected_region})** *a été révélé. Il s'agit de* "
                    f"**{self.gimmick_inventory.get_pokemon(selected_region)}**.")
                await self.item_channel.send(message)

                # Confirmation message
                await self.ctx.send("Gimmick révélé !")
                return

            # For other teams, add zone to list of seen gimmicks
            target_inv = target_team.inventory_manager.gimmick_inventory
            self.gimmick_inventory.see(target_team.name, target_inv.gimmicks[selected_region])
            target_inv.add_see_count(selected_region)

            # Save target inventory, edit message (original inventory is saved later)
            target_inv.save(TEAM_FOLDER, target_team.id)
            target_inv_msg = await target_item_channel.fetch_message(target_inv.message_id)
            await target_inv_msg.edit(content=target_inv.format_discord(target_team.name))

            # Send results
            origin_msg = (f"{item_manager.items['clairvoyance'].get_emoji(self.gold)} *Voilà ce que j'ai observé chez "
                          f"{target_team.name} :*\n"
                          f"**{target_inv.gimmicks[selected_region].zone}** ({selected_region})")
            target_msg = (f"{item_manager.items['clairvoyance'].get_emoji(self.gold)} *Une zone gimmick a été "
                          f"observée... "
                          f"Il s'agit de* **{target_inv.gimmicks[selected_region].zone}** ({selected_region})")
            await self.item_channel.send(origin_msg)
            await target_item_channel.send(target_msg)

            # Update loop counter
            n_loop -= 1

    def get_valid_clairvoyance_regions(self) -> Dict[str, List[str]]:
        valid_teams = {}
        for team in team_manager.teams:
            team_inst = team_manager.teams[team]
            curr_inv = team_inst.inventory_manager.gimmick_inventory
            team_name = team_inst.name

            for region in curr_inv.contents:
                # For team that uses Clairvoyance, only add locked gimmicks
                # Don't add current team for gold clairvoyance
                if self.team.id == team_inst.id and (self.gold or curr_inv.is_unlock(region)):
                    continue

                # For other teams, add gimmicks that are not found and not already seen
                if (self.team.id != team_inst.id
                        and (curr_inv.is_found(region) or self.gimmick_inventory.is_seen(team_name, region))):
                    continue

                if team in valid_teams:
                    valid_teams[team].append(region)
                else:
                    valid_teams[team] = [region]

        return valid_teams
