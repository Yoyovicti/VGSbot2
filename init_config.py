import os

from manager.item_manager import ItemManager
from manager.gimmick_manager import GimmickManager
from manager.mission_manager import MissionManager
from manager.quest_manager import QuestManager
from manager.roll_manager import RollManager
from manager.team_manager import TeamManager

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

ORBE_SUCCESS_RATE = 0.5

# Load Managers (Items, Missions, Gimmicks, Teams, Roll)
item_manager = ItemManager(VGS_FOLDER)
mission_manager = MissionManager(VGS_FOLDER, item_manager.items)
quest_manager = QuestManager(VGS_FOLDER, item_manager.items)
gimmick_manager = GimmickManager(VGS_FOLDER)
team_manager = TeamManager(VGS_FOLDER, TEAM_FOLDER, item_manager.items, mission_manager.missions, quest_manager.quests,
                           gimmick_manager.gimmicks)
roll_manager = RollManager(VGS_FOLDER)



