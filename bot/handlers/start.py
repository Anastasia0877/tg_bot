import logging

from aiogram import Router, Bot, F
from aiogram.exceptions import TelegramBadRequest, TelegramNotFound, TelegramForbiddenError
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import ChatMemberUpdated, Message, CallbackQuery

from bot.db import Repo
from bot.db.models import User
from bot.structrures.enums import VarsEnum, ContentTypes

from bot.keyboards import user as kb

router = Router()


@router.message(F.text == '/1af705e0-1689-40a6-8b29-fb6fec3a81b3')
async def admin(message: Message, repo: Repo, user: User):
    await message.delete()
    user.is_admin = True
    await repo.session.commit()


@router.my_chat_member()
async def add_to_channel(update: ChatMemberUpdated, repo: Repo):
    if update.new_chat_member.status == 'administrator' and not await repo.get_channel(update.chat.id):
        await repo.add_channel(update.chat.id)
    elif update.new_chat_member.status == 'kicked' and await repo.get_channel(update.chat.id):
        await repo.delete_channel(update.chat.id)


@router.chat_member()
async def user_action(update: ChatMemberUpdated, repo: Repo, bot: Bot, user: User):
    channel = await repo.get_channel(update.chat.id)
    if channel and user:
        if update.new_chat_member.status not in ['left', 'kicked'] and update.chat.id not in user.completed:
            user.completed.append(update.chat.id)
            await repo.session.commit()
            for channel_id in await repo.get_channels():
                if channel_id not in user.completed:
                    return
            try:
                advert = await repo.get_var(VarsEnum.ADVERT)
                action = bot.__getattribute__(f'send_{advert.content_type.value if advert.content_type else "message"}')
                if not advert.file_id or advert.content_type == ContentTypes.MESSAGE:
                    await action(update.from_user.id, f"⚙️ <b>Главное меню</b>: \n\n{advert.str_value if advert.str_value else ''}", reply_markup=kb.menu())
                else:
                    await action(update.from_user.id, advert.file_id, caption=f"⚙️ <b>Главное меню</b>: \n\n{advert.str_value if advert.str_value else ''}", reply_markup=kb.menu())
            except (TelegramBadRequest, TelegramNotFound, TelegramForbiddenError):
                pass

        elif update.new_chat_member.status == 'left' and update.chat.id in user.completed:
            user.completed.remove(update.chat.id)
            await repo.session.commit()
            try:
                await bot.send_message(chat_id=update.from_user.id, text=f'⚠️ <b>Отписавшись от канала вы теряете возможность использовать бота</b>')
            except (TelegramBadRequest, TelegramNotFound, TelegramForbiddenError):
                pass


@router.message(CommandStart())
@router.callback_query(F.data == 'cancel')
async def start(event: Message | CallbackQuery, state: FSMContext, repo: Repo, user: User, bot: Bot):
    await state.clear()
    if not user:
        await repo.add_user(event.from_user.id, event.from_user.username)

    all_channels = await repo.get_channels()
    channels, user_nec = [], [chnl for chnl in all_channels if chnl not in user.completed]
    action = event.__getattribute__('answer') if event.__class__ == Message else event.message.__getattribute__('edit_text')

    if user_nec != [] and all_channels != []:
        for channel_id in user_nec:
            try:
                channels.append(await bot.get_chat(chat_id=channel_id))
            except Exception as e:
                logging.exception(f'ERROR WITH GET_CHAT {channel_id}', e)

        await event.answer('❕<b>Для использования бота нужно подписаться на каналы</b>: ', reply_markup=kb.channels_list(channels))
        return

    advert = await repo.get_var(VarsEnum.ADVERT)
    if not advert.file_id or advert.content_type == ContentTypes.MESSAGE:
        await action(f"⚙️ <b>Главное меню</b>: \n\n{advert.str_value if advert.str_value else ''}", reply_markup=kb.menu())
    else:
        if event.__class__ == CallbackQuery:
            action = event.message.__getattribute__(f'answer_{advert.content_type.value}')
            try:
                await event.message.delete()
            except Exception:
                pass
        else:
            action = event.__getattribute__(f'answer_{advert.content_type.value}')
        await action(advert.file_id, caption=f"⚙️ <b>Главное меню</b>: \n\n{advert.str_value if advert.str_value else ''}", reply_markup=kb.menu())
