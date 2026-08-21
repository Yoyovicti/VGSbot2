import interactions
from numpy import random

from init_config import team_manager, TEAM_FOLDER, item_manager

CONFLICTING_ITEMS = {
    "clone": "mrsaturn",
    "mrsaturn": "clone"
}


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


async def resolve_clone_saturn_conflict(bot: interactions.Client, team, inventory, item_channel,
                                        arrived_item: str) -> str:
    """
    Le Clone et MrSaturn ne peuvent pas cohabiter dans un même inventaire. Si l'un arrive alors que
    l'autre est déjà présent, ce dernier est expulsé vers une équipe adverse choisie aléatoirement.
    Retourne l'id de l'objet expulsé, ou "" si aucun conflit n'a été déclenché.
    """
    if arrived_item not in CONFLICTING_ITEMS:
        return ""

    resident_item = CONFLICTING_ITEMS[arrived_item]
    classic_qty = inventory.quantity(resident_item)
    safe_qty = inventory.quantity(resident_item, safe=True)
    gold_qty = inventory.quantity(resident_item, gold=True)
    if classic_qty + safe_qty + gold_qty <= 0:
        return ""

    # Pick a random target team to receive the expelled item
    valid_teams = [t for t in team_manager.teams if t != team.id]
    rng = random.Generator(random.MT19937())
    target_team = team_manager.teams[rng.choice(valid_teams)]
    target_inventory = target_team.inventory_manager.item_inventory

    # Move every copy of the resident item to the target team, preserving buckets
    if classic_qty > 0:
        inventory.remove(resident_item, qty=classic_qty)
        target_inventory.add(resident_item, qty=classic_qty)
    if safe_qty > 0:
        inventory.remove(resident_item, qty=safe_qty, safe=True)
        target_inventory.add(resident_item, qty=safe_qty, safe=True)
    if gold_qty > 0:
        inventory.remove(resident_item, qty=gold_qty, gold=True)
        target_inventory.add(resident_item, qty=gold_qty, gold=True)

    # Save and notify origin team - item channel stays anonymous (no team name), bot channel gets the detail
    inventory.save(TEAM_FOLDER, team.id)
    origin_inv_msg = await item_channel.fetch_message(inventory.message_id)
    await origin_inv_msg.edit(content=inventory.format_discord(team.name))

    item_message = (f"{item_manager.items[arrived_item].get_emoji()} *chasse* "
                    f"{item_manager.items[resident_item].get_emoji()} *hors de sa vue*")
    await item_channel.send(item_message)

    origin_bot_channel = await bot.fetch_channel(team.bot_channel_id)
    if origin_bot_channel is not None:
        await origin_bot_channel.send(
            f"{item_manager.items[resident_item].get_emoji()} expulsé vers l'équipe **{target_team.name}**.")

    # Save and notify target team - item channel stays anonymous (no team name), bot channel gets the detail
    target_inventory.save(TEAM_FOLDER, target_team.id)
    target_item_channel = await bot.fetch_channel(target_team.item_channel_id)
    if target_item_channel is not None:
        target_inv_msg = await target_item_channel.fetch_message(target_inventory.message_id)
        await target_inv_msg.edit(content=target_inventory.format_discord(target_team.name))

        target_item_message = f"{item_manager.items[resident_item].get_emoji()} *a été expulsé chez vous*"
        await target_item_channel.send(target_item_message)

    target_bot_channel = await bot.fetch_channel(target_team.bot_channel_id)
    if target_bot_channel is not None:
        await target_bot_channel.send(
            f"{item_manager.items[resident_item].get_emoji()} reçu depuis l'équipe **{team.name}**.")

    return resident_item
