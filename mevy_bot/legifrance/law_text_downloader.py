import os
from typing import Self

from pylegifrance import recherche_CODE
from dotenv import load_dotenv
from lxml.html import fromstring
from unidecode import unidecode

from mevy_bot.path_finder import PathFinder
from mevy_bot.legifrance.models.code import Code, Section

load_dotenv()


class LawTextDownloader:

    def fetch_code(self: Self, code_name: str) -> str:
        results = recherche_CODE(code_name=code_name)
        code = Code.model_validate(results[0])
        return self.build_code(code)

    def download_code(self: Self, code_name: str) -> None:
        code_content = self.fetch_code(code_name=code_name)

        filename = unidecode(code_name).lower().replace(" ", "_")

        data_dir = PathFinder.data_storage_auto()
        filepath = os.path.join(data_dir, f"{filename}.txt")
        with open(filepath, 'w', encoding='utf8') as f:
            f.write(code_content)

    def build_code(self: Self, code: Code) -> str:
        code_content = f"{code.title}\n\n"
        for section in sorted(code.sections, key=lambda x: x.intOrdre):
            code_content += self.build_section(section)
        return code_content

    def build_section(self: Self, section: Section) -> str:
        section_content = f"{section.title}\n\n"
        for article in sorted(section.articles, key=lambda x: x.intOrdre):
            section_content += f"Article n°{article.num}\n"
            html_tree = fromstring(article.content)
            section_content += f"{html_tree.text_content().strip()}\n\n"

        for section in sorted(section.sections, key=lambda x: x.intOrdre):
            section_content += self.build_section(section)
        return section_content


if __name__ == '__main__':
    downloader = LawTextDownloader()
    downloader.download_code("Code civil")
    # downloader.download_code("Code général des impôts")
