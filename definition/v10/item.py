class ItemFlags:
    STEALABLE       = 1 << 0
    TRANSFORM_GOLD  = 1 << 1
    INSTANT         = 1 << 2
    HIDDEN          = 1 << 3
    TARGET_SHINY    = 1 << 4
    TARGET_TEAM     = 1 << 5
    TARGET_SELF     = 1 << 6
    TARGET_ADV      = 1 << 7
    PROCESS         = 1 << 8

    MAPPING = {
        "stealable":        STEALABLE,
        "transform_gold":   TRANSFORM_GOLD,
        "instant":          INSTANT,
        "hidden":           HIDDEN,
        "target_shiny":     TARGET_SHINY,
        "target_team":      TARGET_TEAM,
        "target_self":      TARGET_SELF,
        "target_adv":       TARGET_ADV,
        "process":          PROCESS
    }

    def pack(**kwargs) -> int:
        result = 0
        for name, mask in ItemFlags.MAPPING.items():
            if kwargs.get(name, False):
                result |= mask
        return result


class Item:
    def __init__(self, id: str, name: str = "", max_capacity: int = -1, emote_id: int = 0, gold_emote_id: int = 0, description: str = "", flags: int = 0):
        self.id = id
        self.name = name
        self.max_capacity = max_capacity
        self.description = description
        self.emote_id = emote_id
        self.gold_emote_id = gold_emote_id
        self.flags = flags

    def get_emoji(self, gold: bool = False) -> str:
        if gold:
            return f"<:gold{self.id}:{self.gold_emote_id}>"
        return f"<:{self.id}:{self.emote_id}>"

    def get_flag(self, flag: int) -> bool:
        return (self.flags & flag) != 0

    def __str__(self):
        return f"{self.id} {self.name} {self.max_capacity} {self.flags} {self.emote_id} {self.gold_emote_id}"


