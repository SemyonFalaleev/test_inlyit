import os
from dotenv import load_dotenv


class Settings:
    def __init__(self):
        load_dotenv()
        self.override_with_env_vars()

    def _get_required_env(self, var_name: str) -> str:
        value = os.getenv(var_name)
        if not value:
            raise ValueError(f"Необходимо указать переменную окружения {var_name}")
        return value

    def override_with_env_vars(self):

        self.db_url = self._get_required_env("db_url")
        self.secret_key_jwt = self._get_required_env("secret_key_jwt")
        self.algorithm_jwt = self._get_required_env("algorithm_jwt")
        self.token_expires = int(self._get_required_env("token_expires"))
        self.telegram_bot_token = self._get_required_env("telegram_bot_token")
        self.telegram_chat_id = int(self._get_required_env("telegram_chat_id"))


settings = Settings()
