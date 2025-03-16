from fastapi import FastAPI
from pydantic import BaseModel

from mevy_bot.legifrance.law_text_downloader import LawTextDownloader

app = FastAPI()


class CodeDto(BaseModel):
    name: str


@app.post("/code")
async def download_code(code_dto: CodeDto):
    downloader = LawTextDownloader()
    code_content = downloader.fetch_code(code_dto.name)
    return {"code": code_dto.name, "content": code_content}
