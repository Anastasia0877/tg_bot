import logging

from aiogram import Router, F, Bot
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.db import Repo
from bot.db.models import Info
from bot.filters.admin import AdminFilter
import bot.keyboards.admin as kb
from bot.structrures.bot import info_fields
from bot.structrures.callback_data import ChannelData
from bot.structrures.enums import VarsEnum, ContentTypes
from bot.structrures.states import AddPeopleStates, ChangeAdStates, ChangeQueryAmountStates, ChangeGoalStates

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())


@router.callback_query(F.data == 'admin')
@router.message(F.text == '/admin')
async def admin_panel(event: Message | CallbackQuery, state: FSMContext, repo: Repo):
    await state.clear()

    action = event.__getattribute__('answer') if event.__class__ == Message else event.message.__getattribute__('edit_text')
    await action(f"Админ-панель\n\nВсего собрано: {await repo.get_sum_payments()}/{(await repo.get_var(VarsEnum.GOAL)).int_value} рублей", reply_markup=kb.menu((await repo.get_var(VarsEnum.LIMIT)).int_value))


@router.callback_query(F.data == 'add_people')
async def add_people(query: CallbackQuery, state: FSMContext):
    await state.set_state(AddPeopleStates.text)
    l = list(info_fields.values())
    l.remove("ID")
    await query.message.edit_text("Отправьте анкету в таком формате:\n"+"\n".join(["{" + str(field) + "}" for field in l]), reply_markup=kb.universal("🔙 К админке", "admin"))


@router.message(AddPeopleStates.text)
async def add_people_text(message: Message, repo: Repo, state: FSMContext):
    l = list(info_fields.values())
    l.remove("ID")
    l = len(l)
    texts = message.text.split("\n")
    if len(texts) != l:
        await message.answer("Количество полей не соответствует шаблону")
        return
    await state.clear()

    fields = list(info_fields.keys())
    fields.remove("id")

    repo.session.add(Info(**{fields[i]: texts[i] for i in range(len(fields))}))
    await repo.session.commit()
    await message.answer("Успешно создано!", reply_markup=kb.universal("🔙 К админке", "admin"))


@router.callback_query(F.data == 'change_ad')
async def change_ad(query: CallbackQuery, state: FSMContext):
    await state.set_state(ChangeAdStates.text)
    await query.message.edit_text("Отправьте сообщение с текстом рекламы, можно с фото/видео/анимацией", reply_markup=kb.universal("🔙 К админке", "admin"))


@router.message(ChangeAdStates.text)
async def change_ad(message: Message, repo: Repo, state: FSMContext):
    await state.clear()

    advert = await repo.get_var(VarsEnum.ADVERT)
    advert.str_value = message.html_text
    if message.content_type in [ContentType.PHOTO, ContentType.VIDEO, ContentType.ANIMATION]:
        advert.content_type = ContentTypes(message.content_type.value)
        file = getattr(message, message.content_type.value)[-1] if message.content_type == ContentType.PHOTO else getattr(message, message.content_type.value)
        advert.file_id = file.file_id
    else:
        advert.content_type = ContentTypes.MESSAGE
    await repo.session.commit()
    await message.answer("Успешно изменено!")

    await admin_panel(message, state, repo)


@router.callback_query(F.data == 'change_query_amount')
async def change_query_amount(query: CallbackQuery, state: FSMContext):
    await state.set_state(ChangeQueryAmountStates.amount)
    await query.message.edit_text("Отправьте число запросов", reply_markup=kb.universal("🔙 К админке", "admin"))


@router.message(ChangeQueryAmountStates.amount)
async def change_query_amount(message: Message, repo: Repo, state: FSMContext):
    try:
        num = int(message.text)
        if num < 0:
            await message.answer("Укажите число больше или равно 0")
        else:
            limit = await repo.get_var(VarsEnum.LIMIT)
            limit.int_value = num
            await repo.session.commit()

            await message.answer("Успешно изменено!")
            await admin_panel(message, state, repo)
    except ValueError:
        await message.answer("Это не число, отправьте еще раз")


@router.callback_query(F.data == 'change_goal')
async def change_goal(query: CallbackQuery, state: FSMContext):
    await state.set_state(ChangeGoalStates.amount)
    await query.message.edit_text("Отправьте необходимое число", reply_markup=kb.universal("🔙 К админке", "admin"))


@router.message(ChangeGoalStates.amount)
async def change_goal_amount(message: Message, repo: Repo, state: FSMContext):
    await state.clear()
    try:
        num = int(message.text)
        if num < 0:
            await message.answer("Укажите число больше или равно 0")
        else:
            goal = await repo.get_var(VarsEnum.GOAL)
            goal.int_value = num
            await repo.session.commit()

            await message.answer("Успешно изменено!")
            await admin_panel(message, state, repo)
    except ValueError:
        await message.answer("Это не число, отправьте еще раз")


@router.callback_query(ChannelData.filter())
@router.callback_query(F.data == 'channels')
async def channels_manage(query: CallbackQuery, repo: Repo, bot: Bot, callback_data: ChannelData | None = None):
    activated = await repo.get_channels()

    if callback_data:
        channel = await repo.get_channel(callback_data.id)
        if channel.id in activated:
            channel.is_active = False
            activated.remove(channel.id)
        else:
            channel.is_active = True
            activated.append(channel.id)
        await repo.session.commit()

    channels = []
    for channel_id in await repo.get_all_channels():
        try:
            channels.append(await bot.get_chat(chat_id=channel_id))
        except Exception as e:
            logging.exception(f'ERROR WITH GET_CHAT {channel_id}', e)

    await query.message.edit_text('🔗 <b>Подключенные каналы</b>: ', reply_markup=kb.channels_list(channels, activated))

