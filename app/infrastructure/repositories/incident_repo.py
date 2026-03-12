import uuid
from typing import override

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import IncidentRepository
from app.models.incident import Incident


class SQLAlchemyIncidentRepository(IncidentRepository):
    """A repository implementation for Incident entities using SQLAlchemy."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @override
    async def create(self, incident: Incident) -> Incident:
        self.db.add(incident)
        try:
            await self.db.commit()
            await self.db.refresh(incident)
            return incident
        except IntegrityError:
            await self.db.rollback()
            raise

    @override
    async def get_by_id(self, incident_id: uuid.UUID) -> Incident | None:
        result = await self.db.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        return result.scalars().first()

    @override
    async def get_all_by_monitor(self, monitor_id: uuid.UUID) -> list[Incident]:
        result = await self.db.execute(
            select(Incident).where(Incident.monitor_id == monitor_id)
        )
        return list(result.scalars().all())
