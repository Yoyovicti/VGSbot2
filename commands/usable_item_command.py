from typing import Dict, List

import interactions
from numpy import random

from logic.boo import Boo
from logic.cadoizo import Cadoizo
from commands.item_command import ItemCommand
from init_config import item_manager, TEAM_FOLDER, ORBE_SUCCESS_RATE, team_manager, roll_manager, GOLD_ORBE_SUCCESS_RATE
from init_emoji import REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N, KEYCAP_NUMBERS, CROSS_MARK
from manager.reaction_manager import ReactionManager


class UsableItemCommand(ItemCommand):
    def __init__(self, bot: interactions.Client, ctx: interactions.SlashContext, param: str, qty: int = 1,
                 gold: bool = False, safe: bool = False, enable_save: bool = True):
        super().__init__(bot, ctx)

        self.command_map = {
            "fulgurorbe": self.run_orbe_command,
            "boo": self.run_boo_command,
            "clairvoyance": self.run_clairvoyance_command,
            "ar": self.run_ar_command,
            "cadoizo": self.run_cadoizo_command,
            "champi": self.run_champi_command
        }

        self.gimmick_inventory = None

        self.param = param
        self.qty = qty
        self.gold = gold
        self.safe = safe

        self.enable_save = enable_save

    async def load_team_info(self) -> bool:
        if not await super().load_team_info():
            return False

        self.gimmick_inventory = self.team.inventory_manager.gimmick_inventory
        if not self.gimmick_inventory.initialized:
            await self.ctx.send("Erreur: La liste de gimmicks n'est pas initialisée.")
            return False

        return True

    async def run(self):
        if self.param in self.command_map:
            await self.command_map[self.param]()

    async def run_orbe_command(self):
        success = await self.load_team_info()
        if not success:
            return

        # Remove item from inventory
        success = await self.run_remove()
        if not success:
            return
        await self.ctx.send("Inventaire mis à jour !")

        # Use item
        for _ in range(self.qty):
            await self.run_orbe(self.gold)

    async def run_orbe(self, gold: bool = False):
        rng = random.Generator(random.MT19937())
        r = rng.random()

        message = (f"{item_manager.items['fulgurorbe'].get_emoji(gold)} *a manqué sa cible et s'est "
                   f"évaporée...*")
        if gold:
            message = (f"{item_manager.items['fulgurorbe'].get_emoji(gold)} *lancée avec "
                       f"succès !*\n")
            gold_message = f"*Elle échouera si une* {item_manager.items['etoile'].get_emoji(gold=True)} *est lancée...*"
            if r < GOLD_ORBE_SUCCESS_RATE:
                gold_message = (f"*Elle passera également à travers une* "
                                f"{item_manager.items['etoile'].get_emoji(gold=True)} *!*")
            message += gold_message

        else:
            if r < ORBE_SUCCESS_RATE:
                message = (f"{item_manager.items['fulgurorbe'].get_emoji(gold)} *lancée avec "
                           f"succès !*")

        await self.item_channel.send(message)
        await self.ctx.send(message)

    async def run_boo_command(self):
        # Load origin team info
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

        # Run each boo
        for _ in range(self.qty):
            await self.run_boo(self.gold)

        # Save inventory, edit message
        self.item_inventory.save(TEAM_FOLDER, self.team.id)
        origin_inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
        await origin_inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))

        # Confirmation message
        await self.ctx.send(f"{item_manager.items['boo'].get_emoji(self.gold)} Inventaires mis à jour !")

    async def run_boo(self, gold: bool = False, remove_boo: bool = True, cancel_option: bool = True):
        # Load valid teams
        valid_teams = []
        for team in team_manager.teams:
            team_inst = team_manager.teams[team]
            item_inv = team_inst.inventory_manager.item_inventory
            if team == self.team.id or not item_inv.initialized:
                continue
            valid_teams.append(team)

        # Get number of loops
        n_loop = 1
        if gold:
            n_loop = len(valid_teams)

        for c in range(n_loop):
            # Select item
            item_emojis = await self.get_valid_boo_target_items()
            item_select_string = "Veuillez sélectionner l'objet que vous désirez voler :"
            item_select_message = await self.item_channel.send(item_select_string)
            await self.ctx.send("*En attente du choix des participants...*")

            reaction_list = item_emojis
            if cancel_option and c <= 0:
                reaction_list = [CROSS_MARK] + reaction_list
            item_reaction_manager = ReactionManager(item_select_message, reaction_list)
            target_item = await item_reaction_manager.run()

            # Cancel
            if target_item == CROSS_MARK:
                await item_select_message.reply("Opération annulée.")
                await self.ctx.send("Opération annulée.")
                return

            # Select team
            team_select_string = "Veuillez sélectionner l'équipe visée:\n\n"
            for i in range(len(valid_teams)):
                team_select_string += f"{KEYCAP_NUMBERS[i]} {team_manager.teams[valid_teams[i]].name}\n"
            team_select_message = await self.item_channel.send(team_select_string)

            reaction_list = KEYCAP_NUMBERS[:len(valid_teams)]
            if cancel_option and c <= 0:
                reaction_list = [CROSS_MARK] + reaction_list
            team_reaction_manager = ReactionManager(team_select_message, reaction_list)
            selected_reaction = await team_reaction_manager.run()

            # Cancel
            if selected_reaction == CROSS_MARK:
                await team_select_message.reply("Opération annulée.")
                await self.ctx.send("Opération annulée.")
                return

            # Remove target from valid teams (for gold boo)
            target_team = valid_teams[KEYCAP_NUMBERS.index(selected_reaction)]
            valid_teams.remove(target_team)

            # Get team instance
            target_team = team_manager.teams[target_team]

            # Check target item channel
            target_item_channel = await self.bot.fetch_channel(target_team.item_channel_id)
            if target_item_channel is None:
                await team_select_message.reply("Opération annulée.")
                await self.ctx.send("Erreur: Salon objets non trouvé pour la cible.")
                continue

            # Remove boo from inventory on last pass
            if remove_boo and c >= n_loop - 1:
                if gold or self.safe:
                    self.item_inventory.remove(self.param, gold=gold, safe=self.safe)
                else:
                    classic_qty = self.item_inventory.quantity(self.param)
                    if classic_qty <= 0:
                        self.item_inventory.remove(self.param, safe=True)
                    else:
                        self.item_inventory.remove(self.param)

            # Process boo
            boo = Boo(gold)

            sent_item = "clone"
            target_inventory = target_team.inventory_manager.item_inventory
            if target_inventory.quantity(sent_item) <= 0:
                if target_inventory.quantity(target_item) <= 0:
                    origin_msg = f"{boo.name} : *J'ai rien trouvé chef !*"
                    target_msg = (
                        f"{boo.name} : *Je passais chercher* {item_manager.items[target_item].get_emoji()} *par ici, "
                        f"mais il semblerait qu'il n'y ait rien. Bon ben je m'en vais snif...*")
                    await self.item_channel.send(origin_msg)
                    await target_item_channel.send(target_msg)

                    # Confirmation message
                    await self.ctx.send(
                        f"{item_manager.items['boo'].get_emoji(gold)} Aucune modification effectuée !")
                    continue

                # Boo successful: set item to send
                sent_item = target_item

            # All non-safe items of the type are stolen with gold boo
            qty_stolen = 1
            if gold:
                qty_stolen = target_inventory.quantity(sent_item)

            # Process inventories
            self.item_inventory.add(sent_item, qty_stolen)
            target_inventory.remove(sent_item, qty_stolen)

            # Save target inventory, edit inventory message (original inventory is saved later)
            target_inventory.save(TEAM_FOLDER, target_team.id)
            target_inv_msg = await target_item_channel.fetch_message(target_inventory.message_id)
            await target_inv_msg.edit(content=target_inventory.format_discord(target_team.name))

            # Send results
            origin_msg = f"{boo.name} : *Je reviens avec* {item_manager.items[sent_item].get_emoji()} "
            if gold:
                origin_msg += f"x{qty_stolen} "
            origin_msg += "*!*"
            target_msg = (f"{boo.name} : *Coucou, j'ai vu que vous m'aviez laissé* "
                          f"{item_manager.items[sent_item].get_emoji()} ")
            if gold:
                target_msg += f"x{qty_stolen}"
            target_msg += f"*, c'est vraiment gentil de votre part ! Allez bisous les nuls héhéhé...*"
            await self.item_channel.send(origin_msg)
            await target_item_channel.send(target_msg)

    async def get_valid_boo_target_items(self):
        # Get item emojis with corresponding reference to name
        items = item_manager.items
        item_emojis = []
        for item in items:
            if not items[item].stealable:
                continue

            classic_qty = self.item_inventory.quantity(item)
            safe_qty = self.item_inventory.quantity(item, safe=True)
            max_capacity = item_manager.items[item].max_capacity
            if -1 < max_capacity <= classic_qty + safe_qty:
                continue

            item_emojis.append(items[item].get_emoji())
        return item_emojis

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
            await self.run_clairvoyance(self.gold)

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

    async def run_clairvoyance(self, gold: bool = False, remove_clairvoyance: bool = True, cancel_option: bool = True):
        # Load valid teams
        valid_regions = self.get_valid_clairvoyance_regions(gold)
        valid_teams = list(valid_regions)

        # Get number of loops
        n_loop = 1
        if gold:
            n_loop = len(valid_teams)

        for c in range(n_loop):
            # Select team
            team_select_string = (f"{item_manager.items['clairvoyance'].get_emoji(gold)} Veuillez sélectionner "
                                  f"l'équipe visée:\n\n")
            for i in range(len(valid_teams)):
                team_select_string += f"{KEYCAP_NUMBERS[i]} {team_manager.teams[valid_teams[i]].name}\n"
            team_select_message = await self.item_channel.send(team_select_string)
            await self.ctx.send("*En attente du choix des participants...*")

            reaction_list = KEYCAP_NUMBERS[:len(valid_teams)]
            if cancel_option and c <= 0:
                reaction_list = [CROSS_MARK] + reaction_list
            team_reaction_manager = ReactionManager(team_select_message, reaction_list)
            selected_reaction = await team_reaction_manager.run()

            # Cancel
            if selected_reaction == CROSS_MARK:
                await team_select_message.reply("Opération annulée.")
                await self.ctx.send("Opération annulée.")
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
            if remove_clairvoyance and c >= n_loop - 1:
                if gold or self.safe:
                    self.item_inventory.remove(self.param, gold=gold, safe=self.safe)
                else:
                    classic_qty = self.item_inventory.quantity(self.param)
                    if classic_qty <= 0:
                        self.item_inventory.remove(self.param, safe=True)
                    else:
                        self.item_inventory.remove(self.param)

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
            origin_msg = (f"{item_manager.items['clairvoyance'].get_emoji(gold)} *Voilà ce que j'ai observé chez "
                          f"{target_team.name} :*\n"
                          f"**{target_inv.gimmicks[selected_region].zone}** ({selected_region})")
            target_msg = (f"{item_manager.items['clairvoyance'].get_emoji(gold)} *Une zone gimmick a été "
                          f"observée... "
                          f"Il s'agit de* **{target_inv.gimmicks[selected_region].zone}** ({selected_region})")
            await self.item_channel.send(origin_msg)
            await target_item_channel.send(target_msg)

    def get_valid_clairvoyance_regions(self, gold: bool) -> Dict[str, List[str]]:
        valid_teams = {}
        for team in team_manager.teams:
            team_inst = team_manager.teams[team]
            curr_inv = team_inst.inventory_manager.gimmick_inventory
            team_name = team_inst.name

            for region in curr_inv.contents:
                # For team that uses Clairvoyance, only add locked gimmicks
                # Don't add current team for gold clairvoyance
                if self.team.id == team_inst.id and (gold or curr_inv.is_unlock(region)):
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

    async def run_ar_command(self):
        # Load origin team info
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

        # Run each AR
        should_save = False
        for _ in range(self.qty):
            if await self.run_ar():
                should_save = True

        # Edit inventory message
        origin_inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
        await origin_inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))

        # Save inventory
        if self.enable_save and should_save:
            self.item_inventory.save(TEAM_FOLDER, self.team.id)

            # Send confirmation
            await self.item_channel.send(
                f"{item_manager.items[self.param].get_emoji(self.gold)} x{self.qty} retiré de l'inventaire !")
            await self.ctx.send("Inventaire mis à jour !")

    async def run_ar(self) -> bool:
        # Ask for which item to transform
        item_emojis = [
            item_manager.items[item].get_emoji(gold=True)
            for item in item_manager.items
            if item_manager.items[item].transform_gold
        ]
        item_select_string = "Veuillez sélectionner l'objet doré à utiliser :"
        item_select_message = await self.item_channel.send(item_select_string)
        await self.ctx.send("*En attente du choix des participants...*")
        item_reaction_manager = ReactionManager(item_select_message, [CROSS_MARK] + item_emojis)
        target_item = await item_reaction_manager.run()

        # Cancel
        if target_item == CROSS_MARK:
            await item_select_message.reply("Opération annulée.")
            await self.ctx.send("Opération annulée.")
            return False

        # Remove AR from inventory
        if self.gold or self.safe:
            self.item_inventory.remove(self.param, gold=self.gold, safe=self.safe)
        else:
            classic_qty = self.item_inventory.quantity(self.param)
            if classic_qty <= 0:
                self.item_inventory.remove(self.param, safe=True)
            else:
                self.item_inventory.remove(self.param)

        target_item = target_item[4:]
        # Process Fulgurorbe
        if target_item == "fulgurorbe":
            await self.run_orbe(gold=True)

        # Process Boo
        if target_item == "boo":
            await self.run_boo(gold=True, remove_boo=False, cancel_option=False)

        # Process Clairvoyance
        if target_item == "clairvoyance":
            await self.run_clairvoyance(gold=True, remove_clairvoyance=False, cancel_option=False)

            # Save and edit gimmick inventory
            self.gimmick_inventory.save(TEAM_FOLDER, self.team.id)
            gimmick_inv_msg = await self.item_channel.fetch_message(self.gimmick_inventory.message_id)
            await gimmick_inv_msg.edit(content=self.gimmick_inventory.format_discord(self.team.name))

        return True

    async def run_cadoizo_command(self):
        # Load origin team info
        success = await self.load_team_info()
        if not success:
            return

        should_save = False
        await self.item_channel.send(f"<@&{self.team.role_id}>")
        for _ in range(self.qty):
            if await self.run_cadoizo(self.gold):
                should_save = True

        # Save inventory
        if self.enable_save and should_save:
            self.item_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message and send to item channel
        inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
        await inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))

    async def run_cadoizo(self, gold: bool = False, cancel_option: bool = True) -> bool:
        cancel_message = "*Tirage annulé*"

        cadoizo = Cadoizo(self.item_inventory, gold)
        choices = cadoizo.run()

        contents_message = f"*Le* {item_manager.items['cadoizo'].get_emoji(gold)} *contient :* "
        for i in range(cadoizo.n_items):
            if gold:
                contents_message += f"\n{KEYCAP_NUMBERS[i]} {choices[i]}"
                continue
            contents_message += f"{item_manager.items[choices[i]].get_emoji()} "
        contents_message += "\n"
        await self.ctx.send(contents_message + "*En attente du choix des participants...*")

        cadoizo_message = await self.item_channel.send(
            f"{item_manager.items['cadoizo'].get_emoji(gold)} "
            f"*Choisissez un lot avec les réactions ci-dessous :*"
        )
        reaction_choices = KEYCAP_NUMBERS[:cadoizo.n_items]
        if cancel_option:
            reaction_choices = [CROSS_MARK] + reaction_choices
        if (not gold and self.item_inventory.quantity("ar") + self.item_inventory.quantity("ar", safe=True) +
                self.item_inventory.quantity("ar", gold=True) > 0):
            reaction_choices += [f"{item_manager.items['cadoizo'].get_emoji(True)}"]

        reaction_manager = ReactionManager(cadoizo_message, reaction_choices)
        selected_reaction = await reaction_manager.run()

        if selected_reaction == CROSS_MARK:
            await cadoizo_message.reply(contents_message + cancel_message)
            await self.ctx.send(cancel_message)
            return False

        should_save = False
        if selected_reaction == "goldcadoizo":
            if self.item_inventory.quantity("ar") > 0:
                self.item_inventory.remove("ar")
            elif self.item_inventory.quantity("ar", safe=True):
                self.item_inventory.remove("ar", safe=True)
            else:
                self.item_inventory.remove("ar", gold=True)
            should_save = True

            await self.run_cadoizo(gold=True, cancel_option=False)
            return should_save

        choice = choices[KEYCAP_NUMBERS.index(selected_reaction)]

        # Gold Cadoizo
        if gold:
            contents = roll_manager.gold_cadoizo[choice]
            result_message = (f"*Lot obtenu :* {choice}\n"
                              f"*Objet(s) obtenus :*\n")
            boss_mention = False

            for elem in contents:
                elem_item = elem["item"]
                elem_qty = elem["qty"]
                elem_is_gold = elem["gold"] == 1

                result_message += f"{item_manager.items[elem_item].get_emoji(elem_is_gold)} x{elem_qty}\n"
                if elem_is_gold or not item_manager.items[elem_item].instant:
                    self.item_inventory.add(elem_item, qty=elem_qty, gold=elem_is_gold)
                    should_save = True
                    continue

                if elem_item == "carapacebleue" or elem_item == "eclair":
                    boss_mention = True

            await cadoizo_message.reply(contents_message + result_message)
            boss_message = result_message
            if boss_mention:
                boss_message += team_manager.get_boss_mention()
            await self.ctx.send(boss_message)

            # Process instant Cadoizo in kit:
            for elem in contents:
                if elem["item"] == "cadoizo":
                    for _ in range(elem["qty"]):
                        await self.run_cadoizo(gold=(elem["gold"] == 1), cancel_option=False)
                    should_save = True
                    continue
            return should_save

        # Add item to inventory
        if not item_manager.items[choice].instant:
            self.item_inventory.add(choice)
            should_save = True

        boss_mention = False
        if choice == "carapacebleue" or choice == "eclair":
            boss_mention = True

        # Send result message
        result_message = f"*Objet obtenu :* {item_manager.items[choice].get_emoji()}"
        await cadoizo_message.reply(contents_message + result_message)
        boss_message = result_message
        if boss_mention:
            boss_message += team_manager.get_boss_mention()
        await self.ctx.send(boss_message)
        return should_save

    async def run_champi_command(self):
        self.team = team_manager.get_team(str(self.ctx.channel_id))
        if self.team is None:
            await self.ctx.send("Erreur: Équipe non trouvée. Assurez-vous d'utiliser la commande dans le bon channel.")
            return

        valid_teams = [team for team in team_manager.teams if team != self.team.id]

        for _ in range(self.qty):
            await self.run_champi(valid_teams)

    async def run_champi(self, valid_teams):
        rng = random.Generator(random.MT19937())
        target_team = rng.choice(valid_teams)

        await self.ctx.send(f"{item_manager.items['champinocif'].get_emoji()} *Les points du shiny s'en vont vers "
                            f"l'équipe* **{team_manager.teams[target_team].name}**")

    async def run_remove(self) -> bool:
        # Check quantity
        if self.item_inventory.quantity(self.param, self.gold, self.safe) < self.qty:
            return await self.run_remove_safe_checks()

        # Remove item and save inventory
        self.item_inventory.remove(self.param, self.qty, self.gold, self.safe)
        self.item_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message
        inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
        await inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))

        return True

    async def run_remove_safe_checks(self) -> bool:
        classic_qty = self.item_inventory.quantity(self.param)

        if self.gold or self.safe or classic_qty + self.item_inventory.quantity(self.param, safe=True) < self.qty:
            await self.ctx.send("Erreur: L'inventaire ne contient pas assez de cet objet.")
            return False

        # Ask for confirmation in case safe items will be removed
        warning_msg = await self.ctx.send("Cette opération va retirer des objets non volables de l'inventaire. "
                                          "Souhaitez-vous continuer ?")
        reaction_manager = ReactionManager(warning_msg, [REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N])
        reaction = await reaction_manager.run()
        if reaction != REGIONAL_INDICATOR_O:
            await self.ctx.send("Opération annulée.")
            return False

        # Remove items from inventory and save
        self.item_inventory.remove(self.param, classic_qty)
        self.item_inventory.remove(self.param, self.qty - classic_qty, safe=True)
        self.item_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory
        inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
        await inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))

        return True
