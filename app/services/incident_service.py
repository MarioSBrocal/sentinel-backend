import uuid
from typing import Any

from app.core.errors import AppError
from app.core.result import Err, Ok, Result
from app.domain.repositories import IncidentRepository
from app.models.incident import Incident, IncidentType


class IncidentService:
    def __init__(self, incident_repo: IncidentRepository):
        self.incident_repo = incident_repo

    async def create_incident(
        self,
        monitor_id: uuid.UUID,
        error_type: IncidentType,
        error_details: dict[str, Any] | None = None,
    ) -> Result[Incident, AppError]:
        """Create a new incident for a monitor."""

        new_incident = Incident(
            monitor_id=monitor_id,
            error_type=error_type,
            error_details=error_details,
        )

        result = await self.incident_repo.create(new_incident)

        if result.is_err():
            return Err(result.unwrap_err())

        return Ok(result.unwrap())

    async def get_incident_by_id(self, incident_id: int) -> Result[Incident, AppError]:
        """Retrieve a single incident by its ID."""

        result = await self.incident_repo.get_by_id(incident_id)

        if result.is_err():
            return Err(result.unwrap_err())

        return Ok(result.unwrap())

    async def get_monitor_incidents(
        self, monitor_id: uuid.UUID
    ) -> Result[list[Incident], AppError]:
        """Retrieve all incidents for a specific monitor."""

        result = await self.incident_repo.get_all_by_monitor(monitor_id)

        if result.is_err():
            return Err(result.unwrap_err())

        return Ok(result.unwrap())
