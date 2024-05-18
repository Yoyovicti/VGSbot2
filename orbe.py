from numpy import random


class Orbe:
    SUCCESS_RATE = 0.5

    def __init__(self, gold: bool = False):
        self.gold = gold

    def success(self) -> bool:
        if self.gold:
            return True

        rng = random.Generator(random.MT19937())
        r = rng.random()
        return r < Orbe.SUCCESS_RATE
