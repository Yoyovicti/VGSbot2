import json
import os

from gimmick import Gimmick


class GimmickManager:
    def __init__(self, base_path: str):
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
