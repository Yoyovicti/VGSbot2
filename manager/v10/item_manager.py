import os
import re

import yaml

from definition.v10.item import Item, ItemFlags


def get_from_path(data, path):
    """Get a nested value from dict given 'a.b.c' path"""
    keys = path.split(".")
    val = data
    for k in keys:
        if k not in val:
            return path
        val = val[k]
    return val

def resolve_string(s: str, data):
    """Replace {x.y} in a string with corresponding dict value"""
    # print(s)
    pattern = re.compile(r"{(.*?)}")
    match = pattern.search(s)
    if not match:
        return s

    path = match.group(1)
    replacement = str(get_from_path(data, path))
    return s[:match.start()] + replacement + s[match.end():]

def walk(x, data, changed_flag):
    """Walk through dict/list/str and resolve placeholders"""
    if isinstance(x, dict):
        return {k: walk(v, data, changed_flag) for k, v in x.items()}
    elif isinstance(x, list):
        return [walk(v, data, changed_flag) for v in x]
    elif isinstance(x, str):
        new_val = resolve_string(x, data)
        if new_val != x:
            changed_flag[0] = True
        return new_val
    else:
        return x

def resolve_data(data, max_iter = 10):
    """Resolve placeholders in dict"""
    for _ in range(max_iter):
        changed_flag = [False]
        data = walk(data, data, changed_flag)  # rebuild fresh
        if not changed_flag[0]:
            break
    return data

class ItemManager:
    def __init__(self, base_path: str):
        items_path = os.path.join(base_path, "v10/items.yaml")
        with open(items_path, "r") as items_file:
            data = resolve_data(yaml.safe_load(items_file))

        self.items = {}
        print("===== ItemManager =====")
        for item_id, item_data in data.items():
            flags = ItemFlags.pack(
                stealable=      item_data["stealable"],
                transform_gold= item_data["transform_gold"],
                instant=        item_data["instant"],
                hidden=         item_data["hidden"],
                target_shiny=   item_data["target_shiny"],
                target_self=    item_data["target_self"],
                target_adv=     item_data["target_adv"],
                process=        item_data["process"]
            )
            item_inst = Item(
                id=item_id,
                name=item_data["name"],
                max_capacity=item_data["max_capacity"],
                emote_id=item_data["emote_id"],
                gold_emote_id=item_data["gold_emote_id"],
                description=item_data["description_base"],
                flags=flags
            )

            self.items[item_id] = item_inst
            print(f"Loaded item: {item_inst}")
