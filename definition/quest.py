from typing import List

from definition.mission import ItemReward


class QuestStep:
    def __init__(self, story: str, description: str):
        self.story = story
        self.description = description

    def __str__(self):
        quest_str = (f"{self.story}\n"
                     f"*{self.description}*")
        return quest_str


class Quest:
    def __init__(self, quest_id: str, name: str, steps: List[QuestStep], reward: ItemReward):
        self.id = quest_id
        self.name = name
        self.steps = steps
        self.reward = reward

    def format_discord(self, step: int) -> str:
        string = (f"**{self} - Étape {step + 1} / {len(self.steps)}**\n"
                  f"{self.steps[step]}")

        if self.reward.item_reward:
            string += f"\nRécompense finale : {self.reward}"
        return string

    def __str__(self):
        return f"Quête {self.id} - {self.name}"
