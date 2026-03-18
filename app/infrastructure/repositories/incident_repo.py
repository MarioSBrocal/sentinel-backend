import uuid
from datetime import UTC, datetime
from typing import override

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError, DatabaseError, IncidentNotFoundError
from app.core.result import Err, Ok, Result
from app.domain.repositories import IncidentRepository
from app.models.incident import Incident


class SQLAlchemyIncidentRepository(IncidentRepository):
    """A repository implementation for Incident entities using SQLAlchemy."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @override
    async def create(self, incident: Incident) -> Result[Incident, AppError]:
        self.db.add(incident)

        try:
            await self.db.commit()
            await self.db.refresh(incident)
            return Ok(incident)
        except IntegrityError as e:
            await self.db.rollback()
            return Err(DatabaseError(detail=str(e)))

    @override
    async def get_by_id(self, incident_id: int) -> Result[Incident, AppError]:
        result = await self.db.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        incident = result.scalars().first()
        if not incident:
            return Err(IncidentNotFoundError(incident_id=incident_id))

        return Ok(incident)

    @override
    async def get_all_by_monitor(
        self, monitor_id: uuid.UUID
    ) -> Result[list[Incident], AppError]:
        result = await self.db.execute(
            select(Incident).where(Incident.monitor_id == monitor_id)
        )
        return Ok(list(result.scalars().all()))

    @override
    async def get_active_by_monitor(
        self, monitor_id: uuid.UUID
    ) -> Result[Incident, AppError]:
        result = await self.db.execute(
            select(Incident).where(
                Incident.monitor_id == monitor_id, Incident.resolved_at.is_(None)
            )
        )
        incident = result.scalars().first()
        if not incident:
            return Err(IncidentNotFoundError())
        return Ok(incident)

    @override
    async def resolve(self, incident_id: int) -> Result[None, AppError]:
        result = await self.get_by_id(incident_id)
        if result.is_err():
            return Err(result.unwrap_err())
        incident = result.unwrap()

        if incident.resolved_at is None:
            incident.resolved_at = datetime.now(UTC)
            try:
                await self.db.commit()
            except IntegrityError as e:
                await self.db.rollback()
                return Err(DatabaseError(detail=str(e)))

        return Ok(None)
