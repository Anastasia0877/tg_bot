from aiogram.filters.callback_data import CallbackData


class FieldData(CallbackData, prefix='field'):
    id: str


class ChannelData(CallbackData, prefix='channel'):
    id: int
