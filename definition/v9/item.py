import warnings


class Item:
    def __init__(self, item_id, name: str, stealable: bool, transform_gold: bool, max_capacity: int, instant: bool, hidden: bool,
                 emote_id: str, gold_emote_id: str):
        self.id = item_id
        self.name = name
        self.stealable = stealable
        self.transform_gold = transform_gold
        self.max_capacity = max_capacity
        self.instant = instant
        self.hidden = hidden
        if emote_id == "0":
            warnings.warn(f"{self.name}: emote_id == 0")
        self.emote_id = emote_id
        if gold_emote_id == "0":
            warnings.warn(f"{self.name}: gold_emote_id == 0")
        self.gold_emote_id = gold_emote_id

    def get_emoji(self, gold: bool = False) -> str:
        if gold:
            return f"<:gold{self.id}:{self.gold_emote_id}>"
        return f"<:{self.id}:{self.emote_id}>"

    def __str__(self):
        return f"{self.name} {self.emote_id} {self.gold_emote_id}"
