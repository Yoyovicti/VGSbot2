import json
import os
from typing import Dict

from definition.item import Item
from definition.mission import ItemReward
from definition.quest import QuestStep, Quest


class QuestManager:
    def __init__(self, base_path: str, items: Dict[str, Item]):
        quests_path = os.path.join(base_path, "quests.json")
        self.quests = {}
        with open(quests_path, "r") as quests_file:
            data = json.load(quests_file)

            print("===== QuestManager =====")
            for quest in data:
                name = data[quest]["name"]
                steps_data = data[quest]["steps"]
                reward = ItemReward(data[quest]["reward"], items)

                steps = []
                for step_elem in steps_data:
                    story = step_elem["story"]
                    description = step_elem["description"]
                    step = QuestStep(story, description)

                    steps.append(step)

                self.quests[quest] = Quest(quest, name, steps, reward)
                print(f"Loaded quest id: {quest}")
