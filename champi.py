from typing import List
from numpy import random


class Champi:
    def __init__(self, team_choices: List[str]):
        self.team_choices = team_choices

    def run(self):
        rng = random.Generator(random.MT19937())
        return rng.choice(self.team_choices)
