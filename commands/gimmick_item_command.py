import interactions

from commands.usable_item_command import UsableItemCommand
from definition.gimmick import Gimmick
from init_config import team_manager, TEAM_FOLDER, item_manager, gimmick_manager
from init_emoji import REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N
from manager.reaction_manager import ReactionManager


class GimmickItemCommand(UsableItemCommand):
    def __init__(self, bot: interactions.Client, ctx: interactions.SlashContext, param: str, qty: int = 1,
                 gold: bool = False, safe: bool = False, region: str = "", zone: str = "", pokemon: str = ""):
        super().__init__(bot, ctx, param, qty=qty, gold=gold, safe=safe)

        self.command_map["d6"] = self.run_d6_command

        self.region = region
        self.zone = zone
        self.pokemon = pokemon

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

                    # Send message and edit gimmick inventory message
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


