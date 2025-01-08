from typing import Self

from PyPDF2 import PdfReader


class FileReader:

    def read_text_from_pdf(self: Self, filepath: str) -> str:
        pdf_reader = PdfReader(filepath)
        file_text = ""
        with open(filepath, 'rb') as f:
            for page in pdf_reader.pages:
                file_text += page.extract_text()
        return file_text
