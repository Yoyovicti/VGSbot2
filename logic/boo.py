from numpy import random

from init_config import BOO_NAMES, item_manager


class Boo:
    def __init__(self, is_gold: bool = False):
        self.name = ""
        self.init_name(is_gold)

    def init_name(self, is_gold: bool = False):
        rng = random.Generator(random.MT19937())
        self.name = rng.choice(BOO_NAMES).replace("boo", item_manager.items["boo"].get_emoji(is_gold))
