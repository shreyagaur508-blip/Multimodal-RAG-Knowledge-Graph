import os
import re
import sys

from PIL import Image


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# CONFIGURATION
# ============================================================

PAGES_DIR = os.path.join(
    PROJECT_ROOT,
    "data",
    "pages"
)


# ============================================================
# LOCAL ANSWER GENERATOR
# ============================================================

class VLMGenerator:

    def __init__(self):

        print("Initializing local answer generator...")

        if not os.path.exists(PAGES_DIR):

            raise FileNotFoundError(
                f"Pages directory not found: {PAGES_DIR}"
            )

        print("Local answer generator ready!")


    # ========================================================
    # LOAD PAGE IMAGE
    # ========================================================

    def load_page(self, image_path):

        if not os.path.exists(image_path):

            raise FileNotFoundError(
                f"Page image not found: {image_path}"
            )

        return Image.open(image_path)


    # ========================================================
    # EXTRACT TEXT FROM QUERY
    # ========================================================

    def extract_keywords(self, query):

        # Remove common question words
        stop_words = {
            "what",
            "is",
            "are",
            "the",
            "a",
            "an",
            "of",
            "in",
            "on",
            "for",
            "to",
            "and",
            "or",
            "how",
            "why",
            "does",
            "do",
            "can",
            "tell",
            "me",
            "about"
        }

        words = re.findall(
            r"[a-zA-Z]+",
            query.lower()
        )

        keywords = [
            word
            for word in words
            if word not in stop_words
        ]

        return keywords


    # ========================================================
    # GENERATE ANSWER
    # ========================================================

    def generate(
        self,
        question,
        retrieved_pages
    ):

        if not retrieved_pages:

            return (
                "I could not find a relevant page "
                "in the document."
            )


        # ----------------------------------------------------
        # Collect graph entities
        # ----------------------------------------------------

        entities = []

        for page in retrieved_pages:

            if "graph_entity" in page:

                entity = page["graph_entity"]

                if entity not in entities:

                    entities.append(entity)


        # ----------------------------------------------------
        # Build answer
        # ----------------------------------------------------

        answer_parts = []


        if entities:

            answer_parts.append(
                "The document contains information related "
                "to " + ", ".join(entities) + "."
            )


        # ----------------------------------------------------
        # Page references
        # ----------------------------------------------------

        page_numbers = []

        for page in retrieved_pages:

            number = page["page_number"]

            if number not in page_numbers:

                page_numbers.append(number)


        if page_numbers:

            page_text = ", ".join(
                str(number)
                for number in page_numbers
            )

            answer_parts.append(
                f"The most relevant information was found "
                f"on page(s) {page_text}."
            )


        # ----------------------------------------------------
        # Explain retrieval
        # ----------------------------------------------------

        sources = set()

        for page in retrieved_pages:

            sources.add(page["source"])


        if "visual + graph" in sources:

            answer_parts.append(
                "The result was supported by both "
                "visual retrieval and the knowledge graph."
            )

        elif "graph" in sources:

            answer_parts.append(
                "The result was identified through the "
                "knowledge graph."
            )

        elif "visual" in sources:

            answer_parts.append(
                "The result was identified through "
                "visual page retrieval."
            )


        return " ".join(answer_parts)


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
    print("LOCAL ANSWER GENERATOR TEST")
    print("=" * 60)

    generator = VLMGenerator()

    try:

        question = input(
            "\nEnter your question: "
        )

        # Test retrieval result
        test_pages = [
            {
                "page_number": 1,
                "image_path": os.path.join(
                    PAGES_DIR,
                    "page_1.png"
                ),
                "score": 0.17,
                "source": "visual + graph",
                "graph_entity": "Machine Learning"
            }
        ]

        answer = generator.generate(
            question,
            test_pages
        )

        print("\nAnswer:")
        print("-" * 40)
        print(answer)

    finally:

        generator.close()