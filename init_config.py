import os

DATA_FOLDER = "data"
BOT_FOLDER = os.path.join(DATA_FOLDER, "bot")

TOKEN_PATH = os.path.join(BOT_FOLDER, "token.txt")

with open(TOKEN_PATH, "r") as token_file:
    TOKEN = token_file.read()
