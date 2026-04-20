from fastapi import HTTPException, status

from src.repository.studioinfo import StudioInfoRepository
from src.schemas.studioinfo import StudioInfoResponse, StudioInfoUpdate


class StudioInfoService:
    def __init__(self, repository: StudioInfoRepository):
        self.repository = repository

    def _to_response(self, row) -> StudioInfoResponse:
        """Конвертирует строку БД в схему ответа."""
        return StudioInfoResponse(
            year_opened=row["year_opened"],
            students_count=row["students_count"],
            phone=row["phone"],
            address=row["address"],
            working_hours=row["working_hours"],
            email=row["email"],
        )

    async def get(self) -> StudioInfoResponse:
        row = await self.repository.get()
        if not row:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Информация о студии не найдена",
            )
        return self._to_response(row)

    async def update(self, data: StudioInfoUpdate) -> StudioInfoResponse:
        fields = data.model_dump(exclude_none=True)
        if not fields:
            return await self.get()
        row = await self.repository.update(fields)
        if not row:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Информация о студии не найдена",
            )
        return self._to_response(row)
