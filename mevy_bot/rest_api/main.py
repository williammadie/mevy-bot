import tempfile

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from mevy_bot.legifrance.law_text_downloader import LawTextDownloader

app = FastAPI()


class CodeDto(BaseModel):
    name: str


@app.post("/code")
async def download_code(code_dto: CodeDto):
    downloader = LawTextDownloader()
    code_content = downloader.fetch_code(code_dto.name)

    with tempfile.NamedTemporaryFile(delete=False) as fp:
        fp.write(code_content.encode('utf8'))

        return FileResponse(
            fp.name,
            filename=f"{code_dto.name}.txt"
        )
