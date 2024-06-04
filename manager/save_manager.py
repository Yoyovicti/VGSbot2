import os.path


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


# def file_exists(folder_path: str, file_name: str) -> bool:
#     file_path = os.path.join(folder_path, file_name)
#     return os.path.exists(file_path)
