class Inventory:
    def __init__(self, message_id: str = "0"):
        self.initialized = False
        self.message_id = message_id

    def init(self, message_id: str):
        raise NotImplementedError

    def delete(self, base_path: str, team_name: str):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def save(self, base_path: str, team_name: str):
        raise NotImplementedError

    def format_discord(self, team_name: str):
        raise NotImplementedError
