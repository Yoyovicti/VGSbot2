from typing import List, Dict

from definition.item import Item


class ItemReward:
    def __init__(self, item_reward: Dict[str, List[int]], items: Dict[str, Item]):
        # id: [classic, gold]
        self.item_reward = item_reward
        self.items = items

    def __str__(self):
        string = ""
        c = 0
        for item in self.item_reward:
            for i in range(2):
                if self.item_reward[item][i] > 0:
                    if c > 0:
                        string += ", "
                    string += f"{self.items[item].get_emoji(i == 1)}x{self.item_reward[item][i]}"
                    c += 1
        return string


class Reward:
    def __init__(self, points: int, items: List[ItemReward]):
        self.points = points
        self.items = items


class Mission:
    def __init__(self, mission_id: str, name: str, description: str, reward: Reward):
        self.id = mission_id
        self.name = name
        self.description = description
        self.reward = reward

    def format_discord(self) -> str:
        return (f"**{self}**\n"
                f"{self.description}")

    def __str__(self):
        return f"Mission {self.id} - {self.name}"
