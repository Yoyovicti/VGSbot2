from typing import List

import interactions

from commands.item_command import ItemCommand
from init_config import gimmick_manager, TEAM_FOLDER, item_manager, VGS_FOLDER
from init_emoji import REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N
from manager.reaction_manager import ReactionManager


class ClairvoyanceCommand(ItemCommand):
    def __init__(self, bot: interactions.Client, ctx: interactions.SlashContext, list_name: str, gold: bool = False,
                 safe: bool = False):
        super().__init__(bot, ctx)

        self.gimmick_inventory = None
        self.gimmick_list = None

        self.list_name = list_name
        self.gold = gold
        self.safe = safe

    async def load_team_info(self) -> bool:
        if not await super().load_team_info():
            return False

        self.gimmick_inventory = gimmick_manager.gimmick_list_inventory
        if not self.gimmick_inventory.initialized:
            await self.ctx.send("Erreur: La liste de gimmicks n'est pas initialisée.")
            return False

        self.gimmick_list = self.gimmick_inventory.contents[self.list_name]
        return True

    async def run(self):
        success = await self.load_team_info()
        if not success:
            return

        item_name = "clairvoyance"

        # Verify quantity, ask to use safe items if needed
        if self.item_inventory.quantity(item_name, self.gold, self.safe) < 1:
            classic_qty = self.item_inventory.quantity(item_name)
            safe_qty = self.item_inventory.quantity(item_name, safe=True)
            if self.gold or self.safe or classic_qty + safe_qty < 1:
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

        # Run clairvoyance
        if self.gimmick_list.current_step >= len(self.gimmick_list.gimmicks):
            await self.ctx.send("Erreur: Tous les Pokémon de la liste sont déjà révélés.")
            return

        if self.gimmick_list.get_found(self.gimmick_list.current_step + 1):
            await self.ctx.send("Erreur: Le gimmick a déjà été validé avec une Clairvoyance dorée. Il est nécessaire de valider l'étape en cours avant de progresser.")
            return

        if self.team.name in self.gimmick_list.unlocked:
            await self.ctx.send("Erreur: Le prochain gimmick a déjà été observé pour cette liste.")
            return

        if self.team.name in self.gimmick_list.seen and not self.gold:
            await self.ctx.send("Erreur: Le prochain gimmick a déjà été observé pour cette liste.")
            return

        await self.run_clairvoyance()

        # Save inventories, edit message
        self.item_inventory.save(TEAM_FOLDER, self.team.id)
        self.gimmick_inventory.save(VGS_FOLDER)
        inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
        await inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))

        # Confirmation message
        await self.ctx.send(f"{item_manager.items['clairvoyance'].get_emoji(self.gold)} Gimmick révélé !")

    async def run_clairvoyance(self):
        item_name = "clairvoyance"

        # Remove clairvoyance from inventory
        if self.gold or self.safe:
            self.item_inventory.remove(item_name, gold=self.gold, safe=self.safe)
        else:
            classic_qty = self.item_inventory.quantity(item_name)
            if classic_qty <= 0:
                self.item_inventory.remove(item_name, safe=True)
            else:
                self.item_inventory.remove(item_name)

        if self.gold:
            self.gimmick_inventory.set_unlock(self.team.name, self.list_name)
        else:
            self.gimmick_inventory.set_observed(self.list_name, self.team.name)

        # Send results
        seen_gimmick = self.gimmick_list.gimmicks[self.gimmick_list.current_step]
        print(seen_gimmick.pokemon, seen_gimmick.version, seen_gimmick.method, seen_gimmick.zone, seen_gimmick.bonus, seen_gimmick.note)
        origin_msg = f"{item_manager.items['clairvoyance'].get_emoji(self.gold)} *Voilà le Pokémon que j'ai observé dans la liste {self.list_name} :* \n"
        origin_msg += f"- Pokémon : **{seen_gimmick.pokemon}**\n"
        origin_msg += f"- Version : *{seen_gimmick.version}*\n" if seen_gimmick.version != "" else ""
        origin_msg += f"- Méthode : *{seen_gimmick.method}*\n" if seen_gimmick.method != "" else ""
        origin_msg += f"- Zone : *{seen_gimmick.zone}*\n" if seen_gimmick.zone != "" else ""
        origin_msg += f"- Bonus : ***x{seen_gimmick.bonus}***\n"
        origin_msg += f"- Note : *{seen_gimmick.note}*\n" if seen_gimmick.note != "" else ""

        await self.item_channel.send(origin_msg)

    def get_valid_clairvoyance_lists(self, gold: bool = False) -> List[str]:
        valid_lists = []
        for entry in self.gimmick_inventory.contents:
            gimmick_list = self.gimmick_inventory.contents[entry]

            if self.team.name in gimmick_list.unlocked:
                continue

            if self.team.name in gimmick_list.seen and not gold:
                continue

            valid_lists.append(entry)

        return valid_lists
