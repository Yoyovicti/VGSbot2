import warnings


class Method:
    def __init__(self, method_id, name: str, item_drop: float, mission_drop: float, quest_drop: float):
        self.id = method_id
        self.name = name

        if item_drop + mission_drop + quest_drop < 0.001:
            warnings.warn(f"{self.name}: Missing drop table")
        if not -0.001 < item_drop < 1.001:
            warnings.warn(f"{self.name}: invalid item drop")
        self.item_drop = item_drop
        if not -0.001 < mission_drop < 1.001:
            warnings.warn(f"{self.name}: invalid mission drop")
        self.mission_drop = mission_drop
        if not -0.001 < quest_drop < 1.001:
            warnings.warn(f"{self.name}: invalid quest drop")
        self.quest_drop = quest_drop

    def __str__(self):
        return f"{self.name}"
