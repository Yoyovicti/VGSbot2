import interactions

from init_config import GUILD_IDS, TEAM_FOLDER, team_manager
from init_emoji import REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N
from reaction_manager import ReactionManager


class InventoryExtension(interactions.Extension):
    INVENTORY_COMMAND_OPTIONS = [
        interactions.SlashCommandOption(
            name="opération",
            description="Opération à réaliser sur l'inventaire",
            type=interactions.OptionType.STRING,
            required=True,
            argument_name="ope",
            choices=[
                interactions.SlashCommandChoice(name="créer", value="init"),
                interactions.SlashCommandChoice(name="suppr", value="delete"),
                interactions.SlashCommandChoice(name="vider", value="clear")
            ]
        ),
    ]

    def __init__(self, bot: interactions.Client):
        super().add_ext_auto_defer()

    @interactions.slash_command(
        name="inventaire",
        description="Effectue une action sur les inventaires",
        scopes=GUILD_IDS,
        options=INVENTORY_COMMAND_OPTIONS,
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="objet",
        sub_cmd_description="Gérer l'inventaire d'objets"
    )
    async def item_inventory_command(self, ctx: interactions.SlashContext, ope: str):
        if ope == "init":
            await self.run_init(ctx, "item")
            return
        if ope == "delete":
            await self.run_delete(ctx, "item")
            return
        if ope == "clear":
            await self.run_clear(ctx, "item")
            return

    @interactions.slash_command(
        name="inventaire",
        description="Effectue une action sur les inventaires",
        scopes=GUILD_IDS,
        options=INVENTORY_COMMAND_OPTIONS,
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="mission",
        sub_cmd_description="Gérer l'inventaire de missions"
    )
    async def mission_inventory_command(self, ctx: interactions.SlashContext, ope: str):
        if ope == "init":
            await self.run_init(ctx, "mission")
            return
        if ope == "delete":
            await self.run_delete(ctx, "mission")
            return
        if ope == "clear":
            await self.run_clear(ctx, "mission")
            return

    @interactions.slash_command(
        name="inventaire",
        description="Effectue une action sur les inventaires",
        scopes=GUILD_IDS,
        options=INVENTORY_COMMAND_OPTIONS,
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="quete",
        sub_cmd_description="Gérer l'inventaire de quêtes"
    )
    async def quest_inventory_command(self, ctx: interactions.SlashContext, ope: str):
        if ope == "init":
            await self.run_init(ctx, "quest")
            return
        if ope == "delete":
            await self.run_delete(ctx, "quest")
            return
        if ope == "clear":
            await self.run_clear(ctx, "quest")
            return

    @interactions.slash_command(
        name="inventaire",
        description="Effectue une action sur les inventaires",
        scopes=GUILD_IDS,
        options=INVENTORY_COMMAND_OPTIONS,
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="gimmick",
        sub_cmd_description="Gérer la liste de gimmicks"
    )
    async def gimmick_inventory_command(self, ctx: interactions.SlashContext, ope: str):
        if ope == "init":
            await self.run_init(ctx, "gimmick")
            return
        if ope == "delete":
            await self.run_delete(ctx, "gimmick")
            return
        if ope == "clear":
            await self.run_clear(ctx, "gimmick")
            return

    async def run_init(self, ctx: interactions.SlashContext, inv_type: str):
        # Load team
        team = team_manager.get_team(str(ctx.channel_id))
        if team is None:
            await ctx.send("Erreur: Équipe non trouvée. Assurez-vous d'utiliser la commande dans le bon channel.")
            return

        # Load inventory
        inventory = team.inventory_manager.get_inventory(inv_type)
        if inventory is None:
            await ctx.send("Erreur: Commande non implémentée.")
            return
        if inventory.initialized:
            await ctx.send("Erreur: L'inventaire existe déjà.")
            return

        # Send message in item channel
        item_channel = await self.bot.fetch_channel(team.item_channel_id)
        item_inv_msg = await item_channel.send(inventory.format_discord(team.name))
        await item_inv_msg.pin()

        # Init item inventory and save in memory
        inventory.init(str(item_inv_msg.id))
        inventory.save(TEAM_FOLDER, team.id)

        # Confirmation message
        await ctx.send("Inventaire initialisé !")

    async def run_delete(self, ctx: interactions.SlashContext, inv_type: str):
        # Load team
        team = team_manager.get_team(str(ctx.channel_id))
        if team is None:
            await ctx.send("Erreur: Équipe non trouvée. Assurez-vous d'utiliser la commande dans le bon channel.")
            return

        # Load inventory
        inventory = team.inventory_manager.get_inventory(inv_type)
        if inventory is None:
            await ctx.send("Erreur: Commande non implémentée.")
            return
        if not inventory.initialized:
            await ctx.send("Erreur: L'inventaire n'est pas initialisé.")
            return

        # Confirmation step
        warning_msg = await ctx.send("Êtes-vous sûr de vouloir réaliser cette opération ? Il n'y a pas de retour en "
                                     "arrière !")
        reaction_manager = ReactionManager(warning_msg, [REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N])
        reaction = await reaction_manager.run()
        if reaction != REGIONAL_INDICATOR_O:
            await ctx.send("Opération annulée.")
            return

        # Delete message in item channel
        item_channel = await self.bot.fetch_channel(team.item_channel_id)
        item_message = await item_channel.fetch_message(inventory.message_id)
        await item_channel.delete_message(item_message)

        # Delete item inventory
        inventory.delete(TEAM_FOLDER, team.id)

        # Confirmation message
        await ctx.send("Inventaire supprimé !")

    async def run_clear(self, ctx: interactions.SlashContext, inv_type: str):
        # Load team
        team = team_manager.get_team(str(ctx.channel_id))
        if team is None:
            await ctx.send("Erreur: Équipe non trouvée. Assurez-vous d'utiliser la commande dans le bon channel.")
            return

        # Load inventory
        inventory = team.inventory_manager.get_inventory(inv_type)
        if inventory is None:
            await ctx.send("Erreur: Commande non implémentée.")
            return
        if not inventory.initialized:
            await ctx.send("Erreur: L'inventaire n'est pas initialisé.")
            return

        # Confirmation step
        warning_msg = await ctx.send("Êtes-vous sûr de vouloir réaliser cette opération ? Il n'y a pas de retour en "
                                     "arrière !")
        reaction_manager = ReactionManager(warning_msg, [REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N])
        reaction = await reaction_manager.run()
        if reaction != REGIONAL_INDICATOR_O:
            await ctx.send("Opération annulée.")
            return

        # Clear inventory contents in memory
        inventory.clear()
        inventory.save(TEAM_FOLDER, team.id)

        # Edit message in item channel
        item_channel = await self.bot.fetch_channel(team.item_channel_id)
        item_message = await item_channel.fetch_message(inventory.message_id)
        await item_message.edit(content=inventory.format_discord(team.name))

        # Confirmation message
        await ctx.send("Inventaire vidé !")
