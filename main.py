import interactions

from init_config import TOKEN


if __name__ == "__main__":
    bot = interactions.Client(token=TOKEN)
    bot.load_extension("extension.inventory_extension")
    bot.load_extension("extension.item_extension")
    bot.load_extension("extension.gimmick_extension")
    bot.load_extension("extension.mission_extension")
    bot.load_extension("extension.quest_extension")
    bot.start()
