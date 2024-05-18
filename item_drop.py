import warnings
from typing import List


class ItemDrop:
    def __init__(self, item_id: str, cado: float, regular: List[float]):
        self.id = item_id
        if not -0.001 < cado < 1.001:
            warnings.warn(f"{self.id}: Invalid cado drop")
        self.cado = cado

        for drop in regular:
            if not -0.001 < drop < 1.001:
                warnings.warn(f"{self.id}: Invalid regular drop")
        self.drops = regular

    def __str__(self):
        return f"{self.id}"

