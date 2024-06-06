import json
import os

from definition.mission import Mission, Reward, ItemReward


class MissionManager:
    def __init__(self, base_path: str):
        missions_path = os.path.join(base_path, "missions.json")
        self.missions = {}
        with open(missions_path, "r") as missions_file:
            data = json.load(missions_file)

            print("===== MissionManager =====")
            for mission in data:
                name = data[mission]["name"]
                description = data[mission]["description"]

                reward_data = data[mission]["reward"]
                points = reward_data["points"]
                items = [ItemReward(item) for item in reward_data["items"]]
                reward = Reward(points, items)

                self.missions[mission] = Mission(mission, name, description, reward)
                print(f"Loaded mission id: {mission}")
