from typing import List

from aiogram.filters.callback_data import CallbackData
from aiogram.types import Chat
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.structrures.bot import info_fields
from bot.structrures.callback_data import FieldData


def universal(text: str, callback_data: str | CallbackData | None):
    kb = InlineKeyboardBuilder()

    kb.button(text=text, callback_data=callback_data)

    return kb.as_markup()


def menu():
    kb = InlineKeyboardBuilder()

    # kb.button(text='💰 Пополнить баланс', callback_data='add_money')
    # kb.button(text='🎟 Оплатить подписку', callback_data='pay_sub')
    kb.button(text='🤖 Диалог с ИИ', callback_data='call_ai')
    kb.button(text='🔎 Сделать запрос', callback_data='make_query')
    kb.adjust(1)

    return kb.as_markup()


def field_types():
    kb = InlineKeyboardBuilder()

    for field in info_fields.keys():
        kb.button(text=info_fields[field], callback_data=FieldData(id=field))
    kb.button(text='❌ Закрыть', callback_data='cancel')
    kb.adjust(2, 2, 2, 2, 2, 1)

    return kb.as_markup()


def sub():
    kb = InlineKeyboardBuilder()

    # kb.button(text='Оплатить подписку', callback_data='pay_sub')
    # kb.button(text='Оплатить запрос (10 рублей)', callback_data='pay_query')
    kb.button(text='❌ Закрыть', callback_data='cancel')
    kb.adjust(1)

    return kb.as_markup()


def sub_payment():
    kb = InlineKeyboardBuilder()

    kb.button(text="Пополнить баланс", callback_data="add_money")
    kb.button(text="Оплатить подписку", callback_data="pay_sub")
    kb.button(text='❌ Закрыть', callback_data='cancel')
    kb.adjust(1)

    return kb.as_markup()


def tariffs():
    kb = InlineKeyboardBuilder()

    kb.button(text="Безлимит (500 рублей)", callback_data="pay_unlimit")
    kb.button(text='❌ Закрыть', callback_data='cancel')
    kb.adjust(1)

    return kb.as_markup()


def payment():
    kb = InlineKeyboardBuilder()

    kb.button(text="Пополнить баланс", callback_data="add_money")
    kb.button(text="Оплатить подписку сразу", callback_data="pay_now")
    kb.button(text='❌ Закрыть', callback_data='cancel')
    kb.adjust(1)

    return kb.as_markup()


def channels_list(channels: List[Chat]):
    kb = InlineKeyboardBuilder()

    for channel in channels:
        kb.button(text=channel.full_name if len(channel.full_name) < 64 else channel.full_name[64:] + '...', url=channel.invite_link)

    kb.adjust(1)

    return kb.as_markup()

