import json
import os
from typing import Dict

from definition.item import Item
from definition.mission import Mission, Reward, ItemReward


class MissionManager:
    def __init__(self, base_path: str, items: Dict[str, Item]):
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
                item_rewards = [ItemReward(item, items) for item in reward_data["items"]]
                reward = Reward(points, item_rewards)

                self.missions[mission] = Mission(mission, name, description, reward)
                print(f"Loaded mission id: {mission}")
