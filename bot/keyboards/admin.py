from aiogram.filters.callback_data import CallbackData
from aiogram.types import Chat
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.structrures.callback_data import ChannelData


def universal(text: str, callback_data: CallbackData | str):
    kb = InlineKeyboardBuilder()

    kb.button(text=text, callback_data=callback_data)

    return kb.as_markup()


def menu(limit: int):
    kb = InlineKeyboardBuilder()

    kb.button(text="Изменить рекламу", callback_data="change_ad")
    kb.button(text=f"Изменить количество запросов:  {limit}", callback_data="change_query_amount")
    kb.button(text="Установить цель", callback_data="change_goal")
    kb.button(text="Добавить анкету", callback_data="add_people")
    kb.button(text="🔗 Каналы", callback_data="channels")
    kb.adjust(1)

    return kb.as_markup()


def channels_list(channels: list[Chat], activated: list[int]):
    kb = InlineKeyboardBuilder()

    for channel in channels:
        kb.button(text=f"{'🟢' if channel.id in activated else '🔴'} {channel.full_name if len(channel.full_name) < 64 else channel.full_name[64:] + '...'}", callback_data=ChannelData(id=channel.id))
    kb.button(text="🔙 К админке", callback_data="admin")
    kb.adjust(1)

    return kb.as_markup()

