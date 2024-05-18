import interactions

from boo import Boo
from cadoizo import Cadoizo
from champi import Champi
from init_config import GUILD_IDS, item_manager, team_manager, TEAM_FOLDER, roll_manager
from init_emoji import REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N, CROSS_MARK, KEYCAP_NUMBERS
from orbe import Orbe
from reaction_manager import ReactionManager
from roll import Roll


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

    # TEAM_OPTION = interactions.SlashCommandOption(
    #     name="cible",
    #     description="L'équipe visée",
    #     type=interactions.OptionType.STRING,
    #     required=True,
    #     argument_name="target",
    #     choices=[
    #         interactions.SlashCommandChoice(name=team_manager.teams[team].name, value=team)
    #         for team in team_manager.teams
    #     ]
    # )

    def __init__(self, bot: interactions.Client):
        self.add_ext_auto_defer()

        self.team = None
        self.item_inventory = None
        self.item_channel = None
        self.team_list = []

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
        success = await self.load_team_info(ctx)
        if not success:
            return

        # Add item and save to memory
        is_gold = gold == "oui"
        is_safe = stealable == "non"
        self.item_inventory.add(item, qty, is_gold, is_safe)
        self.item_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message and send to item channel
        inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
        await inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))
        message = f"{item_manager.items[item].get_emoji(is_gold)} x{qty}"
        if is_safe:
            message += " (non volable)"
        await self.item_channel.send(message + " ajouté à l'inventaire !")

        # Confirmation message
        await ctx.send("Inventaire mis à jour !")

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
        success = await self.load_team_info(ctx)
        if not success:
            return

        await self.run_remove(ctx, item, qty, gold == "oui", stealable == "non")

    @interactions.slash_command(
        name="tirage",
        description="Effectue un ou plusieurs tirages",
        scopes=GUILD_IDS,
        options=[
            METHODE_OPTION,
            POSITION_OPTION,
            QTY_OPTION,
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def tirage_command(self, ctx: interactions.SlashContext, method: str, pos: int, qty: int = 1):
        # TODO Carapace, Éclair
        # TODO Mission, Quest
        success = await self.load_team_info(ctx)
        if not success:
            return

        should_save = False

        for _ in range(qty):
            roll = Roll(self.item_inventory, method, pos)
            roll.run()

            message = "*Aucun objet tiré*"

            if roll.item != "":
                message = f"*Objet tiré:* {item_manager.items[roll.item].get_emoji()}\n"

                if not item_manager.items[roll.item].instant:
                    # Add item
                    self.item_inventory.add(roll.item)
                    should_save = True

            team_message = message
            boss_message = message

            if roll.item == "champinocif":
                valid_teams = [team for team in team_manager.teams if team != self.team.id]
                champi = Champi(valid_teams)
                target_team = champi.run()

                team_message += f"*Vos points s'envolent vers d'autres cieux...*"
                boss_message += (f"{item_manager.items[roll.item].get_emoji()} *Les points du shiny s'en vont vers "
                                 f"l'équipe **{team_manager.teams[target_team].name}***\n")

            await self.item_channel.send(team_message)
            await ctx.send(boss_message)

            # Run Cadoizo after sending roll result
            if roll.item == "cadoizo":
                await self.run_cadoizo(ctx, enable_save=False)
                should_save = True

        # Save inventory
        if should_save:
            self.item_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message and send to item channel
        inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
        await inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))

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
        success = await self.load_team_info(ctx)
        if not success:
            return

        await self.run_remove(ctx, "maxitomate", qty, gold == "oui", stealable == "non")

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
        success = await self.load_team_info(ctx)
        if not success:
            return

        await self.run_remove(ctx, "ruche", qty, gold == "oui", stealable == "non")

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
        success = await self.load_team_info(ctx)
        if not success:
            return

        await self.run_remove(ctx, "grappin", qty, gold == "oui", stealable == "non")

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
        success = await self.load_team_info(ctx)
        if not success:
            return

        # Remove item from inventory
        is_gold = gold == "oui"
        item = "fulgurorbe"
        success = await self.run_remove(ctx, item, qty, is_gold, stealable == "non", True)
        if not success:
            return
        await ctx.send("Inventaire mis à jour !")

        # Use item
        for _ in range(qty):
            orbe = Orbe(is_gold)
            if not orbe.success():
                await self.item_channel.send(f"{item_manager.items[item].get_emoji(is_gold)} a manqué sa cible et "
                                             f"s'est évaporée...")
                continue
            await self.item_channel.send(f"{item_manager.items[item].get_emoji(is_gold)} lancée avec succès !")

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
        success = await self.load_team_info(ctx)
        if not success:
            return

        await self.run_remove(ctx, "etoile", qty, gold == "oui", stealable == "non")

    @interactions.slash_command(
        name="boo",
        description="Utilise un Boo",
        scopes=GUILD_IDS,
        options=[
            SAFE_OPTION,
            GOLD_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def boo_command(self, ctx: interactions.SlashContext, stealable: str = "oui", gold: str = "non"):
        # Load origin team info
        success = await self.load_team_info(ctx)
        if not success:
            return

        is_gold = gold == "oui"
        is_safe = stealable == "non"
        cancel_message = "Opération annulée."

        # Load team names
        valid_teams = [team for team in team_manager.teams if team != self.team.id]
        n_runs = len(valid_teams) if is_gold else 1

        while n_runs > 0:
            item_emojis = await self.get_valid_boo_target_items()
            item_select_string = "Veuillez sélectionner l'objet que vous désirez voler :"
            item_select_message = await self.item_channel.send(item_select_string)
            item_reaction_manager = ReactionManager(item_select_message, [CROSS_MARK] + item_emojis)
            target_item = await item_reaction_manager.run()

            if target_item == CROSS_MARK:
                await item_select_message.reply(cancel_message)
                await ctx.send(cancel_message)
                if is_gold: continue
                return

            team_select_string = "Veuillez sélectionner l'équipe visée:\n\n"
            for i in range(n_runs):
                team_select_string += f"{KEYCAP_NUMBERS[i]} {team_manager.teams[valid_teams[i]].name}\n"
            team_select_message = await self.item_channel.send(team_select_string)
            team_reaction_manager = ReactionManager(team_select_message, [CROSS_MARK] + KEYCAP_NUMBERS[:n_runs])
            selected_reaction = await team_reaction_manager.run()

            if selected_reaction == CROSS_MARK:
                await team_select_message.reply(cancel_message)
                await ctx.send(cancel_message)
                if is_gold: continue
                return

            target_team = valid_teams[KEYCAP_NUMBERS.index(selected_reaction)]
            valid_teams.remove(target_team)
            n_runs -= 1

            # Check target inventory
            target_team = team_manager.teams[target_team]
            target_inventory = target_team.inventory_manager.item_inventory
            if not target_inventory.initialized:
                await team_select_message.reply(cancel_message)
                await ctx.send("Erreur: L'inventaire de la cible n'est pas initialisé.")
                continue

            # Check target item channel
            target_item_channel = await self.bot.fetch_channel(target_team.item_channel_id)
            if target_item_channel is None:
                await team_select_message.reply(cancel_message)
                await ctx.send("Erreur: Salon objets non trouvé pour la cible.")
                continue

            # All checks passed: remove boo from inventory
            if n_runs <= 0:
                success = await self.run_remove(ctx, "boo", 1, is_gold, is_safe, True)
                if not success:
                    return

            # Process boo
            boo = Boo(is_gold)

            # Set default item to clone
            sent_item = "clone"
            if target_inventory.quantity(sent_item) <= 0:
                if target_inventory.quantity(target_item) <= 0:
                    origin_msg = f"{boo.name} : *J'ai rien trouvé chef !*"
                    target_msg = (
                        f"{boo.name} : *Je passais chercher* {item_manager.items[target_item].get_emoji()} *par ici, mais "
                        f"il semblerait qu'il n'y ait rien. Bon ben je m'en vais snif...*")
                    await self.item_channel.send(origin_msg)
                    await target_item_channel.send(target_msg)

                    # Confirmation message
                    await ctx.send(f"{item_manager.items['boo'].get_emoji(is_gold)} Aucune modification effectuée !")
                    continue

                # Boo successful: set item to send
                sent_item = target_item

            # Process inventory
            qty_stolen = 1
            if is_gold:
                qty_stolen = target_inventory.quantity(sent_item)

            self.item_inventory.add(sent_item, qty_stolen)
            target_inventory.remove(sent_item, qty_stolen)

            # Save inventory
            self.item_inventory.save(TEAM_FOLDER, self.team.id)
            target_inventory.save(TEAM_FOLDER, target_team.id)

            # Edit inventory messages and send to item channel
            origin_inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
            target_inv_msg = await target_item_channel.fetch_message(target_inventory.message_id)
            await origin_inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))
            await target_inv_msg.edit(content=target_inventory.format_discord(target_team.name))
            origin_msg = f"{boo.name} : *Je reviens avec *{item_manager.items[sent_item].get_emoji()} *!*"
            target_msg = (f"{boo.name} : *Coucou, j'ai vu que vous m'aviez laissé* "
                          f"{item_manager.items[sent_item].get_emoji()} *, c'est vraiment gentil de votre part ! Allez "
                          f"bisous les nuls héhéhé...*")
            await self.item_channel.send(origin_msg)
            await target_item_channel.send(target_msg)

            # Confirmation message
            await ctx.send(f"{item_manager.items['boo'].get_emoji(is_gold)} Inventaires mis à jour !")

    async def get_valid_boo_target_items(self):
        # Get item emojis with corresponding reference to name
        items = item_manager.items
        item_emojis = []
        for item in items:
            if not items[item].stealable:
                continue

            classic_qty = self.item_inventory.quantity(item)
            safe_qty = self.item_inventory.quantity(item, safe=True)
            max_capacity = item_manager.items[item].max_capacity
            if -1 < max_capacity <= classic_qty + safe_qty:
                continue

            item_emojis.append(items[item].get_emoji())
        return item_emojis

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
        success = await self.load_team_info(ctx)
        if not success:
            return

        await self.run_remove(ctx, "picvenin", qty, gold == "oui", stealable == "non")

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
        # TODO reveal gimmick to the origin team

        success = await self.load_team_info(ctx)
        if not success:
            return

        await self.run_remove(ctx, "clairvoyance", qty, gold == "oui", stealable == "non")

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
        success = await self.load_team_info(ctx)
        if not success:
            return

        await self.run_remove(ctx, "klaxon", qty, gold == "oui", stealable == "non")

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
        # TODO ask for which gold item to use
        success = await self.load_team_info(ctx)
        if not success:
            return

        await self.run_remove(ctx, "ar", qty, gold == "oui", stealable == "non")

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
        success = await self.load_team_info(ctx)
        if not success:
            return

        await self.run_cadoizo(ctx, qty, gold == "oui", False)

    async def run_cadoizo(self, ctx: interactions.SlashContext, qty: int = 1, is_gold: bool = False,
                          cancel_option: bool = True, enable_save: bool = True):
        cancel_message = "*Tirage annulé*"
        should_save = False

        for _ in range(qty):
            n_items = 5 if is_gold else 3
            cadoizo = Cadoizo(self.item_inventory, n_items, is_gold)
            choices = cadoizo.run()

            contents_message = f"*Le* {item_manager.items['cadoizo'].get_emoji(is_gold)} *contient :* "
            for i in range(n_items):
                if is_gold:
                    contents_message += f"\n{KEYCAP_NUMBERS[i]} {choices[i]}"
                    continue
                contents_message += f"{item_manager.items[choices[i]].get_emoji()} "
            contents_message += "\n"
            await ctx.send(contents_message + "*En attente du choix des participants...*")

            cadoizo_message = await self.item_channel.send(
                f"{item_manager.items['cadoizo'].get_emoji(is_gold)} "
                f"*Choisissez un lot avec les réactions ci-dessous :*"
            )
            reaction_choices = KEYCAP_NUMBERS[:n_items]
            if cancel_option:
                reaction_choices = [CROSS_MARK] + reaction_choices
            if not is_gold and self.item_inventory.quantity("ar") + self.item_inventory.quantity("ar", safe=True) + self.item_inventory.quantity("ar", gold=True) > 0:
                reaction_choices += [f"{item_manager.items['cadoizo'].get_emoji(True)}"]

            reaction_manager = ReactionManager(cadoizo_message, reaction_choices)
            selected_reaction = await reaction_manager.run()

            if selected_reaction == CROSS_MARK:
                await cadoizo_message.reply(contents_message + cancel_message)
                await ctx.send(cancel_message)
                continue

            if selected_reaction == "goldcadoizo":
                if self.item_inventory.quantity("ar") > 0:
                    self.item_inventory.remove("ar")
                elif self.item_inventory.quantity("ar", safe=True):
                    self.item_inventory.remove("ar", safe=True)
                else:
                    self.item_inventory.remove("ar", gold=True)
                should_save = True

                await self.run_cadoizo(ctx, is_gold=True, cancel_option=False, enable_save=False)
                continue

            choice = choices[KEYCAP_NUMBERS.index(selected_reaction)]

            if is_gold:
                contents = roll_manager.gold_cadoizo[choice]
                result_message = (f"*Lot obtenu :* {choice}\n"
                                  f"*Objet(s) obtenus :*\n")

                for elem in contents:
                    elem_item = elem["item"]
                    elem_qty = elem["qty"]
                    elem_is_gold = elem["gold"] == 1

                    result_message += f"{item_manager.items[elem_item].get_emoji(elem_is_gold)} x{elem_qty}\n"
                    if elem_is_gold or not item_manager.items[elem_item].instant:
                        self.item_inventory.add(elem_item, qty=elem_qty, gold=elem_is_gold)
                        should_save = True
                        continue

                    # TODO process instant items for gold cadoizo
                    continue

                await cadoizo_message.reply(contents_message + result_message)
                await ctx.send(result_message)
                continue

            # Add item to inventory
            if not item_manager.items[choice].instant:
                self.item_inventory.add(choice)
                should_save = True

            # Send result message
            result_message = f"*Objet obtenu :* {item_manager.items[choice].get_emoji()}"
            await cadoizo_message.reply(contents_message + result_message)
            await ctx.send(result_message)

        # Save inventory
        if enable_save and should_save:
            self.item_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message and send to item channel
        inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
        await inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))

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
        self.init_team_info()

        self.team = team_manager.get_team(str(ctx.channel_id))
        if self.team is None:
            await ctx.send("Erreur: Équipe non trouvée. Assurez-vous d'utiliser la commande dans le bon channel.")
            return

        valid_teams = [team for team in team_manager.teams if team != self.team.id]

        for _ in range(qty):
            champi = Champi(valid_teams)
            target_team = champi.run()

            item = "champinocif"
            message = (f"{item_manager.items[item].get_emoji()} *Les points du shiny s'en vont vers l'équipe "
                       f"**{team_manager.teams[target_team].name}***")
            await ctx.send(message)

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
        success = await self.load_team_info(ctx)
        if not success:
            return

        await self.run_remove(ctx, "paopou", qty, gold == "oui", stealable == "non")

    @interactions.slash_command(
        name="d6",
        description="Utilise un D6",
        scopes=GUILD_IDS,
        options=[
            QTY_OPTION,
            GOLD_OPTION,
            SAFE_OPTION
        ],
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        dm_permission=False
    )
    async def d6_command(self, ctx: interactions.SlashContext, qty: int = 1, gold: str = "non",
                         stealable: str = "oui"):
        # TODO do something more ?
        success = await self.load_team_info(ctx)
        if not success:
            return

        await self.run_remove(ctx, "d6", qty, gold == "oui", stealable == "non")

    async def run_remove(self, ctx: interactions.SlashContext, item: str, qty: int = 1, is_gold: bool = False,
                         is_safe: bool = False, silent: bool = False) -> bool:
        # Check quantity
        if self.item_inventory.quantity(item, is_gold, is_safe) < qty:
            return await self.run_remove_checks(ctx, item, qty, is_gold, is_safe, silent)

        # Remove item and save inventory
        self.item_inventory.remove(item, qty, is_gold, is_safe)
        self.item_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message
        inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
        await inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))

        # Send messages
        if not silent:
            await self.item_channel.send(
                f"{item_manager.items[item].get_emoji(is_gold)} x{qty} retiré de l'inventaire !")
            await ctx.send("Inventaire mis à jour !")

        return True

    async def run_remove_checks(self, ctx: interactions.SlashContext, item: str,
                                qty: int = 1, is_gold: bool = False, is_safe: bool = False, silent=False) -> bool:
        classic_qty = self.item_inventory.quantity(item)

        if is_gold or is_safe or classic_qty + self.item_inventory.quantity(item, safe=True) < qty:
            await ctx.send("Erreur: L'inventaire ne contient pas assez de cet objet.")
            return False

        # Ask for confirmation in case safe items will be removed
        warning_msg = await ctx.send("Cette opération va retirer des objets non volables de l'inventaire. "
                                     "Souhaitez-vous continuer ?")
        reaction_manager = ReactionManager(warning_msg, [REGIONAL_INDICATOR_O, REGIONAL_INDICATOR_N])
        reaction = await reaction_manager.run()
        if reaction != REGIONAL_INDICATOR_O:
            await ctx.send("Opération annulée.")
            return False

        # Remove items from inventory and save
        self.item_inventory.remove(item, classic_qty)
        self.item_inventory.remove(item, qty - classic_qty, safe=True)
        self.item_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory
        inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
        await inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))

        # Send messages
        if not silent:
            await self.item_channel.send(f"{item_manager.items[item].get_emoji()} x{qty} retiré de l'inventaire !")
            await ctx.send("Inventaire mis à jour !")

        return True
