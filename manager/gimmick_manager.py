import json
import os

from manager import save_manager
from definition.gimmick import Gimmick


class GimmickManager:
    def __init__(self, base_path: str):
        self.base_path = base_path
        gimmick_path = os.path.join(base_path, "gimmicks.json")
        self.gimmicks = {}
        with open(gimmick_path, "r") as gimmick_file:
            data = json.load(gimmick_file)

            print("===== GimmickManager =====")
            for team in data:
                self.gimmicks[team] = {}
                for region in data[team]:
                    gimmick = Gimmick(region, data[team][region]["zone"], data[team][region]["pokemon"])
                    self.gimmicks[team][region] = gimmick
                print(f"Loaded gimmicks for team: {team}")

    def add_gimmick(self, team: str, region: str, zone: str, pokemon: str):
        self.edit_gimmick(team, region, zone, pokemon)

    def edit_gimmick(self, team: str, region: str, zone: str, pokemon: str):
        # Edit gimmick
        gimmick = Gimmick(region, zone, pokemon)
        self.gimmicks[team][region] = gimmick

        # Save data
        data = {
            team: {
                region: {
                    "zone": self.gimmicks[team][region].zone,
                    "pokemon": self.gimmicks[team][region].pokemon
                }
                for region in self.gimmicks[team]
            }
            for team in self.gimmicks
        }
        save_manager.save(self.base_path, "gimmicks.json", json.dumps(data, indent=4))
