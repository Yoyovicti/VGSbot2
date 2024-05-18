import interactions

from init_config import TOKEN


if __name__ == "__main__":
    bot = interactions.Client(token=TOKEN)
    bot.load_extension("extension.inventory_extension")
    bot.start()
