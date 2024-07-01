import interactions

from commands.mission_command import MissionCommand
from init_config import GUILD_IDS, mission_manager


class MissionExtension(interactions.Extension):
    ID_OPTION = interactions.SlashCommandOption(
        name="mission",
        description="Le numéro de la mission",
        type=interactions.OptionType.STRING,
        autocomplete=True,
        required=True,
        argument_name="mission_id"
    )

    def __init__(self, bot: interactions.Client):
        self.add_ext_auto_defer()

    @interactions.slash_command(
        name="mission",
        description="Effectue une action sur les missions",
        scopes=GUILD_IDS,
        options=[
            ID_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="ajouter",
        sub_cmd_description="Ajouter une mission aux missions en cours"
    )
    async def mission_add_command(self, ctx: interactions.SlashContext, mission_id: str):
        command = MissionCommand(self.bot, ctx, "add", mission_id)
        await command.run()

    @interactions.slash_command(
        name="mission",
        description="Effectue une action sur les missions",
        scopes=GUILD_IDS,
        options=[
            ID_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="valider",
        sub_cmd_description="Valider une mission"
    )
    async def mission_complete_command(self, ctx: interactions.SlashContext, mission_id: str):
        command = MissionCommand(self.bot, ctx, "complete", mission_id)
        await command.run()

    @interactions.slash_command(
        name="mission",
        description="Effectue une action sur les missions",
        scopes=GUILD_IDS,
        options=[
            ID_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="annuler",
        sub_cmd_description="Annuler une mission en cours ou validée"
    )
    async def mission_cancel_command(self, ctx: interactions.SlashContext, mission_id: str):
        command = MissionCommand(self.bot, ctx, "cancel", mission_id)
        await command.run()

    @interactions.slash_command(
        name="mission",
        description="Effectue une action sur les missions",
        scopes=GUILD_IDS,
        options=[
            interactions.SlashCommandOption(
                name="nombre",
                description="Le nombre de slots pour les missions",
                type=interactions.OptionType.INTEGER,
                required=True,
                min_value=3,
                max_value=4,
                argument_name="qty"
            )
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="slot",
        sub_cmd_description="Modifier le nombre de slots pour les missions"
    )
    async def mission_slot_command(self, ctx: interactions.SlashContext, qty: int):
        command = MissionCommand(self.bot, ctx, "slot", n_slot=qty)
        await command.run()

    @mission_add_command.autocomplete("mission")
    @mission_complete_command.autocomplete("mission")
    @mission_cancel_command.autocomplete("mission")
    async def autocomplete(self, ctx: interactions.AutocompleteContext):
        str_input = ctx.input_text
        choices = [
            interactions.SlashCommandChoice(name=mission_manager.missions[m_id], value=m_id)
            for m_id in mission_manager.missions
            if m_id.startswith(str_input)
        ]
        await ctx.send(choices[:25])