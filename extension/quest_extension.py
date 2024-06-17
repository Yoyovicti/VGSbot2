import interactions

from commands.quest_command import QuestCommand
from init_config import GUILD_IDS, quest_manager


class QuestExtension(interactions.Extension):
    ID_OPTION = interactions.SlashCommandOption(
        name="quête",
        description="Le numéro de la quête",
        type=interactions.OptionType.STRING,
        required=True,
        argument_name="quest_id",
        choices=[
            interactions.SlashCommandChoice(name=quest_manager.quests[q_id], value=q_id)
            for q_id in quest_manager.quests
        ]
    )

    def __init__(self, bot: interactions.Client):
        self.add_ext_auto_defer()

    @interactions.slash_command(
        name="quete",
        description="Effectue une action sur les quêtes",
        scopes=GUILD_IDS,
        options=[
            ID_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="ajouter",
        sub_cmd_description="Ajouter une mission aux quêtes en cours"
    )
    async def quest_add_command(self, ctx: interactions.SlashContext, quest_id: str):
        command = QuestCommand(self.bot, ctx, "add", quest_id)
        await command.run()

    @interactions.slash_command(
        name="quete",
        description="Effectue une action sur les quêtes",
        scopes=GUILD_IDS,
        options=[
            ID_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="valider",
        sub_cmd_description="Valider une quête"
    )
    async def quest_complete_command(self, ctx: interactions.SlashContext, quest_id: str):
        command = QuestCommand(self.bot, ctx, "complete", quest_id)
        await command.run()

    @interactions.slash_command(
        name="quete",
        description="Effectue une action sur les quêtes",
        scopes=GUILD_IDS,
        options=[
            ID_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="annuler",
        sub_cmd_description="Annuler une quête en cours ou validée sans sauvegarder."
    )
    async def quest_cancel_command(self, ctx: interactions.SlashContext, quest_id: str):
        command = QuestCommand(self.bot, ctx, "cancel", quest_id)
        await command.run()

    @interactions.slash_command(
        name="quete",
        description="Effectue une action sur les quêtes",
        scopes=GUILD_IDS,
        options=[
            ID_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="sauvegarder",
        sub_cmd_description="Annule une quête en cours et sauvegarde son état."
    )
    async def quest_cancel_command(self, ctx: interactions.SlashContext, quest_id: str):
        command = QuestCommand(self.bot, ctx, "save", quest_id)
        await command.run()

    @interactions.slash_command(
        name="quete",
        description="Effectue une action sur les quêtes",
        scopes=GUILD_IDS,
        options=[
            ID_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="avancer",
        sub_cmd_description="Avancer une quête à l'étape suivante."
    )
    async def quest_forward_command(self, ctx: interactions.SlashContext, quest_id: str):
        command = QuestCommand(self.bot, ctx, "forward", quest_id)
        await command.run()

    @interactions.slash_command(
        name="quete",
        description="Effectue une action sur les quêtes",
        scopes=GUILD_IDS,
        options=[
            ID_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="reculer",
        sub_cmd_description="Faire revenir une quête à l'étape précédente."
    )
    async def quest_backward_command(self, ctx: interactions.SlashContext, quest_id: str):
        command = QuestCommand(self.bot, ctx, "backward", quest_id)
        await command.run()
