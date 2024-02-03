import logging

from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery

from bot.db import Repo
from bot.db.models import User

from bot.keyboards import user as kb

router = Router()


@router.message()
async def necessary_channels(message: Message, repo: Repo, user: User, bot: Bot):
    channels = []
    for channel_id in [chnl for chnl in await repo.get_channels() if chnl not in user.completed]:
        try:
            channels.append(await bot.get_chat(chat_id=channel_id))
        except Exception as e:
            logging.exception(f'ERROR WITH GET_CHAT {channel_id}', e)

    await message.answer('❕<b>Для использования бота нужно подписаться на каналы</b>: ', reply_markup=kb.channels_list(channels))


@router.callback_query()
async def necessary_channels(query: CallbackQuery, repo: Repo, user: User, bot: Bot):
    channels = []
    for channel_id in [chnl for chnl in await repo.get_channels() if chnl not in user.completed]:
        try:
            channels.append(await bot.get_chat(chat_id=channel_id))
        except Exception as e:
            logging.exception(f'ERROR WITH GET_CHAT {channel_id}', e)

    await query.message.answer('❕<b>Для использования бота нужно подписаться на каналы</b>: ', reply_markup=kb.channels_list(channels))
