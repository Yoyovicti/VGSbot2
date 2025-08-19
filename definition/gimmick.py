import datetime
from typing import List


class Find:
    def __init__(self, name: str, team: str, date: datetime.date):
        self.name = name
        self.team = team
        self.date = date

class Gimmick:
    def __init__(self, pokemon: str, version: str, method: str, zone: str, bonus: int, note: str):
        self.pokemon = pokemon
        self.version = version
        self.method = method
        self.zone = zone
        self.bonus = bonus
        self.note = note

class GimmickList:
    def __init__(self, gimmicks: List[Gimmick], img_path: str):
        self.gimmicks = gimmicks
        self.img_path = img_path
