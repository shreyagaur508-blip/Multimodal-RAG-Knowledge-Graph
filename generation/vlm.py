import os
import re
import sys

import fitz


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# DIRECTORIES
# ============================================================

PDF_DIR = os.path.join(
    PROJECT_ROOT,
    "data",
    "pdfs"
)


PAGES_DIR = os.path.join(
    PROJECT_ROOT,
    "data",
    "pages"
)


# ============================================================
# LOCAL DOCUMENT ANSWER GENERATOR
# ============================================================

class VLMGenerator:

    def __init__(self):

        print("Initializing local document answer generator...")

        os.makedirs(
            PDF_DIR,
            exist_ok=True
        )

        print("Local document answer generator ready!")


    # ========================================================
    # FIND PDF
    # ========================================================

    def find_pdf(self):

        pdf_files = []

        for filename in os.listdir(PDF_DIR):

            if filename.lower().endswith(".pdf"):

                pdf_files.append(
                    os.path.join(
                        PDF_DIR,
                        filename
                    )
                )

        if not pdf_files:

            return None

        # Most recently modified PDF
        pdf_files.sort(
            key=os.path.getmtime,
            reverse=True
        )

        return pdf_files[0]


    # ========================================================
    # EXTRACT PDF TEXT
    # ========================================================

    def extract_document_text(self):

        pdf_path = self.find_pdf()

        if not pdf_path:

            return "", None

        try:

            document = fitz.open(
                pdf_path
            )

            pages = []

            for page_number, page in enumerate(
                document,
                start=1
            ):

                text = page.get_text(
                    "text"
                )

                if text.strip():

                    pages.append({
                        "page_number": page_number,
                        "text": text.strip()
                    })

            document.close()

            full_text = "\n\n".join(
                page["text"]
                for page in pages
            )

            return full_text, pages

        except Exception as error:

            print(
                "PDF text extraction error:",
                error
            )

            return "", None


    # ========================================================
    # CLEAN TEXT
    # ========================================================

    def clean_text(self, text):

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()


    # ========================================================
    # FIND IMPORTANT SENTENCES
    # ========================================================

    def important_sentences(
        self,
        text
    ):

        text = self.clean_text(
            text
        )

        if not text:

            return []

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text
        )

        useful = []

        for sentence in sentences:

            sentence = sentence.strip()

            if len(sentence) < 15:

                continue

            # Ignore verification-code noise
            lower = sentence.lower()

            if (
                "verification code" in lower
                and len(sentence) > 100
            ):

                continue

            useful.append(
                sentence
            )

        return useful


    # ========================================================
    # GENERATE DOCUMENT SUMMARY
    # ========================================================

    def generate(
        self,
        question,
        retrieved_pages
    ):

        document_text, pages = (
            self.extract_document_text()
        )

        # ----------------------------------------------------
        # No PDF text
        # ----------------------------------------------------

        if not document_text:

            if retrieved_pages:

                page_numbers = []

                for page in retrieved_pages:

                    number = page[
                        "page_number"
                    ]

                    if number not in page_numbers:

                        page_numbers.append(
                            number
                        )

                return (
                    "I found relevant page(s) "
                    + ", ".join(
                        str(x)
                        for x in page_numbers
                    )
                    + ", but I could not extract "
                      "text from the PDF to generate "
                      "a detailed answer."
                )

            return (
                "I could not find enough information "
                "in the document to answer the question."
            )


        # ----------------------------------------------------
        # DOCUMENT SUMMARY REQUEST
        # ----------------------------------------------------

        question_lower = question.lower()

        summary_words = [
            "briefly",
            "brief",
            "summarize",
            "summary",
            "about the document",
            "describe the document",
            "what is this document",
            "tell me about the document"
        ]

        is_summary_request = any(
            word in question_lower
            for word in summary_words
        )


        sentences = self.important_sentences(
            document_text
        )


        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        if is_summary_request:

            selected = []

            # Take the first useful sentences
            for sentence in sentences:

                if sentence not in selected:

                    selected.append(
                        sentence
                    )

                if len(selected) >= 4:

                    break


            if selected:

                summary = " ".join(
                    selected
                )

                return (
                    "Briefly: "
                    + summary
                )


        # ----------------------------------------------------
        # QUESTION-BASED SEARCH
        # ----------------------------------------------------

        keywords = re.findall(
            r"[a-zA-Z]{3,}",
            question_lower
        )


        stop_words = {
            "what",
            "when",
            "where",
            "which",
            "who",
            "whom",
            "why",
            "how",
            "does",
            "this",
            "that",
            "about",
            "document",
            "tell",
            "briefly",
            "please",
            "give"
        }


        keywords = [
            word
            for word in keywords
            if word not in stop_words
        ]


        matching_sentences = []


        for sentence in sentences:

            sentence_lower = (
                sentence.lower()
            )

            score = sum(
                1
                for keyword in keywords
                if keyword in sentence_lower
            )

            if score > 0:

                matching_sentences.append(
                    (
                        score,
                        sentence
                    )
                )


        matching_sentences.sort(
            key=lambda x: x[0],
            reverse=True
        )


        # ----------------------------------------------------
        # RETURN MATCHING ANSWER
        # ----------------------------------------------------

        if matching_sentences:

            best_sentences = [
                item[1]
                for item in matching_sentences[:3]
            ]

            return (
                "Based on the document: "
                + " ".join(
                    best_sentences
                )
            )


        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        return (
            "I could not find a specific answer "
            "to that question in the extracted "
            "document content."
        )


    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):

        pass


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("LOCAL DOCUMENT ANSWER GENERATOR")
    print("=" * 60)


    generator = VLMGenerator()


    try:

        question = input(
            "\nEnter your question: "
        )


        answer = generator.generate(
            question,
            []
        )


        print("\nAnswer:")
        print("-" * 60)
        print(answer)


    finally:

        generator.close()