from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from bot.db import Repo
from bot.db.models import User


class CompletedFilter(BaseFilter):
    async def __call__(self, event: TelegramObject, user: None | User, repo: Repo):
        if user:
            channels = await repo.get_channels()
            return [chnl for chnl in channels if chnl not in user.completed] == []
        else:
            return False
