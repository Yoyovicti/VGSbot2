import warnings


class Method:
    def __init__(self, method_id, name: str, item_drop: float, mission_drop: float, quest_drop: float, charm_roll: float):
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
        if not -0.001 < charm_roll < 1.001:
            warnings.warn(f"{self.name}: invalid charm roll")
        self.charm_roll = charm_roll

    def __str__(self):
        return f"{self.name}"
