import interactions

from commands.gimmick_item_command import GimmickItemCommand
from gimmick import Gimmick
from init_config import GUILD_IDS, team_manager, gimmick_manager, TEAM_FOLDER
from init_emoji import REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N, KEYCAP_NUMBERS, CROSS_MARK
from reaction_manager import ReactionManager


# TODO Command to add gimmick
# TODO Refactor with gimmick command

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

    ZONE_OPTION = interactions.SlashCommandOption(
        name="zone",
        description="La zone du gimmick",
        type=interactions.OptionType.STRING,
        required=True,
        argument_name="zone"
    )

    POKEMON_OPTION = interactions.SlashCommandOption(
        name="pokémon",
        description="Le Pokémon gimmick de liste",
        type=interactions.OptionType.STRING,
        required=True,
        argument_name="pokemon"
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
        name="d6",
        description="Utilise un D6",
        scopes=GUILD_IDS,
        options=[
            REGION_OPTION,
            ZONE_OPTION,
            POKEMON_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def d6_command(self, ctx: interactions.SlashContext, cat, zone, pokemon):
        command = GimmickItemCommand(self.bot, ctx, "d6", region=cat, zone=zone, pokemon=pokemon)
        await command.run()

    @interactions.slash_command(
        name="gimmick",
        description="Effectue une action sur les gimmicks",
        scopes=GUILD_IDS,
        options=[
            REGION_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="valider",
        sub_cmd_description="Valider la trouvaille d'un gimmick de liste."
    )
    async def gimmick_found_command(self, ctx: interactions.SlashContext, cat: str):
        success = await self.load_team_info(ctx)
        if not success:
            return

        if self.gimmick_inventory.is_found(cat):
            await ctx.send("Erreur: le gimmick a déjà été validé.")
            return

        if not self.gimmick_inventory.is_unlock(cat):
            warning_msg = await ctx.send("Attention ! Le Pokémon gimmick n'a jamais été révélé aux participants. Cette "
                                         "opération va valider le gimmick et révéler le Pokémon.\n"
                                         "Souhaitez-vous continuer ?")
            reaction_manager = ReactionManager(warning_msg, [REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N])
            reaction = await reaction_manager.run()
            if reaction != REGIONAL_INDICATOR_O:
                await ctx.send("Opération annulée.")
                return

        # Select team that found the gimmick
        valid_teams = list(team_manager.teams)
        team_select_string = "Veuillez sélectionner l'équipe qui a validé le gimmick :\n\n"
        for i in range(len(team_manager.teams)):
            team_select_string += f"{KEYCAP_NUMBERS[i]} {team_manager.teams[valid_teams[i]].name}\n"
        team_select_message = await ctx.send(team_select_string)
        team_reaction_manager = ReactionManager(team_select_message,
                                                [CROSS_MARK] + KEYCAP_NUMBERS[:len(valid_teams)])
        selected_reaction = await team_reaction_manager.run()

        # Cancel
        if selected_reaction == CROSS_MARK:
            await ctx.send("Opération annulée.")
            return

        # Get name of team that found the gimmick
        target_team_id = valid_teams[KEYCAP_NUMBERS.index(selected_reaction)]
        target_team_name = team_manager.teams[target_team_id].name

        if self.gimmick_inventory.get_see_count(cat) > 0:
            # Delete from opponents seen list
            for team in team_manager.teams:
                if self.team.id == team:
                    continue
                gimmick_inv = team_manager.teams[team].inventory_manager.gimmick_inventory
                if gimmick_inv.is_seen(self.team.name, cat):
                    # Update and save
                    gimmick_inv.see(self.team.name, gimmick_inv.get_seen(self.team.name, cat), state=False)
                    gimmick_inv.save(TEAM_FOLDER, team)

                    # Send message
                    item_channel = await self.bot.fetch_channel(team_manager.teams[team].item_channel_id)
                    if item_channel is None:
                        await ctx.send(f"Erreur: Salon objets non trouvé pour l'équipe {team}")
                        continue

                    inv_msg = await item_channel.fetch_message(gimmick_inv.message_id)
                    await inv_msg.edit(content=gimmick_inv.format_discord(team_manager.teams[team].name))
                    message = (f"*Le gimmick de la région* **{cat}** *observé chez l'équipe {self.team.name} a été "
                               f"validé et a donc été supprimé des gimmicks observés.*\n")
                    await item_channel.send(message)

        # Mark gimmick as found, unlock and save
        self.gimmick_inventory.set_found(cat, target_team_name)
        self.gimmick_inventory.set_unlock(cat)
        self.gimmick_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message and send to item channel for current team
        inv_msg = await self.item_channel.fetch_message(self.gimmick_inventory.message_id)
        await inv_msg.edit(content=self.gimmick_inventory.format_discord(self.team.name))
        message = f"*Le gimmick de la région **{cat}** a été validé par l'équipe {target_team_name}.*"
        await self.item_channel.send(message)

        # Confirmation message
        await ctx.send("Gimmick validé !")

    @interactions.slash_command(
        name="gimmick",
        description="Effectue une action sur les gimmicks",
        scopes=GUILD_IDS,
        options=[
            REGION_OPTION,
            ZONE_OPTION,
            POKEMON_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="éditer",
        sub_cmd_description="Modifier un gimmick de liste"
    )
    async def gimmick_edit_command(self, ctx: interactions.SlashContext, cat: str, zone: str, pokemon: str):
        success = await self.load_team_info(ctx)
        if not success:
            return

        if self.gimmick_inventory.is_found(cat):
            await ctx.send("Erreur. Impossible de modifier un gimmick déjà validé.")
            return

        if self.gimmick_inventory.is_unlock(cat):
            warning_msg = await ctx.send("Attention ! Le Pokémon gimmick a déjà été révélé aux participants. Cette "
                                         "opération va conserver le statut et indiquer le nouveau Pokémon.\n"
                                         "Souhaitez-vous continuer ?")
            reaction_manager = ReactionManager(warning_msg, [REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N])
            reaction = await reaction_manager.run()
            if reaction != REGIONAL_INDICATOR_O:
                await ctx.send("Opération annulée.")
                return

        if self.gimmick_inventory.get_see_count(cat) > 0:
            warning_msg = await ctx.send("Attention ! La zone gimmick a déjà été observée par d'autres équipes. Cette "
                                         "opération va indiquer le changement aux équipes concernées.\n"
                                         "Souhaitez-vous continuer ?")
            reaction_manager = ReactionManager(warning_msg, [REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N])
            reaction = await reaction_manager.run()
            if reaction != REGIONAL_INDICATOR_O:
                await ctx.send("Opération annulée.")
                return

            gimmick = Gimmick(cat, zone, pokemon)
            # Edit other teams
            for team in team_manager.teams:
                if self.team.id == team:
                    continue
                gimmick_inv = team_manager.teams[team].inventory_manager.gimmick_inventory
                if gimmick_inv.is_seen(self.team.name, cat):
                    # Update and save
                    gimmick_inv.see(self.team.name, gimmick_inv.get_seen(self.team.name, cat), state=False)
                    gimmick_inv.see(self.team.name, gimmick)
                    gimmick_inv.save(TEAM_FOLDER, team)

                    # Send message
                    item_channel = await self.bot.fetch_channel(team_manager.teams[team].item_channel_id)
                    if item_channel is None:
                        await ctx.send(f"Erreur: Salon objets non trouvé pour l'équipe {team}")
                        return False
                    inv_msg = await item_channel.fetch_message(gimmick_inv.message_id)
                    await inv_msg.edit(content=gimmick_inv.format_discord(team_manager.teams[team].name))
                    message = (f"*Le gimmick de la région* **{cat}** *observé chez l'équipe {self.team.name} a été "
                               f"modifié.\nLa zone est désormais* **{zone}**.")
                    await item_channel.send(message)

        # Edit gimmick for current team
        self.edit_gimmick(cat, zone, pokemon)

        # Edit inventory message and send to item channel for current team
        inv_msg = await self.item_channel.fetch_message(self.gimmick_inventory.message_id)
        await inv_msg.edit(content=self.gimmick_inventory.format_discord(self.team.name))
        message = (f"*Le gimmick de la région **{cat}** a été modifié.\n"
                   f"La zone est désormais* **{zone}**.")
        await self.item_channel.send(message)

        # Confirmation message
        await ctx.send("Gimmick modifié !")

    def edit_gimmick(self, region: str, zone: str, pokemon: str, lock: bool = False):
        # Update gimmick in list
        gimmick_manager.edit_gimmick(self.team.id, region, zone, pokemon)
        self.gimmick_inventory.update_gimmicks(gimmick_manager.gimmicks[self.team.id])
        if lock:
            self.gimmick_inventory.set_unlock(region, state=False)

        # Save gimmick inventory
        self.gimmick_inventory.save(TEAM_FOLDER, self.team.id)

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

        if self.gimmick_inventory.is_unlock(cat):
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
        self.gimmick_inventory.set_unlock(cat)
        self.gimmick_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message and send to item channel
        inv_msg = await self.item_channel.fetch_message(self.gimmick_inventory.message_id)
        await inv_msg.edit(content=self.gimmick_inventory.format_discord(self.team.name))
        message = (f"*Le Pokémon gimmick de la zone **{self.gimmick_inventory.get_zone(cat)} ({cat})** a été révélé. "
                   f"Il s'agit de* **{self.gimmick_inventory.get_pokemon(cat)}**.")
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

        if not self.gimmick_inventory.is_unlock(cat):
            await ctx.send("Erreur. Ce gimmick est déjà caché.")
            return

        # Hide Pokémon in inventory and save
        self.gimmick_inventory.set_unlock(cat, state=False)
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
        if should_cancel and not self.gimmick_inventory.is_seen(team_inst.name, cat):
            await ctx.send("Erreur : Cette zone n'a pas été observée.")

        if not should_cancel and self.gimmick_inventory.is_seen(team_inst.name, cat):
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
