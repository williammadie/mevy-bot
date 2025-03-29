import tempfile
from fastapi import APIRouter

from fastapi.responses import FileResponse
from pydantic import BaseModel

from mevy_bot.services.legifrance_service import LegifranceService

router = APIRouter(prefix="/legifrance", tags=["Legifrance"])


class CodeDto(BaseModel):
    name: str


@router.post("/code")
async def download_code(code_dto: CodeDto):
    legifrance_service = LegifranceService()
    code_content = legifrance_service.fetch_code(code_dto.name)

    with tempfile.NamedTemporaryFile(delete=False) as fp:
        fp.write(code_content.encode('utf8'))

        return FileResponse(
            fp.name,
            filename=f"{code_dto.name}.txt"
        )
