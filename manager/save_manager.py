import interactions
import os.path
import pytz
import datetime
import zipfile


def load(folder_path: str, file_name: str) -> str:
    data = ""
    file_path = os.path.join(folder_path, file_name)

    try:
        with open(file_path, "r") as save_file:
            data = save_file.read()
            print(f"SaveManager: Loaded data at {file_path}")

    except Exception as e:
        print(f"SaveManager: Failed to load save file at {file_path}: {e}")

    finally:
        return data


def save(folder_path: str, file_name: str, data: str):
    file_path = os.path.join(folder_path, file_name)

    try:
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
            print(f"SaveManager: Save folder created at {folder_path}.")

        with open(file_path, "w") as save_file:
            save_file.write(data)
            print(f"SaveManager: File saved at {file_path}.")

    except Exception as e:
        print(f"SaveManager: Failed to save file at {file_path}: {e}")


def delete(folder_path: str, file_name: str):
    file_path = os.path.join(folder_path, file_name)

    try:
        os.remove(file_path)
        print(f"SaveManager: File {file_path} deleted successfully.")

    except Exception as e:
        print(f"SaveManager: Failed to delete file at {file_path}: {e}")


async def backup_data(ctx: interactions.SlashContext, folder_path: str):
    timezone = pytz.timezone("Europe/Paris")
    curr_time = datetime.datetime.now(timezone).strftime("%Y%m%d_%H%M%S")
    zip_filename = f"data_{curr_time}.zip"
    # await utils.send_ctx_message(ctx, f"Creating zip as {zip_filename}...")

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))

    file = interactions.File(zip_filename)
    await ctx.send(files=[file])
    # await bot._http.create_message(payload={}, channel_id=ctx.channel_id, files=[file])
    os.remove(zip_filename)
