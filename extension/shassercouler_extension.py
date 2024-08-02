import interactions

from init_config import GUILD_IDS, team_manager, TEAM_FOLDER


class ShasserCoulerExtension(interactions.Extension):
    CELL_OPTION = interactions.SlashCommandOption(
        name="case",
        description="La case à valider",
        type=interactions.OptionType.STRING,
        required=True,
        argument_name="cell"
    )

    def __init__(self, bot: interactions.Client):
        self.add_ext_auto_defer()

        self.team = None
        self.shassercouler_grid = None
        self.shassercouler_channel = None

    @interactions.slash_command(
        name="shassercouler",
        description="Effectue une action pour le shasser-couler",
        scopes=GUILD_IDS,
        options=[
            CELL_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="valider",
        sub_cmd_description="Valider une case du shasser-couler"
    )
    async def shassercouler_valider_command(self, ctx: interactions.SlashContext, cell: str = ""):
        success = await self.load_team_info(ctx)
        if not success:
            return

        # Reveal cell and save
        success = self.shassercouler_grid.reveal_from_string(cell)
        if not success:
            await ctx.send("Erreur: Format de case invalide.")
            return

        self.shassercouler_grid.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message and send to item channel
        await self.shassercouler_channel.send(f"Case {cell.upper()} validée !")

        # Confirmation message
        await ctx.send("Inventaire mis à jour !")

    @interactions.slash_command(
        name="shassercouler",
        description="Effectue une action pour le shasser-couler",
        scopes=GUILD_IDS,
        options=[
            CELL_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="invalider",
        sub_cmd_description="Invalider une case du shasser-couler"
    )
    async def shassercouler_invalider_command(self, ctx: interactions.SlashContext, cell: str = ""):
        success = await self.load_team_info(ctx)
        if not success:
            return

        # Hide cell and save
        success = self.shassercouler_grid.reveal_from_string(cell, invert=True)
        if not success:
            await ctx.send("Erreur: Format de case invalide.")
        self.shassercouler_grid.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message and send to item channel
        await self.shassercouler_channel.send(f"Case {cell.upper()} invalidée !")

        # Confirmation message
        await ctx.send("Inventaire mis à jour !")

    @interactions.slash_command(
        name="shassercouler",
        description="Effectue une action pour le shasser-couler",
        scopes=GUILD_IDS,
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="afficher",
        sub_cmd_description="Afficher la grille du shasser-couler"
    )
    async def shassercouler_afficher_command(self, ctx: interactions.SlashContext):
        success = await self.load_team_info(ctx)
        if not success:
            return

        await ctx.send(self.shassercouler_grid.format_discord())

    @interactions.slash_command(
        name="shassercouler",
        description="Effectue une action pour le shasser-couler",
        scopes=GUILD_IDS,
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="dracofleche",
        sub_cmd_description="Valide 4 cases aléatoirement parmi les cases disponibles de la grille"
    )
    async def shassercouler_dracofleche_command(self, ctx: interactions.SlashContext):
        success = await self.load_team_info(ctx)
        if not success:
            return

        # Get selected cells and validate
        selected_cells = self.shassercouler_grid.random_reveal(4)
        self.shassercouler_grid.save(TEAM_FOLDER, self.team.id)

        # Print
        string = "Cases tirées par la draco-flèche : "
        for i in range(len(selected_cells)):
            if i > 0:
                string += ", "
            row, col = selected_cells[i]
            string += self.shassercouler_grid.get_cell(row, col)
        await self.shassercouler_channel.send(string)

        # Confirmation message
        await ctx.send("Inventaire mis à jour !")

    async def load_team_info(self, ctx: interactions.SlashContext) -> bool:
        self.team = team_manager.get_team(str(ctx.channel_id))
        if self.team is None:
            await ctx.send("Erreur: Équipe non trouvée. Assurez-vous d'utiliser la commande dans le bon channel.")
            return False

        self.shassercouler_grid = self.team.inventory_manager.shassercouler_grid
        if not self.shassercouler_grid.initialized:
            await ctx.send("Erreur: L'inventaire n'est pas initialisé.")
            return False

        self.shassercouler_channel = await self.bot.fetch_channel(self.team.shassercouler_id)
        if self.shassercouler_channel is None:
            await ctx.send("Erreur: Salon shasser-couler non trouvé pour l'équipe sélectionnée.")
            return False

        return True
