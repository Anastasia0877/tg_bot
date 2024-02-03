from datetime import datetime, timedelta
from typing import Sequence, Any

from sqlalchemy import select, func, update, distinct, delete, desc
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import User, Variable, Info, Query, Payment, Channel
from bot.structrures.enums import VarsEnum


class BaseRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def scalar_one(self, stmt):
        return (await self.session.execute(stmt)).scalar_one()

    async def scalars_all(self, stmt):
        return (await self.session.scalars(stmt)).all()


class Repo(BaseRepo):

    async def add_user(self, user_id: int, username: str | None):
        stmt = insert(User).values(id=user_id, username=username).on_conflict_do_nothing().returning(User)
        user = await self.session.execute(stmt)
        await self.session.commit()
        return user.scalar()

    async def get_user(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_var(self, t: VarsEnum) -> Variable | None:
        return await self.session.get(Variable, t)

    async def get_info(self, field: str, condition: str) -> Sequence[Info]:
        query = getattr(Info, field)
        return await self.scalars_all(select(Info).where(query.contains(condition)))

    async def get_count_queries(self, user_id: int) -> int:
        return await self.session.scalar(select(func.count(Query.id)).where(Query.user_id == user_id).where(datetime.now() - timedelta(hours=24) <= Query.created_at)) or 0

    async def get_sum_payments(self) -> int:
        return await self.session.scalar(select(func.sum(Payment.amount))) or 0

    async def get_for_notify(self) -> Sequence[Info]:
        return await self.scalars_all(update(Info).where(Info.updated_notif == True).values(updated_notif=False).returning(Info))

    async def get_info_by_ids(self, ids: list[int]) -> Sequence[Info]:
        return await self.scalars_all(select(Info).where(Info.id.in_(ids)))

    async def get_user_ids_by_info(self, info_id: int) -> Sequence[int]:
        return await self.scalars_all(select(distinct(Query.user_id)).where(Query.result.contains(info_id)))

    async def add_channel(self, channel_id: int):
        self.session.add(Channel(id=channel_id))
        await self.session.commit()

    async def delete_channel(self, channel_id: int):
        await self.session.execute(delete(Channel).where(Channel.id == channel_id))
        await self.session.commit()

    async def get_channel(self, channel_id: int) -> Channel | None:
        return await self.session.get(Channel, channel_id)

    async def get_all_channels(self) -> Sequence[int]:
        return await self.scalars_all(select(Channel.id).order_by(desc(Channel.id)))

    async def get_channels(self) -> Sequence[int]:
        return await self.scalars_all(select(Channel.id).where(Channel.is_active == True))

