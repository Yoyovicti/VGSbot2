import interactions

from commands.item_command import ItemCommand
from init_config import TEAM_FOLDER, item_manager
from init_emoji import REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N
from reaction_manager import ReactionManager


class ClassicItemCommand(ItemCommand):
    def __init__(self, bot: interactions.Client, ctx: interactions.SlashContext, item: str, param: str, qty: int = 1,
                 gold: bool = False, safe: bool = False):
        super().__init__(bot, ctx)
        self.item = item
        self.param = param
        self.qty = qty
        self.gold = gold
        self.safe = safe

    async def run(self):
        success = await self.load_team_info()
        if not success:
            return

        if self.param == "add":
            await self.run_add()
            return
        if self.param == "remove":
            await self.run_remove()
            return

    async def run_add(self) -> bool:
        # Add item and save to memory
        self.item_inventory.add(self.item, self.qty, self.gold, self.safe)
        self.item_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message and send to item channel
        inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
        await inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))
        message = f"{item_manager.items[self.item].get_emoji(self.gold)} x{self.qty}"
        if self.safe:
            message += " (non volable)"
        await self.item_channel.send(message + " ajouté à l'inventaire !")

        # Confirmation message
        await self.ctx.send("Inventaire mis à jour !")
        return True

    async def run_remove(self) -> bool:
        # Check quantity
        if self.item_inventory.quantity(self.item, self.gold, self.safe) < self.qty:
            return await self.run_remove_safe_checks()

        # Remove item and save inventory
        self.item_inventory.remove(self.item, self.qty, self.gold, self.safe)
        self.item_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message
        inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
        await inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))

        # Send messages
        await self.item_channel.send(
            f"{item_manager.items[self.item].get_emoji(self.gold)} x{self.qty} retiré de l'inventaire !")
        await self.ctx.send("Inventaire mis à jour !")

        return True

    async def run_remove_safe_checks(self) -> bool:
        classic_qty = self.item_inventory.quantity(self.item)

        if self.gold or self.safe or classic_qty + self.item_inventory.quantity(self.item, safe=True) < self.qty:
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
        self.item_inventory.remove(self.item, classic_qty)
        self.item_inventory.remove(self.item, self.qty - classic_qty, safe=True)
        self.item_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory
        inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
        await inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))

        # Send messages
        await self.item_channel.send(f"{item_manager.items[self.item].get_emoji()} x{self.qty} retiré de l'inventaire !")
        await self.ctx.send("Inventaire mis à jour !")

        return True
