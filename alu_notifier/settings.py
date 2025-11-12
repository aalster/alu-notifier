import os
from datetime import datetime

from pydantic import BaseModel

path = "data.json"

class Settings(BaseModel):
    daily_gift_link: str = "https://shop.gameloft.com/games/Asphalt_Unite"
    daily_gift_notification: bool = True
    next_daily_gift_time: datetime | None = None


class SettingsService:
    cache = None

    def save(self, settings: Settings):
        with open(path, "w", encoding="utf-8") as f:
            f.write(settings.model_dump_json(indent=2))
        self.cache = None

    def get(self) -> Settings:
        if not self.cache:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.cache = Settings.model_validate_json(content)
            else:
                self.cache = Settings()
        return Settings(**self.cache.model_dump())


SETTINGS_SERVICE = SettingsService()