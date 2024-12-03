import os
from PyPDF2 import PdfReader  # Using PyPDF2 for PDF parsing
from dotenv import load_dotenv

load_dotenv()


class Utils:
    def __init__(self):
        pass  # No need for initialization as PyPDF2 does not require API keys or configurations

    def extract_text(self, file_path):
        try:
            # Initialize a PDF reader
            reader = PdfReader(file_path)
            text_content = []

            # Extract text from each page
            for page in reader.pages:
                if page.extract_text():
                    text_content.append(page.extract_text())

            return "\n".join(text_content)
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""

    def map_to_template(self):
        pass

    def render_latex(self):
        pass
