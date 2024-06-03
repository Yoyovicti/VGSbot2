import interactions
import numpy
from numpy import random

from commands.item_command import ItemCommand
from commands.usable_item_command import UsableItemCommand
from init_config import TEAM_FOLDER, item_manager, roll_manager, team_manager
from roll_manager import N_POS


class RollItemCommand(ItemCommand):
    def __init__(self, bot: interactions.Client, ctx: interactions.SlashContext, method: str, position: int,
                 qty: int = 1, charm: bool = False):
        super().__init__(bot, ctx)

        self.method = roll_manager.method_drops[method]
        self.position = min(position, N_POS)
        self.qty = qty
        self.charm = charm

    async def run(self):
        # TODO semi-random ?
        success = await self.load_team_info()
        if not success:
            return

        should_save = False
        for _ in range(self.qty):
            if await self.run_roll():
                should_save = True

        # Save inventory
        if should_save:
            self.item_inventory.save(TEAM_FOLDER, self.team.id)

        # Edit inventory message and send to item channel
        inv_msg = await self.item_channel.fetch_message(self.item_inventory.message_id)
        await inv_msg.edit(content=self.item_inventory.format_discord(self.team.name))

    async def run_roll(self, enable_charm: bool = True) -> bool:
        should_save = False
        message = "*Aucun objet tiré*"
        item = ""

        # Roll method
        meth_rng = random.Generator(random.MT19937())
        if meth_rng.random() < self.method.item_drop:
            item = self.roll_item()
            message = f"*Objet tiré:* {item_manager.items[item].get_emoji()}\n"

            if not item_manager.items[item].instant:
                self.item_inventory.add(item)
                should_save = True

        team_message = message
        boss_message = message

        if item == "champinocif":
            target_team = await self.run_champi()
            team_message += f"*Vos points s'envolent vers d'autres cieux...*\n"
            boss_message += (f"{item_manager.items[item].get_emoji()} *Les points du shiny s'en vont vers "
                             f"l'équipe* **{team_manager.teams[target_team].name}**\n")

        await self.item_channel.send(team_message)
        await self.ctx.send(boss_message)

        # Run Cadoizo after sending message
        if item == "cadoizo":
            command = UsableItemCommand(self.bot, self.ctx, "cadoizo", enable_save=False)
            await command.run()
            should_save = True

        # TODO CB
        # TODO Eclair

        if enable_charm and self.charm:
            charm_rng = random.Generator(random.MT19937())
            if charm_rng.random() < self.method.charm_roll:
                message = "*Le charme* **Cupidité irréversible** s'active, vous obtenez un tirage supplémentaire."
                await self.item_channel.send(message)
                await self.ctx.send(message)

                if await self.run_roll(enable_charm=False):
                    should_save = True

        return should_save

    def roll_item(self) -> str:
        pos_index = self.position - 1

        valid_items = []
        for item in item_manager.items:
            max_capacity = item_manager.items[item].max_capacity
            if max_capacity >= 0:
                total_qty = self.item_inventory.quantity(item) + self.item_inventory.quantity(item, safe=True)
                if total_qty >= max_capacity:
                    continue

            valid_items.append(item)

        # Compute weights (fix weights when some items are not valid)
        weights = [roll_manager.item_drops[item].drops[pos_index] for item in valid_items]
        probs = numpy.array(weights) * 1 / sum(weights)

        rng = random.Generator(random.MT19937())
        item = rng.choice(valid_items, p=probs)
        return item

    async def run_champi(self):
        # TODO merge with champi command
        valid_teams = [team for team in team_manager.teams if team != self.team.id]
        rng = random.Generator(random.MT19937())
        target_team = rng.choice(valid_teams)
        return target_team
