import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


class VLMGenerator:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in .env")

        self.client = genai.Client(api_key=api_key)

        # Gemini multimodal model
        self.model = "gemini-3.6-flash"

    def find_latest_pdf(self):
        pdf_folder = Path("data/pdfs")

        pdf_files = list(pdf_folder.glob("*.pdf"))

        if not pdf_files:
            return None

        return max(pdf_files, key=lambda file: file.stat().st_mtime)

    def generate_answer(self, question, retrieved_results=None):

        pdf_path = self.find_latest_pdf()

        if pdf_path is None:
            return "No PDF document was found."

        print(f"\nSending document to Gemini: {pdf_path.name}")

        # Upload the PDF to Gemini
        uploaded_file = self.client.files.upload(
            file=str(pdf_path)
        )

        prompt = f"""
You are a helpful document analysis assistant.

Analyze the uploaded PDF carefully.

You can use:
- Text
- Images
- Tables
- Charts
- Diagrams
- Visual layout

Answer the user's question using only information available in the document.

If the user asks for a summary, give a concise summary of the document.

If the answer cannot be found in the document, clearly say that it is not available in the document.

User question:
{question}

Give a clear and easy-to-understand answer.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                uploaded_file,
                prompt
            ],
            config=types.GenerateContentConfig(
                temperature=0.2
            )
        )

        return response.text


if __name__ == "__main__":

    print("=" * 60)
    print("GEMINI MULTIMODAL DOCUMENT ANALYZER")
    print("=" * 60)

    generator = VLMGenerator()

    question = input("\nEnter your question: ")

    answer = generator.generate_answer(question)

    print("\nAnswer:")
    print("-" * 40)
    print(answer)

