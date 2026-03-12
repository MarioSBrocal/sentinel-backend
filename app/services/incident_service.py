import uuid

from app.core.errors import AppError, DatabaseError, IncidentNotFoundError
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
        error_details: str | None = None,
    ) -> Result[Incident, AppError]:
        """Create a new incident for a monitor."""
        new_incident = Incident(
            monitor_id=monitor_id,
            error_type=error_type,
            error_details=error_details,
        )

        try:
            saved_incident = await self.incident_repo.create(new_incident)
            return Ok(saved_incident)
        except Exception as e:
            return Err(DatabaseError(detail=str(e)))

    async def get_incident_by_id(self, incident_id: int) -> Result[Incident, AppError]:
        """Retrieve a single incident by its ID."""
        try:
            incident = await self.incident_repo.get_by_id(incident_id)
            if incident is None:
                return Err(IncidentNotFoundError(incident_id=incident_id))

            return Ok(incident)
        except Exception as e:
            return Err(DatabaseError(detail=str(e)))

    async def get_monitor_incidents(
        self, monitor_id: uuid.UUID
    ) -> Result[list[Incident], AppError]:
        """Retrieve all incidents for a specific monitor."""
        try:
            incidents = await self.incident_repo.get_all_by_monitor(monitor_id)
            return Ok(incidents)
        except Exception as e:
            return Err(DatabaseError(detail=str(e)))
