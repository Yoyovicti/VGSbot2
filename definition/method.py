import warnings
from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class MethodDropRate:
    cat_id: str
    drop_rate: float

@dataclass(frozen=True)
class MethodItemDrop:
    item_id: str
    drop_factor: int

class Method:
    def __init__(self, method_id: str, name: str, cat_ids: List[str], drop_rates: List[int], item_ids: List[str], item_drops: List[List[int]]):
        self.id : str = method_id
        self.name : str = name

        self.drop_rates : Dict[str, MethodDropRate] = {}
        for i in range(len(cat_ids)):
            self.drop_rates[cat_ids[i]] = MethodDropRate(cat_ids[i], drop_rates[i])

        self.item_drop_table : List[List[List[MethodItemDrop]]] = []
        # Cadoizo
        for data_table in item_drops:
            table = []
            # Position
            for data_row in data_table:
                row = []
                # Item
                for i in range(len(item_ids)):
                    method_item_drop = MethodItemDrop(item_ids[i], data_row[i])
                    row.append(method_item_drop)
                table.append(row)
            self.item_drop_table.append(table)

    def get_item_drops(self, cadoizo: bool, pos_index: int) -> List[MethodItemDrop]:
        return self.item_drop_table[int(cadoizo)][pos_index]