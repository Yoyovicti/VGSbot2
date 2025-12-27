import interactions

from init_constants import TOKEN, EXTENSIONS

if __name__ == "__main__":
    print("===== Main =====")
    bot = interactions.Client(token=TOKEN)

    print("> Extensions")
    for extension in EXTENSIONS:
        bot.load_extension(extension)
        print(f"Loaded extension: {extension}")


    bot.start()
