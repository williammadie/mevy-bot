from typing import Self

from PyPDF2 import PdfReader

from mevy_bot.exceptions.unsupported_file_type_error import UnsupportedFileTypeError


class FileReader:

    def detect_format_and_read(self: Self, filepath: str) -> str:
        if filepath.endswith('.txt'):
            file_text = self.read_text_from_txt(filepath)
        elif filepath.endswith('.pdf'):
            file_text = self.read_text_from_pdf(filepath)
        else:
            raise UnsupportedFileTypeError(filepath)

        return file_text

    def read_text_from_txt(self: Self, filepath: str) -> str:
        with open(filepath, 'r', encoding='utf8') as f:
            file_text = f.read()
        return file_text

    def read_text_from_pdf(self: Self, filepath: str) -> str:
        pdf_reader = PdfReader(filepath)
        file_text = ""
        with open(filepath, 'rb') as f:
            for page in pdf_reader.pages:
                file_text += page.extract_text()
        return file_text
