import interactions

from init_config import team_manager


class ItemCommand:
    def __init__(self, bot: interactions.Client, ctx: interactions.SlashContext):
        self.bot = bot
        self.ctx = ctx

        self.team = None
        self.item_inventory = None
        self.item_channel = None

    async def run(self):
        raise NotImplementedError

    async def load_team_info(self) -> bool:
        self.team = team_manager.get_team(str(self.ctx.channel_id))
        if self.team is None:
            await self.ctx.send("Erreur: Équipe non trouvée. Assurez-vous d'utiliser la commande dans le bon channel.")
            return False

        self.item_inventory = self.team.inventory_manager.item_inventory
        if not self.item_inventory.initialized:
            await self.ctx.send("Erreur: L'inventaire n'est pas initialisé.")
            return False

        self.item_channel = await self.bot.fetch_channel(self.team.item_channel_id)
        if self.item_channel is None:
            await self.ctx.send("Erreur: Salon objets non trouvé pour l'équipe sélectionnée.")
            return False

        return True
