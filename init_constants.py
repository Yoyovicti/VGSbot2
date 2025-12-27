import os

DATA_FOLDER = "data"

BOT_FOLDER = os.path.join(DATA_FOLDER, "bot")
VGS_FOLDER = os.path.join(DATA_FOLDER, "vgs")
TEAM_FOLDER = os.path.join(DATA_FOLDER, "team")

TOKEN_PATH = os.path.join(BOT_FOLDER, "token.txt")
GUILD_IDS_PATH = os.path.join(BOT_FOLDER, "guild_ids.txt")
BOO_NAMES_PATH = os.path.join(BOT_FOLDER, "boo.txt")


EXTENSIONS = [
    "extension.inventory_extension",
    "extension.item_extension",
    "extension.gimmick_extension",
    "extension.quest_extension",
    "extension.backup_extension",
]

GIMMICK_CHANNEL = 529337222768492554
# GIMMICK_CHANNEL = 1381265455787933766 #

# Load Token
TOKEN = ""
with open(TOKEN_PATH, "r") as token_file:
    TOKEN += token_file.read()

# Load Guild ids
GUILD_IDS = []
with open(GUILD_IDS_PATH, "r") as guild_ids_file:
    for guild_id in guild_ids_file:
        GUILD_IDS.append(guild_id.rstrip())

BOO_NAMES = []
with open(BOO_NAMES_PATH, "r") as boo_names_file:
    for boo_name in boo_names_file:
        BOO_NAMES.append(boo_name.rstrip())

ORBE_SUCCESS_RATE = 0.5
GOLD_ORBE_SUCCESS_RATE = 0.25