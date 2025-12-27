from init_constants import VGS_FOLDER, TEAM_FOLDER
from init_items import item_manager
from manager.gimmick_manager import GimmickManager
from manager.mission_manager import MissionManager
from manager.quest_manager import QuestManager
from manager.roll_manager import RollManager
from manager.team_manager import TeamManager
from manager.v10.method_item_manager import MethodItemManager

# Load Managers (Items, Missions, Gimmicks, Teams, Roll)
mission_manager = MissionManager(VGS_FOLDER, item_manager.items)
quest_manager = QuestManager(VGS_FOLDER, item_manager.items)
gimmick_manager = GimmickManager(VGS_FOLDER)
team_manager = TeamManager(VGS_FOLDER, TEAM_FOLDER, quest_manager.quests)
roll_manager = RollManager(VGS_FOLDER)



