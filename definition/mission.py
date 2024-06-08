from typing import List, Dict


class ItemReward:
    def __init__(self, items: Dict[str, List[int]]):
        # id: [classic, gold]
        self.items = items


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
