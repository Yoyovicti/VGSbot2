import os

from item_manager import ItemManager
from roll_manager import RollManager
from team_manager import TeamManager

DATA_FOLDER = "data"

BOT_FOLDER = os.path.join(DATA_FOLDER, "bot")
VGS_FOLDER = os.path.join(DATA_FOLDER, "vgs")
TEAM_FOLDER = os.path.join(DATA_FOLDER, "team")

TOKEN_PATH = os.path.join(BOT_FOLDER, "token.txt")
GUILD_IDS_PATH = os.path.join(BOT_FOLDER, "guild_ids.txt")
BOO_NAMES_PATH = os.path.join(BOT_FOLDER, "boo.txt")

# Load Token
TOKEN = ""
with open(TOKEN_PATH, "r") as token_file:
    TOKEN += token_file.read()

# Load Guild ids
GUILD_IDS = []
with open(GUILD_IDS_PATH, "r") as guild_ids_file:
    for guild_id in guild_ids_file:
        GUILD_IDS.append(guild_id)

BOO_NAMES = []
with open(BOO_NAMES_PATH, "r") as boo_names_file:
    for boo_name in boo_names_file:
        BOO_NAMES.append(boo_name.rstrip())

# Load Managers (Items, Teams, Roll)
item_manager = ItemManager(VGS_FOLDER)
team_manager = TeamManager(VGS_FOLDER, TEAM_FOLDER, item_manager.items)
roll_manager = RollManager(VGS_FOLDER)



