import asyncio
import logging

from contextlib import suppress

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from openai import AsyncOpenAI

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage

from bot.db import sa_sessionmaker
from bot.middlewares.db import DbSessionMiddleware
from bot.middlewares.user import DbUserMiddleware
from bot.configreader import load_config
from bot.handlers import user, admin, start, user_channels

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    config = load_config()
    storage = MemoryStorage()
    session_factory = sa_sessionmaker(config.db)

    bot = Bot(config.bot.token, parse_mode="HTML")
    client = AsyncOpenAI(api_key=config.key.openai)
    scheduler = AsyncIOScheduler(timezone="Europe/Kiev")
    dp = Dispatcher(storage=storage)

    dp.update.outer_middleware(DbSessionMiddleware(session_factory))
    dp.update.outer_middleware(DbUserMiddleware())

    dp.message.filter(F.chat.type == "private")

    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(user.router)
    dp.include_router(user_channels.router)

    dp["config"] = config
    dp["session_factory"] = session_factory
    dp["client"] = client

    scheduler.start()

    # scheduler.add_job(notifier, trigger='interval', seconds=30, args=[session_factory, bot])

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    with suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(main())
