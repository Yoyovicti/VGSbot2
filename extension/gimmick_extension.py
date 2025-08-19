from datetime import datetime, timedelta

import interactions
import pytz
from interactions import DateTrigger

from init_config import GUILD_IDS, team_manager, gimmick_manager, GIMMICK_CHANNEL, VGS_FOLDER
from init_emoji import REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N
from manager.reaction_manager import ReactionManager


# TODO Command to add gimmick
# TODO Refactor with gimmick command

class GimmickExtension(interactions.Extension):
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
            await self.init_gimmicks(ctx)
            return
        if ope == "delete":
            await self.delete_gimmicks(ctx)
            return
        if ope == "clear":
            await self.clear_gimmicks(ctx)
            return

    async def edit_gimmick_message(self, gimmick_list):
        gimmick_channel = await self.bot.fetch_channel(GIMMICK_CHANNEL)
        gimmick_message = await gimmick_channel.fetch_message(gimmick_list.message_id)
        await gimmick_message.edit(content=gimmick_list.format_discord(), file=gimmick_list.get_image_path(VGS_FOLDER))

    async def init_gimmicks(self, ctx: interactions.SlashContext):
        # Load inventory
        inventory = gimmick_manager.gimmick_list_inventory
        if inventory is None:
            await ctx.send("Erreur: Commande non implémentée.")
            return
        if inventory.initialized:
            await ctx.send("Erreur: L'inventaire existe déjà.")
            return

        # Send message in gimmick channel
        gimmick_channel = await self.bot.fetch_channel(GIMMICK_CHANNEL)

        inventory.init()
        for entry in inventory.contents:
            gimmick_list = inventory.contents[entry]
            gimmick_list_message = await gimmick_channel.send(content=gimmick_list.format_discord(), file=gimmick_list.get_image_path(VGS_FOLDER))

            gimmick_list.init(str(gimmick_list_message.id))

        inventory.save(VGS_FOLDER)

        # Confirmation message
        await ctx.send("Listes de gimmicks initialisées !")

    async def delete_gimmicks(self, ctx: interactions.SlashContext):
        # Load inventory
        inventory = gimmick_manager.gimmick_list_inventory
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

        # Delete message in gimmick channel
        gimmick_channel = await self.bot.fetch_channel(GIMMICK_CHANNEL)

        for entry in inventory.contents:
            gimmick_list = inventory.contents[entry]
            gimmick_list_message = await gimmick_channel.fetch_message(gimmick_list.message_id)
            await gimmick_channel.delete_message(gimmick_list_message)

        inventory.delete(VGS_FOLDER)

        # Confirmation message
        await ctx.send("Listes de gimmicks supprimées !")

    async def clear_gimmicks(self, ctx: interactions.SlashContext):
        # Load inventory
        inventory = gimmick_manager.gimmick_list_inventory
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
        inventory.save(VGS_FOLDER)

        # Edit message in item channel
        gimmick_channel = await self.bot.fetch_channel(GIMMICK_CHANNEL)
        for entry in inventory.contents:
            gimmick_list = inventory.contents[entry]
            gimmick_message = await gimmick_channel.fetch_message(gimmick_list.message_id)
            await gimmick_message.edit(content=gimmick_list.format_discord(), file=gimmick_list.get_image_path(VGS_FOLDER))

        # Confirmation message
        await ctx.send("Listes de gimmicks vidées !")

    LIST_OPTION = interactions.SlashCommandOption(
        name="liste",
        description="La liste de gimmicks",
        type=interactions.OptionType.STRING,
        required=True,
        argument_name="list_name",
        choices=[
            interactions.SlashCommandChoice(name=list_name, value=list_name)
            for list_name in gimmick_manager.gimmicks
        ]
    )

    STEP_OPTION = interactions.SlashCommandOption(
        name="étape",
        description="L'étape de la liste de gimmicks",
        type=interactions.OptionType.INTEGER,
        required=True,
        argument_name="step",
        min_value=1,
        max_value=6
    )

    DAY_OPTION = interactions.SlashCommandOption(
        name="jour",
        description="Le jour de la validation",
        type=interactions.OptionType.INTEGER,
        required=False,
        argument_name="day",
        min_value=1,
        max_value=31
    )

    MONTH_OPTION = interactions.SlashCommandOption(
        name="mois",
        description="Le mois de la validation",
        type=interactions.OptionType.INTEGER,
        required=False,
        argument_name="month",
        min_value=6,
        max_value=8
    )

    INSTANT_OPTION = interactions.SlashCommandOption(
        name="instant",
        description="Si oui, révèle le gimmick immédiatement. Si non, attend minuit.",
        type=interactions.OptionType.STRING,
        required=False,
        choices=[
            interactions.SlashCommandChoice(name="oui", value="oui"),
            interactions.SlashCommandChoice(name="non", value="non")
        ]
    )


    def __init__(self, bot: interactions.Client):
        self.add_ext_auto_defer()

        self.team = None
        self.gimmick_list = None

    def init_team_info(self):
        self.team = None

    async def load_team_info(self, ctx: interactions.SlashContext) -> bool:
        self.init_team_info()

        self.team = team_manager.get_team(str(ctx.channel_id))
        if self.team is None:
            await ctx.send("Erreur: Équipe non trouvée. Assurez-vous d'utiliser la commande dans le bon channel.")
            return False

        return True

    @interactions.slash_command(
        name="gimmick",
        description="Effectue une action sur les gimmicks",
        scopes=GUILD_IDS,
        options=[
            LIST_OPTION,
            STEP_OPTION,
            DAY_OPTION,
            MONTH_OPTION,
            INSTANT_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="valider",
        sub_cmd_description="Valider la trouvaille d'un gimmick de liste."
    )
    async def gimmick_found_command(self, ctx: interactions.SlashContext, list_name: str, step: int, day: int = -1,
                                    month: int = -1, instant: str = "non"):
        # Load inventory
        inventory = gimmick_manager.gimmick_list_inventory
        if inventory is None:
            await ctx.send("Erreur: Commande non implémentée.")
            return
        if not inventory.initialized:
            await ctx.send("Erreur: L'inventaire n'est pas initialisé.")
            return

        success = await self.load_team_info(ctx)
        if not success:
            return

        if inventory.get_found(list_name, step):
            await ctx.send("Erreur: le gimmick a déjà été validé.")
            return

        curr_step = inventory.get_current_step(list_name)
        if step != curr_step:
            if not(step == curr_step + 1 and inventory.get_unlock(self.team.name, list_name)):
                await ctx.send(f"Erreur: le gimmick de l'étape {step} n'est pas encore disponible.")
                return

        else:
            inventory.next_step(list_name)

        inventory.clear_seen(list_name)
        inventory.clear_unlocked(list_name)

        inventory.set_found(list_name, self.team.name, step)
        inventory.save(VGS_FOLDER)

        # TODO Edit message, update png
        gimmick_list = inventory.contents[list_name]

        if instant == "oui":
            await self.edit_gimmick_message(gimmick_list)
            # Confirmation message
            await ctx.send("Gimmick validé !")
        else:
            paris_tz = pytz.timezone("Europe/Paris")
            now_paris = datetime.now(paris_tz)

            if month > 0: now_paris = now_paris.replace(month=month)
            if day > 0: now_paris = now_paris.replace(day=day)
            if now_paris < datetime.now(paris_tz):
                await self.edit_gimmick_message(gimmick_list)
                await ctx.send("Gimmick validé !")
                return

            # schedule = now_paris + timedelta(seconds=10)
            schedule = (now_paris + timedelta(days=1)).replace(hour=0, minute=0, second=0)
            local_dt = schedule.astimezone()
            naive_local_dt = local_dt.replace(tzinfo=None)

            task = interactions.Task(self.edit_gimmick_message, DateTrigger(naive_local_dt))
            task.start(gimmick_list)
            await ctx.send("Le prochain gimmick sera révélé à minuit !")

    @interactions.slash_command(
        name="gimmick",
        description="Effectue une action sur les gimmicks",
        scopes=GUILD_IDS,
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="rafraîchir",
        sub_cmd_description="Un peu d'air frais, ça fait du bien :)"
    )
    async def gimmick_refresh_command(self, ctx: interactions.SlashContext):
        # Load inventory
        inventory = gimmick_manager.gimmick_list_inventory
        if inventory is None:
            await ctx.send("Erreur: Commande non implémentée.")
            return
        if not inventory.initialized:
            await ctx.send("Erreur: L'inventaire n'est pas initialisé.")
            return

        gimmick_channel = await self.bot.fetch_channel(GIMMICK_CHANNEL)
        for entry in inventory.contents:
            gimmick_list = inventory.contents[entry]
            gimmick_message = await gimmick_channel.fetch_message(gimmick_list.message_id)
            await gimmick_message.edit(content=gimmick_list.format_discord(),
                                       file=gimmick_list.get_image_path(VGS_FOLDER))

        # Confirmation message
        await ctx.send("J'ai un gros glaçon sur ma tête !")

    @interactions.slash_command(
        name="gimmick",
        description="Effectue une action sur les gimmicks",
        scopes=GUILD_IDS,
        options=[
            # REGION_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="révéler",
        sub_cmd_description="Révéler le Pokémon gimmick de liste"
    )
    async def gimmick_reveal_command(self, ctx: interactions.SlashContext, cat: str):
        # TODO
        raise NotImplementedError
        # success = await self.load_team_info(ctx)
        # if not success:
        #     return
        #
        # if self.gimmick_inventory.is_unlock(cat):
        #     await ctx.send("Erreur. Ce gimmick a déjà été révélé.")
        #     return
        #
        # warning_msg = await ctx.send("Attention ! Le Pokémon gimmick sera révélé aux participants. Souhaitez-vous "
        #                              "confirmer l'opération ?")
        # reaction_manager = ReactionManager(warning_msg, [REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N])
        # reaction = await reaction_manager.run()
        # if reaction != REGIONAL_INDICATOR_O:
        #     await ctx.send("Opération annulée.")
        #     return
        #
        # # Unlock Pokémon in inventory and save
        # self.gimmick_inventory.set_unlock(cat)
        # self.gimmick_inventory.save(TEAM_FOLDER, self.team.id)
        #
        # # Edit inventory message and send to item channel
        # inv_msg = await self.item_channel.fetch_message(self.gimmick_inventory.message_id)
        # await inv_msg.edit(content=self.gimmick_inventory.format_discord(self.team.name))
        # message = (f"*Le Pokémon gimmick de la zone **{self.gimmick_inventory.get_zone(cat)} ({cat})** a été révélé. "
        #            f"Il s'agit de* **{self.gimmick_inventory.get_pokemon(cat)}**.")
        # await self.item_channel.send(message)
        #
        # # Confirmation message
        # await ctx.send("Gimmick révélé !")

    # @interactions.slash_command(
    #     name="gimmick",
    #     description="Effectue une action sur les gimmicks",
    #     scopes=GUILD_IDS,
    #     options=[
    #         # REGION_OPTION
    #     ],
    #     default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    #     dm_permission=False,
    #     sub_cmd_name="cacher",
    #     sub_cmd_description="Cache un gimmick de liste révélé. Ne devrait pas être utilisé en conditions réelles."
    # )
    # async def gimmick_hide_command(self, ctx: interactions.SlashContext, cat: str):
    #     # TODO
    #     raise NotImplementedError
        # success = await self.load_team_info(ctx)
        # if not success:
        #     return
        #
        # if not self.gimmick_inventory.is_unlock(cat):
        #     await ctx.send("Erreur. Ce gimmick est déjà caché.")
        #     return
        #
        # # Hide Pokémon in inventory and save
        # self.gimmick_inventory.set_unlock(cat, state=False)
        # self.gimmick_inventory.save(TEAM_FOLDER, self.team.id)
        #
        # # Edit inventory message
        # inv_msg = await self.item_channel.fetch_message(self.gimmick_inventory.message_id)
        # await inv_msg.edit(content=self.gimmick_inventory.format_discord(self.team.name))
        #
        # # Confirmation message
        # await ctx.send("Gimmick caché !")

    # @interactions.slash_command(
    #     name="gimmick",
    #     description="Effectue une action sur les gimmicks",
    #     scopes=GUILD_IDS,
    #     options=[
    #         LIST_OPTION
    #     ],
    #     default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    #     dm_permission=False,
    #     sub_cmd_name="observer",
    #     sub_cmd_description="Observer la zone d'un gimmick adverse. Ne devrait pas être utilisé en conditions réelles."
    # )
    # async def gimmick_see_command(self, ctx: interactions.SlashContext, list_name: str):
    #     success = await self.load_team_info(ctx)
    #     if not success:
    #         return
    #
    #     if gimmick_manager.gimmick_list_inventory.get_found(list_name, step):
    #         await ctx.send("Erreur: le gimmick a déjà été validé.")
    #         return
    #
    #     if not gimmick_manager.gimmick_list_inventory.get_unlock(list_name, step):
    #         warning_msg = await ctx.send("Attention ! Le Pokémon gimmick n'a jamais été révélé aux participants. "
    #                                      "Cette opération va valider le gimmick et révéler le Pokémon.\n"
    #                                      "Souhaitez-vous continuer ?")
    #
    #         reaction_manager = ReactionManager(warning_msg, [REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N])
    #         reaction = await reaction_manager.run()
    #         if reaction != REGIONAL_INDICATOR_O:
    #             await ctx.send("Opération annulée.")
    #             return
    #
    #     gimmick_manager.gimmick_list_inventory.set_found(list_name, step)
    #     gimmick_manager.gimmick_list_inventory.set_unlock(list_name, step)  # ?
    #     gimmick_manager.gimmick_list_inventory.save()
    #
    #     # TODO Edit message, update png
    #
    #     # TODO
    #     raise NotImplementedError
        # success = await self.load_team_info(ctx)
        # if not success:
        #     return
        #
        # # Fetch target team channel
        # team_inst = team_manager.teams[team]
        # target_item_channel = await self.bot.fetch_channel(team_inst.item_channel_id)
        # if target_item_channel is None:
        #     await ctx.send("Erreur: Salon objets non trouvé pour l'équipe visée.")
        #     return False
        #
        # # Check that gimmick is not seen already
        # should_cancel = cancel == "oui"
        # if should_cancel and not self.gimmick_inventory.is_seen(team_inst.name, cat):
        #     await ctx.send("Erreur : Cette zone n'a pas été observée.")
        #
        # if not should_cancel and self.gimmick_inventory.is_seen(team_inst.name, cat):
        #     await ctx.send("Erreur : Cette zone a déjà été observée.")
        #     return
        #
        # # Add gimmick to seen gimmicks, update counter on target team
        # target_inv = team_inst.inventory_manager.gimmick_inventory
        # self.gimmick_inventory.see(team_inst.name, target_inv.gimmicks[cat], state=(not should_cancel))
        #
        # if should_cancel:
        #     target_inv.remove_see_count(cat)
        # else:
        #     target_inv.add_see_count(cat)
        #
        # # Edit messages
        # origin_inv_msg = await self.item_channel.fetch_message(self.gimmick_inventory.message_id)
        # await origin_inv_msg.edit(content=self.gimmick_inventory.format_discord(self.team.name))
        # target_inv_msg = await target_item_channel.fetch_message(target_inv.message_id)
        # await target_inv_msg.edit(content=target_inv.format_discord(team_inst.name))
        #
        # # Save inventories
        # self.gimmick_inventory.save(TEAM_FOLDER, self.team.id)
        # target_inv.save(TEAM_FOLDER, team)
        #
        # # Confirmation message
        # await ctx.send("Opération effectuée !")
