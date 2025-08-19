import os.path
from datetime import datetime
from typing import Dict

from definition.gimmick import GimmickList
from inventory.inventory import Inventory


class GimmickInventory(Inventory):
    def __init__(self, name: str, gimmick_list: GimmickList):
        super().__init__()
        self.img_path = gimmick_list.img_path
        self.gimmicks = gimmick_list.gimmicks

        self.name = name
        self.current_step = 1
        self.found = [{} for _ in range(len(self.gimmicks))]
        self.seen = []          # Clairvoyance
        self.unlocked = []      # Clairvoyance dorée

    def init(self, message_id: str):
        self.message_id = message_id
        self.clear()
        self.initialized = True

    def delete(self, base_path: str):
        self.message_id = "0"
        self.clear()
        self.initialized = False

    def clear(self):
        self.current_step = 1
        self.found = [{} for _ in range(len(self.gimmicks))]
        self.seen = []          # Clairvoyance
        self.unlocked = []      # Clairvoyance dorée

    def see(self, team_name: str, state: bool = True):
        if not state:
            if team_name in self.seen:
                self.seen.remove(team_name)
            return

        print(team_name, self.seen)
        if team_name not in self.seen:
            self.seen.append(team_name)

    def unlock(self, team_name: str, state: bool = True):
        if not state:
            if team_name in self.unlocked:
                self.unlocked.remove(team_name)
            return

        if team_name not in self.unlocked:
            self.unlocked.append(team_name)

    def set_found(self, step: int, team: str, date: datetime):
        if 0 < step < len(self.gimmicks) + 1:
            self.found[step - 1] = {
                "team": team,
                "date": str(date.date())
            }
        print(step, self.found[step-1])

    def get_found(self, step: int):
        return len(self.found[step - 1]) > 0

    def get_unlock(self, team: str):
        return team in self.unlocked

    def next_step(self):
        n_gimmicks = len(self.gimmicks)
        if self.current_step - 1 < n_gimmicks:
            if self.current_step < n_gimmicks:
                if self.found[self.current_step]:
                    self.current_step += 1
            self.current_step += 1

    def clear_seen(self):
        self.seen = []

    def clear_unlocked(self):
        self.unlocked = []

    def get_raw_data(self):
        data = {
            "message_id": self.message_id,
            "current_step": self.current_step,
            "found": self.found,
            "seen": self.seen,
            "unlocked": self.unlocked
        }
        print("data: ", data)
        return data

    def deserialize(self, data: Dict):
        print("data:", data)
        self.message_id = data["message_id"]
        self.current_step = data["current_step"]
        self.found = data["found"]
        self.seen = data["seen"]
        self.unlocked = data["unlocked"]

    def format_discord(self) -> str:
        string = f"__**{self.name}**__\n"

        for i in range(len(self.gimmicks)):
            gimmick = self.gimmicks[i]

            string += f"**Étape {i+1}/{len(self.gimmicks)} -** "
            found = self.found[i]

            if i != self.current_step - 1:
                if not found:
                    string += f"*À venir*\n"
                    continue

            string += f"**{gimmick.pokemon}** : "
            if found:
                string += f"*Validé le {self.found[i]['date']} par l'équipe {self.found[i]['team']} *\n"
                continue

            string += f"*En cours*\n"
            string += f"- Version : *{gimmick.version}*\n" if gimmick.version != "" else ""
            string += f"- Méthode : *{gimmick.method}*\n" if gimmick.method != "" else ""
            string += f"- Zone : *{gimmick.zone}*\n" if gimmick.zone != "" else ""
            string += f"- Bonus : ***x{gimmick.bonus}***\n"
            string += f"- Note : *{gimmick.note}*\n" if gimmick.note != "" else ""
            string += "\n"

        return string[:2000]

    def get_image_path(self, base_path):
        gimmicks_path = os.path.join(base_path, "gimmicks")
        list_path = os.path.join(gimmicks_path, self.img_path)
        step_path = os.path.join(list_path, f"{self.current_step}.png")
        return step_path


