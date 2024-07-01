import interactions

from init_config import GUILD_IDS, DATA_FOLDER
from manager import save_manager


class BackupExtension(interactions.Extension):
    def __init__(self, bot: interactions.Client):
        self.add_ext_auto_defer()

    @interactions.slash_command(
        name="backup",
        description="Crée un fichier .zip contenant les inventaires des équipes",
        scopes=GUILD_IDS,
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def backup_command(self, ctx: interactions.SlashContext):
        await save_manager.backup_data(ctx, DATA_FOLDER)

    @interactions.slash_command(
        name="shutdown",
        description="Arrête le bot et sauvegarde les fichiers",
        scopes=GUILD_IDS,
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def shutdown_command(self, ctx: interactions.SlashContext):
        await save_manager.backup_data(ctx, DATA_FOLDER)
        exit()
