import interactions

from init_config import TOKEN

bot = interactions.Client(token=TOKEN)

if __name__ == "__main__":
    print("Hello world!")

    bot.start()
