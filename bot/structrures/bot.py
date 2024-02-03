from aiogram import Bot

from bot.db import Repo

info_fields = {
    "id": "ID",
    "login": "Логин",
    "state": "Данные",
    "contacts": "Контакты",
    "links_first": "Ссылки №1",
    "links_second": "Ссылки №2",
    "links_third": "Ссылки №3",
    "term": "Термин",
    "amount": "Покупки",
    "notes": "Записка"
}


async def notifier(session_factory, bot: Bot):
    async with session_factory() as session:
        repo = Repo(session)

        for info in await repo.get_for_notify():
            text = "Ваш запрос был обновлен:\n"+"\n".join([f"{info_fields[field]}: {info.__getattribute__(field)}" for field in info_fields.keys()])
            for user_id in await repo.get_user_ids_by_info(info.id):
                try:
                    await bot.send_message(chat_id=user_id, text=text)
                except Exception:
                    pass

