import interactions

from init_config import GUILD_IDS, team_manager, gimmick_manager, TEAM_FOLDER
from init_emoji import REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N
from reaction_manager import ReactionManager


# TODO Command to add or edit gimmick

class GimmickExtension(interactions.Extension):
    REGION_OPTION = interactions.SlashCommandOption(
        name="catégorie",
        description="La région du gimmick",
        type=interactions.OptionType.STRING,
        required=True,
        argument_name="cat",
        choices=[
            interactions.SlashCommandChoice(name=cat, value=cat)
            for cat in gimmick_manager.gimmicks[list(gimmick_manager.gimmicks)[0]]
        ]
    )

    TEAM_OPTION = interactions.SlashCommandOption(
        name="équipe",
        description="L'équipe concernée",
        type=interactions.OptionType.STRING,
        required=True,
        argument_name="team",
        choices=[
            interactions.SlashCommandChoice(name=team_manager.teams[team].name, value=team)
            for team in team_manager.teams
        ]
    )

    CANCEL_OPTION = interactions.SlashCommandOption(
        name="annuler",
        description="Inverser l'opération",
        type=interactions.OptionType.STRING,
        required=False,
        argument_name="cancel",
        choices=[
            interactions.SlashCommandChoice(name="oui", value="oui"),
            interactions.SlashCommandChoice(name="non", value="non")
        ]
    )

    def __init__(self, bot: interactions.Client):
        self.add_ext_auto_defer()

        self.team = None
        self.gimmick_inventory = None
        self.item_channel = None

    def init_team_info(self):
        self.team = None
        self.gimmick_inventory = None
        self.item_channel = None

    async def load_team_info(self, ctx: interactions.SlashContext) -> bool:
        self.init_team_info()

        self.team = team_manager.get_team(str(ctx.channel_id))
        if self.team is None:
            await ctx.send("Erreur: Équipe non trouvée. Assurez-vous d'utiliser la commande dans le bon channel.")
            return False

        self.gimmick_inventory = self.team.inventory_manager.gimmick_inventory
        if not self.gimmick_inventory.initialized:
            await ctx.send("Erreur: L'inventaire n'est pas initialisé.")
            return False

        self.item_channel = await self.bot.fetch_channel(self.team.item_channel_id)
        if self.item_channel is None:
            await ctx.send("Erreur: Salon objets non trouvé pour l'équipe sélectionnée.")
            return False

        return True

    @interactions.slash_command(
        name="gimmick",
        description="Effectue une action sur les gimmicks",
        scopes=GUILD_IDS,
        options=[
            REGION_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="révéler",
        sub_cmd_description="Révéler le Pokémon gimmick de liste"
    )
    async def gimmick_reveal_command(self, ctx: interactions.SlashContext, cat: str):
        success = await self.load_team_info(ctx)
        if not success:
            return

        if self.gimmick_inventory.get_unlock(cat):
            await ctx.send("Erreur. Ce gimmick a déjà été révélé.")
            return

        warning_msg = await ctx.send("Attention ! Le Pokémon gimmick sera révélé aux participants. Souhaitez-vous "
                                     "confirmer l'opération ?")
        reaction_manager = ReactionManager(warning_msg, [REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N])
        reaction = await reaction_manager.run()
        if reaction != REGIONAL_INDICATOR_O:
            await ctx.send("Opération annulée.")
            return

        # Unlock Pokémon in inventory and save
        self.gimmick_inventory.unlock(cat)
        self.gimmick_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message and send to item channel
        inv_msg = await self.item_channel.fetch_message(self.gimmick_inventory.message_id)
        await inv_msg.edit(content=self.gimmick_inventory.format_discord(self.team.name))
        message = (f"*Le Pokémon gimmick de la zone **{self.gimmick_inventory.get_zone(cat)} ({cat})** a été révélé. "
                   f"Il s'agit de* **{self.gimmick_inventory.get_pokemon(cat)}**")
        await self.item_channel.send(message)

        # Confirmation message
        await ctx.send("Gimmick révélé !")

    @interactions.slash_command(
        name="gimmick",
        description="Effectue une action sur les gimmicks",
        scopes=GUILD_IDS,
        options=[
            REGION_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="cacher",
        sub_cmd_description="Cache un gimmick de liste révélé. Ne devrait pas être utilisé en conditions réelles."
    )
    async def gimmick_hide_command(self, ctx: interactions.SlashContext, cat: str):
        success = await self.load_team_info(ctx)
        if not success:
            return

        if not self.gimmick_inventory.get_unlock(cat):
            await ctx.send("Erreur. Ce gimmick est déjà caché.")
            return

        # Hide Pokémon in inventory and save
        self.gimmick_inventory.unlock(cat, state=False)
        self.gimmick_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message
        inv_msg = await self.item_channel.fetch_message(self.gimmick_inventory.message_id)
        await inv_msg.edit(content=self.gimmick_inventory.format_discord(self.team.name))

        # Confirmation message
        await ctx.send("Gimmick caché !")

    @interactions.slash_command(
        name="gimmick",
        description="Effectue une action sur les gimmicks",
        scopes=GUILD_IDS,
        options=[
            TEAM_OPTION,
            REGION_OPTION,
            CANCEL_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="observer",
        sub_cmd_description="Observer la zone d'un gimmick adverse. Ne devrait pas être utilisé en conditions réelles."
    )
    async def gimmick_see_command(self, ctx: interactions.SlashContext, team: str, cat: str, cancel: str = "non"):
        success = await self.load_team_info(ctx)
        if not success:
            return

        # Fetch target team channel
        team_inst = team_manager.teams[team]
        target_item_channel = await self.bot.fetch_channel(team_inst.item_channel_id)
        if target_item_channel is None:
            await ctx.send("Erreur: Salon objets non trouvé pour l'équipe visée.")
            return False

        # Check that gimmick is not seen already
        should_cancel = cancel == "oui"
        if should_cancel and not self.gimmick_inventory.get_seen(team_inst.name, cat):
            await ctx.send("Erreur : Cette zone n'a pas été observée.")

        if not should_cancel and self.gimmick_inventory.get_seen(team_inst.name, cat):
            await ctx.send("Erreur : Cette zone a déjà été observée.")
            return

        # Add gimmick to seen gimmicks, update counter on target team
        target_inv = team_inst.inventory_manager.gimmick_inventory
        self.gimmick_inventory.see(team_inst.name, target_inv.gimmicks[cat], state=(not should_cancel))

        if should_cancel:
            target_inv.remove_see_count(cat)
        else:
            target_inv.add_see_count(cat)

        # Edit messages
        origin_inv_msg = await self.item_channel.fetch_message(self.gimmick_inventory.message_id)
        await origin_inv_msg.edit(content=self.gimmick_inventory.format_discord(self.team.name))
        target_inv_msg = await target_item_channel.fetch_message(target_inv.message_id)
        await target_inv_msg.edit(content=target_inv.format_discord(team_inst.name))

        # Save inventories
        self.gimmick_inventory.save(TEAM_FOLDER, self.team.id)
        target_inv.save(TEAM_FOLDER, team)

        # Confirmation message
        await ctx.send("Opération effectuée !")

    # @interactions.slash_command(
    #     name="gimmick",
    #     description="Effectue une action sur les gimmicks",
    #     scopes=GUILD_IDS,
    #     options=[
    #
    #     ],
    #     default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    #     dm_permission=False,
    #     sub_cmd_name="modifier",
    #     sub_cmd_description="Révéler le Pokémon gimmick de liste"
    # )
    # async def gimmick_reveal_command(self, ctx: interactions.SlashContext):
    #     await ctx.send("test")
