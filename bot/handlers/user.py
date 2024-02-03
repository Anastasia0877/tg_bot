from openai import AsyncOpenAI
from datetime import datetime

from aiogram import Router, F
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ErrorEvent, ChatMemberUpdated

from bot.db import Repo
from bot.db.models import User, Query
from bot.filters.user import CompletedFilter
from bot.structrures.bot import info_fields
from bot.structrures.callback_data import FieldData
from bot.structrures.enums import VarsEnum, ContentTypes
from bot.structrures.states import MakeQueryStates, AddMoneyStates, TalkAIStates

import bot.keyboards.user as kb

router = Router()

router.message.filter(CompletedFilter())
router.callback_query.filter(CompletedFilter())


@router.message(F.text == '/id')
async def user_id(message: Message):
    await message.answer(f"<code>{message.from_user.id}</code>")


@router.callback_query(F.data == 'make_query')
async def make_query(query: CallbackQuery):
    try:
        await query.message.edit_text(text="🔎 Выберите по какому полю производить поиск информации:", reply_markup=kb.field_types())
    except:
        try:
            await query.message.delete()
        except:
            pass
        finally:
            await query.message.answer(text="🔎 Выберите по какому полю производить поиск информации:",reply_markup=kb.field_types())


@router.callback_query(FieldData.filter())
async def field_data(query: CallbackQuery, state: FSMContext, callback_data: FieldData):
    await state.update_data(field_id=callback_data.id)
    await state.set_state(MakeQueryStates.value)
    await query.message.edit_text("🔎 Отправьте текст который содержится в этом поле, <b>миниум 3 символа</b>:", reply_markup=kb.universal(text='❌ Закрыть', callback_data='cancel'))


@router.message(MakeQueryStates.value)
async def process_update(message: Message, repo: Repo, state: FSMContext):
    state_data = await state.get_data()
    if len(message.text) < 3:
        await message.answer("⚠️ В запросе должно быть минимум <b>3 символа</b>\n\n"
                             "🔎 Отправьте текст который содержится в этом поле ещё раз:", reply_markup=kb.universal(text='❌ Закрыть', callback_data='cancel'))
        return

    result = await repo.get_info(state_data['field_id'], message.text)

    if result == []:
        await message.answer(f"🔎 По вашему запросу ничего не найдено. Попробуйте ввести другое значение", reply_markup=kb.universal(text='❌ Закрыть', callback_data='cancel'))
    else:
        await state.set_state()
        await state.update_data(result=[info.id for info in result])
        await message.answer(f"🔎 По вашему запросу найдено <b>{len(result)}</b> результатов. Первый из них:\n\n"+"\n".join([f'<b>» {info_fields[field]}</b>: {result[0].__getattribute__(field)}' for field in ["id", "login"]]), reply_markup=kb.universal("Получить полную информацию", "get_all_info"))


@router.callback_query(F.data == 'get_all_info')
async def get_all_info(query: CallbackQuery, repo: Repo, user: User, state: FSMContext):
    state_data = await state.get_data()
    await state.set_state()

    if not user.pay_forever:
        limit = await repo.get_var(VarsEnum.LIMIT)
        if user.pay_until and user.pay_until < datetime.now().astimezone():
            await query.message.edit_text("❕<b>У вас кончилась подписка</b>. Вы можете продолжить подписку или купить доступ к этому запросу сейчас", reply_markup=kb.sub())
            return
        elif limit.int_value and await repo.get_count_queries(query.from_user.id) >= limit.int_value:
            # Вы превысили лимит бесплатных запросов</b>. Вы можете продолжить подписку или купить доступ к этому запросу сейчас
            await query.message.edit_text("❕<b>Вы превысили лимит запросов</b>. Повторите запрос через 24 часа", reply_markup=kb.sub())
            return

    res = await repo.get_info_by_ids(state_data['result'])
    repo.session.add(Query(user_id=query.from_user.id, result=state_data['result']))
    await repo.session.commit()

    await query.message.edit_text("\n\n".join("\n".join([f'<b>» {info_fields[field]}</b>: {result.__getattribute__(field)}' for field in info_fields.keys()]) for result in res) + "\n\nДля возвращения в главное меню: /start")


@router.callback_query(F.data == 'pay_query')
async def pay_query(query: CallbackQuery, repo: Repo, user: User, state: FSMContext):
    if user.balance < 10:
        await state.clear()
        await query.message.edit_text("❕<b>У вас недостаточно денег на балансе</b>", reply_markup=kb.sub_payment())
    else:
        user.balance -= 10
        user.pay_forever = True
        await repo.session.commit()

        await get_all_info(query, repo, user, state)


@router.callback_query(F.data == 'pay_sub')
async def pay_sub(query: CallbackQuery, user: User):
    if user.pay_forever:
        text = "бесконечная подписка"
    elif not user.pay_forever:
        text = "нет подписки"
    elif user.pay_until > datetime.now().astimezone():
        text = user.pay_until - datetime.now().astimezone()
    else:
        text = "у вас кончилась подписка"

    if user.pay_forever:
        kwargs = {"text": f"💰 Ваш баланс:  <b>{user.balance} рублей</b>\n» До конца подписки осталось: {text}", "reply_markup": kb.universal("Назад", "cancel")}
    else:
        kwargs = {"text": f"💰 Ваш баланс:  <b>{user.balance} рублей</b>\n» До конца подписки осталось: {text}\n\n📍Выберите тариф для пополнения: ", "reply_markup": kb.tariffs()}

    try:
        await query.message.edit_text(**kwargs)
    except:
        try:
            await query.message.delete()
        except:
            pass
        finally:
            await query.message.answer(**kwargs)


@router.callback_query(F.data == 'pay_unlimit')
async def pay_unlimit(query: CallbackQuery, repo: Repo, user: User):
    if user.balance < 500:
        await query.message.edit_text("❕<b>У вас недостаточно денег на балансе</b>", reply_markup=kb.payment())
    else:
        user.balance -= 500
        user.pay_forever = True
        await repo.session.commit()

        await query.message.edit_text("🎟 <b>Вы успешно приобрели тариф за счёт баланса!</b> Нажмите /start для выхода в главное меню")


### ПЛАТІЖКА РАЗ
@router.callback_query(F.data == 'pay_now')
async def pay_now(query: CallbackQuery, repo: Repo, user: User):
    url = " "

    await query.message.edit_text(f"Ссылка для оплаты: {url}")


@router.callback_query(F.data == 'add_money')
async def add_money(query: CallbackQuery, state: FSMContext):
    await state.set_state(AddMoneyStates.amount)

    try:
        await query.message.edit_text("💰 На сколько рублей вы хотите пополнить баланс?", reply_markup=kb.universal(text='❌ Закрыть', callback_data='cancel'))
    except:
        try:
            await query.message.delete()
        except:
            pass
        finally:
            await query.message.answer("💰 На сколько рублей вы хотите пополнить баланс?", reply_markup=kb.universal(text='❌ Закрыть', callback_data='cancel'))


### ПЛАТІЖКА ДВА
@router.message(AddMoneyStates.amount)
async def add_amount(message: Message, state: FSMContext):
    num = int(message.text)


@router.callback_query(F.data == 'call_ai')
async def call_ai(query: CallbackQuery, state: FSMContext):
    try:
        await query.message.edit_text("🤖 Вы приступили к разговору с ИИ", reply_markup=kb.universal("❌ Завершить разговор", "cancel"))
    except:
        try:
            await query.message.delete()
        except:
            pass
        finally:
            await query.message.answer("🤖 Вы приступили к разговору с ИИ", reply_markup=kb.universal("❌ Завершить разговор", "cancel"))
    await state.set_state(TalkAIStates.talk)


@router.message(TalkAIStates.talk)
async def talk_ai(message: Message, state: FSMContext, client: AsyncOpenAI):
    msg = await message.answer("🤖 ИИ думает...")
    state_data = await state.get_data()   # Дістаємо дані, які пов'язані з користувачем із ОЗУ хоста

    messages = state_data.get("messages")   # Отримуємо історію запитів користувача

    if not messages:   # Якщо історії немає, починаємо зберігати її
        messages = []

    messages.append(                                 #
        {"role": "user", "content": message.text},   # Записуємо запит користувача до історії
    )                                                #
    chat = await client.chat.completions.create(   #
        messages=messages, model="gpt-3.5-turbo"   # Створюємо чат користувача з ШІ, передаючи історію чату(messages) та версію ШІ(model)
    )                                              #
    reply = chat.choices[0].message.content   # Отримуємо відповідь на запит користувача від ШІ
    messages.append({"role": "assistant", "content": reply})   # Зберігаємо до історії відповідь від ШІ
    await state.update_data(messages=messages)   # Зберігаємо історію в ОЗУ хоста для використання в подальших запитаннях
    await msg.edit_text(f"🤖 Ответ: <b>{reply}</b>", reply_markup=kb.universal("❌ Завершить разговор", "cancel"))
