from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from bot.db.models import User


class AdminFilter(BaseFilter):
    async def __call__(self, event: TelegramObject, user: None | User):
        return user.is_admin if user else False
