from typing import List

from definition.mission import ItemReward


class QuestStep:
    def __init__(self, story: str, description: str, reward: ItemReward):
        self.story = story
        self.description = description
        self.reward = reward

    def __str__(self):
        quest_str = (f"{self.story}\n"
                     f"*{self.description}*")
        if self.reward.item_reward:
            quest_str += f"\nRécompense: {self.reward}"
        return quest_str


class Quest:
    def __init__(self, quest_id: str, name: str, steps: List[QuestStep]):
        self.id = quest_id
        self.name = name
        self.steps = steps

    def format_discord(self, step: int) -> str:
        return (f"**{self} - Étape {step + 1} / {len(self.steps)}**\n"
                f"{self.steps[step]}")

    def __str__(self):
        return f"Quête {self.id} - {self.name}"
