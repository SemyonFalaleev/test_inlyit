import json

class Settings:
    def __init__(self, file_path='config.json'):
        self.file_path = file_path
        self.load_settings()
    def load_settings(self):
        try:
            with open(self.file_path, 'r') as file:
                self.settings = json.load(file)
        except FileNotFoundError:
            print(f"Файл {self.file_path} не найден.")
            exit(1)
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON: {e}")
            exit(1)

        self.db_url = self.settings.get("db_url")

settings = Settings()