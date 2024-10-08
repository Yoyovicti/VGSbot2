import interactions

from commands.classic_item_command import ClassicItemCommand
from commands.roll_item_command import RollItemCommand
from commands.usable_item_command import UsableItemCommand
from init_config import GUILD_IDS, item_manager, team_manager, roll_manager


class ItemExtension(interactions.Extension):
    ITEM_OPTION = interactions.SlashCommandOption(
        name="objet",
        description="L'objet à ajouter ou retirer",
        type=interactions.OptionType.STRING,
        required=True,
        argument_name="item",
        choices=[
            interactions.SlashCommandChoice(name=item_manager.items[item].name, value=item)
            for item in item_manager.items
        ]
    )
    ITEM_STEALABLE_OPTION = interactions.SlashCommandOption(
        name="objet",
        description="L'objet à voler",
        type=interactions.OptionType.STRING,
        required=True,
        argument_name="item",
        choices=[
            interactions.SlashCommandChoice(name=item_manager.items[item].name, value=item)
            for item in item_manager.items
            if item_manager.items[item].stealable
        ]
    )
    QTY_OPTION = interactions.SlashCommandOption(
        name="quantité",
        description="La quantité de l'objet concerné",
        type=interactions.OptionType.INTEGER,
        required=False,
        argument_name="qty",
        min_value=1
    )
    GOLD_OPTION = interactions.SlashCommandOption(
        name="doré",
        description="Si l'objet est doré",
        type=interactions.OptionType.STRING,
        required=False,
        argument_name="gold",
        choices=[
            interactions.SlashCommandChoice(name="oui", value="oui"),
            interactions.SlashCommandChoice(name="non", value="non")
        ]
    )
    SAFE_OPTION = interactions.SlashCommandOption(
        name="volable",
        description="Si l'objet est volable",
        type=interactions.OptionType.STRING,
        required=False,
        argument_name="stealable",
        choices=[
            interactions.SlashCommandChoice(name="oui", value="oui"),
            interactions.SlashCommandChoice(name="non", value="non")
        ]
    )

    METHODE_OPTION = interactions.SlashCommandOption(
        name="méthode",
        description="La méthode utilisée pour trouver le shiny",
        type=interactions.OptionType.STRING,
        required=True,
        argument_name="method",
        choices=[
            interactions.SlashCommandChoice(name=roll_manager.method_drops[method].name, value=method)
            for method in roll_manager.method_drops
        ]
    )

    POSITION_OPTION = interactions.SlashCommandOption(
        name="position",
        description="La position de l'équipe au classement",
        type=interactions.OptionType.INTEGER,
        required=True,
        argument_name="pos",
        min_value=1
    )

    CHARM_OPTION = interactions.SlashCommandOption(
        name="charme",
        description="Si le charme est équipé",
        type=interactions.OptionType.STRING,
        required=False,
        argument_name="charm",
        choices=[
            interactions.SlashCommandChoice(name="oui", value="oui"),
            interactions.SlashCommandChoice(name="non", value="non")
        ]
    )

    def __init__(self, bot: interactions.Client):
        self.add_ext_auto_defer()

        self.team = None
        self.item_inventory = None
        self.item_channel = None

    def init_team_info(self):
        self.team = None
        self.item_inventory = None
        self.item_channel = None

    async def load_team_info(self, ctx: interactions.SlashContext) -> bool:
        self.init_team_info()

        self.team = team_manager.get_team(str(ctx.channel_id))
        if self.team is None:
            await ctx.send("Erreur: Équipe non trouvée. Assurez-vous d'utiliser la commande dans le bon channel.")
            return False

        self.item_inventory = self.team.inventory_manager.item_inventory
        if not self.item_inventory.initialized:
            await ctx.send("Erreur: L'inventaire n'est pas initialisé.")
            return False

        self.item_channel = await self.bot.fetch_channel(self.team.item_channel_id)
        if self.item_channel is None:
            await ctx.send("Erreur: Salon objets non trouvé pour l'équipe sélectionnée.")
            return False

        return True

    @interactions.slash_command(
        name="objet",
        description="Effectue une action sur les inventaires",
        scopes=GUILD_IDS,
        options=[
            ITEM_OPTION,
            QTY_OPTION,
            GOLD_OPTION,
            SAFE_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="ajouter",
        sub_cmd_description="Ajouter un objet à l'inventaire"
    )
    async def add_item_command(self, ctx: interactions.SlashContext, item: str, qty: int = 1, gold: str = "non",
                               stealable: str = "oui"):
        command = ClassicItemCommand(self.bot, ctx, item, param="add", qty=qty, gold=(gold == "oui"),
                                     safe=(stealable == "non"))
        await command.run()

    @interactions.slash_command(
        name="objet",
        description="Effectue une action sur les inventaires",
        scopes=GUILD_IDS,
        options=[
            ITEM_OPTION,
            QTY_OPTION,
            GOLD_OPTION,
            SAFE_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False,
        sub_cmd_name="retirer",
        sub_cmd_description="Retirer un objet de l'inventaire"
    )
    async def remove_item_command(self, ctx: interactions.SlashContext, item: str, qty: int = 1, gold: str = "non",
                                  stealable: str = "oui"):
        command = ClassicItemCommand(self.bot, ctx, item, param="remove", qty=qty, gold=(gold == "oui"),
                                     safe=(stealable == "non"))
        await command.run()

    @interactions.slash_command(
        name="tirage",
        description="Effectue un ou plusieurs tirages",
        scopes=GUILD_IDS,
        options=[
            METHODE_OPTION,
            POSITION_OPTION,
            QTY_OPTION,
            CHARM_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def tirage_command(self, ctx: interactions.SlashContext, method: str, pos: int, qty: int = 1,
                             charm: str = "non"):
        command = RollItemCommand(self.bot, ctx, method, pos, qty=qty, charm=(charm == "oui"))
        await command.run()

    @interactions.slash_command(
        name="maxitomate",
        description="Utilise une Maxitomate",
        scopes=GUILD_IDS,
        options=[
            QTY_OPTION,
            GOLD_OPTION,
            SAFE_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def maxitomate_command(self, ctx: interactions.SlashContext, qty: int = 1, gold: str = "non",
                                 stealable: str = "oui"):
        command = ClassicItemCommand(self.bot, ctx, "maxitomate", param="remove", qty=qty, gold=(gold == "oui"),
                                     safe=(stealable == "non"))
        await command.run()

    @interactions.slash_command(
        name="ruche",
        description="Utilise une Ruche",
        scopes=GUILD_IDS,
        options=[
            QTY_OPTION,
            GOLD_OPTION,
            SAFE_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def ruche_command(self, ctx: interactions.SlashContext, qty: int = 1, gold: str = "non",
                            stealable: str = "oui"):
        command = ClassicItemCommand(self.bot, ctx, "ruche", param="remove", qty=qty, gold=(gold == "oui"),
                                     safe=(stealable == "non"))
        await command.run()

    @interactions.slash_command(
        name="grappin",
        description="Utilise un Grappin",
        scopes=GUILD_IDS,
        options=[
            QTY_OPTION,
            GOLD_OPTION,
            SAFE_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def grappin_command(self, ctx: interactions.SlashContext, qty: int = 1, gold: str = "non",
                              stealable: str = "oui"):
        command = ClassicItemCommand(self.bot, ctx, "grappin", param="remove", qty=qty, gold=(gold == "oui"),
                                     safe=(stealable == "non"))
        await command.run()

    @interactions.slash_command(
        name="fulgurorbe",
        description="Utilise une Fulgurorbe",
        scopes=GUILD_IDS,
        options=[
            QTY_OPTION,
            GOLD_OPTION,
            SAFE_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def orbe_command(self, ctx: interactions.SlashContext, qty: int = 1, gold: str = "non",
                           stealable: str = "oui"):
        command = UsableItemCommand(self.bot, ctx, param="fulgurorbe", qty=qty, gold=(gold == "oui"),
                                    safe=(stealable == "non"))
        await command.run()

    @interactions.slash_command(
        name="etoile",
        description="Utilise une Étoile",
        scopes=GUILD_IDS,
        options=[
            QTY_OPTION,
            GOLD_OPTION,
            SAFE_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def etoile_command(self, ctx: interactions.SlashContext, qty: int = 1, gold: str = "non",
                             stealable: str = "oui"):
        command = ClassicItemCommand(self.bot, ctx, "etoile", param="remove", qty=qty, gold=(gold == "oui"),
                                     safe=(stealable == "non"))
        await command.run()

    @interactions.slash_command(
        name="boo",
        description="Utilise un Boo",
        scopes=GUILD_IDS,
        options=[
            QTY_OPTION,
            GOLD_OPTION,
            SAFE_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def boo_command(self, ctx: interactions.SlashContext, qty: int = 1, gold: str = "non",
                          stealable: str = "oui"):
        command = UsableItemCommand(self.bot, ctx, param="boo", qty=qty, gold=(gold == "oui"),
                                    safe=(stealable == "non"))
        await command.run()

    @interactions.slash_command(
        name="picvenin",
        description="Utilise un Pic venin",
        scopes=GUILD_IDS,
        options=[
            QTY_OPTION,
            GOLD_OPTION,
            SAFE_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def picvenin_command(self, ctx: interactions.SlashContext, qty: int = 1, gold: str = "non",
                               stealable: str = "oui"):
        command = ClassicItemCommand(self.bot, ctx, "picvenin", param="remove", qty=qty, gold=(gold == "oui"),
                                     safe=(stealable == "non"))
        await command.run()

    @interactions.slash_command(
        name="clairvoyance",
        description="Utilise une Clairvoyance",
        scopes=GUILD_IDS,
        options=[
            QTY_OPTION,
            GOLD_OPTION,
            SAFE_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def clairvoyance_command(self, ctx: interactions.SlashContext, qty: int = 1, gold: str = "non",
                                   stealable: str = "oui"):
        command = UsableItemCommand(self.bot, ctx, param="clairvoyance", qty=qty, gold=(gold == "oui"),
                                    safe=(stealable == "non"))
        await command.run()

    @interactions.slash_command(
        name="klaxon",
        description="Utilise un Klaxon",
        scopes=GUILD_IDS,
        options=[
            QTY_OPTION,
            GOLD_OPTION,
            SAFE_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def klaxon_command(self, ctx: interactions.SlashContext, qty: int = 1, gold: str = "non",
                             stealable: str = "oui"):
        command = ClassicItemCommand(self.bot, ctx, "klaxon", param="remove", qty=qty, gold=(gold == "oui"),
                                     safe=(stealable == "non"))
        await command.run()

    @interactions.slash_command(
        name="ar",
        description="Utilise une Action Replay",
        scopes=GUILD_IDS,
        options=[
            QTY_OPTION,
            GOLD_OPTION,
            SAFE_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def ar_command(self, ctx: interactions.SlashContext, qty: int = 1, gold: str = "non",
                         stealable: str = "oui"):
        command = UsableItemCommand(self.bot, ctx, param="ar", qty=qty, gold=(gold == "oui"), safe=(stealable == "non"))
        await command.run()

    @interactions.slash_command(
        name="cadoizo",
        description="Utilise un Cadoizo",
        scopes=GUILD_IDS,
        options=[
            QTY_OPTION,
            GOLD_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def cadoizo_command(self, ctx: interactions.SlashContext, qty: int = 1, gold: str = "non"):
        command = UsableItemCommand(self.bot, ctx, param="cadoizo", qty=qty, gold=(gold == "oui"))
        await command.run()

    @interactions.slash_command(
        name="champi",
        description="Effecture un tirage de Champinocif",
        scopes=GUILD_IDS,
        options=[
            QTY_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def champi_command(self, ctx: interactions.SlashContext, qty: int = 1):
        command = UsableItemCommand(self.bot, ctx, param="champi", qty=qty)
        await command.run()

    @interactions.slash_command(
        name="paopou",
        description="Utilise un Paopou",
        scopes=GUILD_IDS,
        options=[
            QTY_OPTION,
            GOLD_OPTION,
            SAFE_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def paopou_command(self, ctx: interactions.SlashContext, qty: int = 1, gold: str = "non",
                             stealable: str = "oui"):
        command = ClassicItemCommand(self.bot, ctx, "paopou", param="remove", qty=qty, gold=(gold == "oui"),
                                     safe=(stealable == "non"))
        await command.run()

    @interactions.slash_command(
        name="fleurdegel",
        description="Utilise une Fleur de Gel",
        scopes=GUILD_IDS,
        options=[
            QTY_OPTION,
            GOLD_OPTION,
            SAFE_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def fleurdegel_command(self, ctx: interactions.SlashContext, qty: int = 1, gold: str = "non",
                                 stealable: str = "oui"):
        command = ClassicItemCommand(self.bot, ctx, "fleurdegel", param="remove", qty=qty, gold=(gold == "oui"),
                                     safe=(stealable == "non"))
        await command.run()
