import os
import re
import sys

import pymupdf


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# PDF DIRECTORY
# ============================================================

PDF_DIR = os.path.join(
    PROJECT_ROOT,
    "data",
    "pdfs"
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
    # FIND LATEST PDF
    # ========================================================

    def find_pdf(self):

        pdf_files = []

        for filename in os.listdir(PDF_DIR):

            if filename.lower().endswith(".pdf"):

                full_path = os.path.join(
                    PDF_DIR,
                    filename
                )

                pdf_files.append(full_path)


        if not pdf_files:

            return None


        # Latest uploaded PDF
        pdf_files.sort(
            key=os.path.getmtime,
            reverse=True
        )

        return pdf_files[0]


    # ========================================================
    # EXTRACT PDF CONTENT
    # ========================================================

    def extract_document(self):

        pdf_path = self.find_pdf()

        if not pdf_path:

            return {
                "filename": None,
                "text": "",
                "lines": [],
                "pages": []
            }


        print(
            f"Reading document: "
            f"{os.path.basename(pdf_path)}"
        )


        try:

            document = pymupdf.open(
                pdf_path
            )

            all_text = []

            all_lines = []

            page_data = []


            for page_number, page in enumerate(
                document,
                start=1
            ):

                text = page.get_text(
                    "text"
                )


                # Save page information
                page_data.append({
                    "page_number": page_number,
                    "text": text
                })


                if text:

                    all_text.append(
                        text
                    )


                    for line in text.splitlines():

                        line = line.strip()

                        if line:

                            all_lines.append(
                                line
                            )


            document.close()


            combined_text = "\n".join(
                all_text
            )


            return {
                "filename": os.path.basename(
                    pdf_path
                ),
                "text": combined_text,
                "lines": all_lines,
                "pages": page_data
            }


        except Exception as error:

            print(
                "PDF extraction error:",
                error
            )

            return {
                "filename": os.path.basename(
                    pdf_path
                ),
                "text": "",
                "lines": [],
                "pages": []
            }


    # ========================================================
    # CLEAN LINE
    # ========================================================

    def clean_line(self, line):

        line = re.sub(
            r"\s+",
            " ",
            line
        )

        return line.strip()


    # ========================================================
    # DOCUMENT SUMMARY
    # ========================================================

    def create_summary(
        self,
        document
    ):

        filename = document["filename"]

        lines = document["lines"]


        if not lines:

            return (
                "I could not extract readable text "
                "from the document."
            )


        # ----------------------------------------------------
        # Clean lines
        # ----------------------------------------------------

        cleaned_lines = []

        for line in lines:

            line = self.clean_line(
                line
            )

            if not line:

                continue


            # Ignore long verification-code lines
            lower = line.lower()

            if (
                "verification code" in lower
                and len(line) > 80
            ):

                continue


            cleaned_lines.append(
                line
            )


        # ----------------------------------------------------
        # Remove obvious duplicate lines
        # ----------------------------------------------------

        unique_lines = []

        for line in cleaned_lines:

            if line not in unique_lines:

                unique_lines.append(
                    line
                )


        # ----------------------------------------------------
        # Identify important content
        # ----------------------------------------------------

        important = []

        keywords = [
            "certificate",
            "completion",
            "simulation",
            "data",
            "analysis",
            "technology",
            "completed",
            "practical",
            "deloitte",
            "forage",
            "issued"
        ]


        for line in unique_lines:

            lower = line.lower()

            if any(
                keyword in lower
                for keyword in keywords
            ):

                if line not in important:

                    important.append(
                        line
                    )


        # ----------------------------------------------------
        # If important lines are available
        # ----------------------------------------------------

        selected = []


        for line in important:

            if line not in selected:

                selected.append(
                    line
                )

            if len(selected) >= 6:

                break


        # ----------------------------------------------------
        # Otherwise use first meaningful lines
        # ----------------------------------------------------

        if not selected:

            for line in unique_lines:

                if len(line) >= 5:

                    selected.append(
                        line
                    )

                if len(selected) >= 6:

                    break


        # ----------------------------------------------------
        # Build natural summary
        # ----------------------------------------------------

        if selected:

            joined = " | ".join(
                selected
            )


            return (
                f"Briefly, this document "
                f"({filename}) contains: "
                f"{joined}."
            )


        return (
            f"This document is titled "
            f"{filename}, but its readable "
            f"content could not be summarized."
        )


    # ========================================================
    # QUESTION ANSWERING
    # ========================================================

    def answer_question(
        self,
        question,
        document
    ):

        lines = document["lines"]

        question_lower = question.lower()


        # ----------------------------------------------------
        # Summary request detection
        # ----------------------------------------------------

        summary_patterns = [
            "brief",
            "briefly",
            "summary",
            "summarize",
            "summarise",
            "about this document",
            "about the document",
            "describe this document",
            "describe the document",
            "tell me about this document",
            "tell me about the document",
            "what is this document"
        ]


        is_summary = any(
            pattern in question_lower
            for pattern in summary_patterns
        )


        if is_summary:

            return self.create_summary(
                document
            )


        # ----------------------------------------------------
        # Keyword search
        # ----------------------------------------------------

        stop_words = {
            "what",
            "is",
            "are",
            "the",
            "a",
            "an",
            "this",
            "that",
            "document",
            "tell",
            "me",
            "about",
            "please",
            "can",
            "you",
            "explain",
            "give",
            "brief",
            "briefly",
            "how",
            "why",
            "when",
            "where",
            "who"
        }


        words = re.findall(
            r"[a-zA-Z]{3,}",
            question_lower
        )


        keywords = [
            word
            for word in words
            if word not in stop_words
        ]


        # ----------------------------------------------------
        # Find matching lines
        # ----------------------------------------------------

        matches = []


        for line in lines:

            lower = line.lower()

            score = 0


            for keyword in keywords:

                if keyword in lower:

                    score += 1


            if score > 0:

                matches.append(
                    (
                        score,
                        line
                    )
                )


        matches.sort(
            key=lambda x: x[0],
            reverse=True
        )


        # ----------------------------------------------------
        # Return matching content
        # ----------------------------------------------------

        if matches:

            answer_lines = []

            for score, line in matches[:5]:

                if line not in answer_lines:

                    answer_lines.append(
                        line
                    )


            return (
                "Based on the document: "
                + " ".join(answer_lines)
            )


        return (
            "I could not find a specific answer "
            "to that question in the document."
        )


    # ========================================================
    # MAIN GENERATE FUNCTION
    # ========================================================

    def generate(
        self,
        question,
        retrieved_pages
    ):

        document = self.extract_document()


        if not document["text"].strip():

            return (
                "I could not extract readable text "
                "from the uploaded PDF."
            )


        return self.answer_question(
            question,
            document
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