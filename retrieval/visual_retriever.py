import os
import sys
import numpy as np
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

INDEX_PATH = os.path.join(
    PROJECT_ROOT,
    "indexes",
    "page_embeddings.npy"
)

PAGES_DIR = os.path.join(
    PROJECT_ROOT,
    "data",
    "pages"
)


# ============================================================
# VISUAL RETRIEVER
# ============================================================

class VisualRetriever:

    def __init__(self):

        print("Loading visual index...")

        if not os.path.exists(INDEX_PATH):
            raise FileNotFoundError(
                f"Visual index not found: {INDEX_PATH}\n"
                "Run the visual indexer first."
            )

        self.embeddings = np.load(INDEX_PATH)

        self.image_paths = []

        if os.path.exists(PAGES_DIR):

            files = os.listdir(PAGES_DIR)

            for filename in files:

                if filename.lower().endswith(
                    (".png", ".jpg", ".jpeg", ".webp")
                ):

                    self.image_paths.append(
                        os.path.join(PAGES_DIR, filename)
                    )

        # Sort pages so page_1, page_2, page_3...
        self.image_paths.sort()

        if len(self.image_paths) != len(self.embeddings):

            raise ValueError(
                "Number of page images does not match "
                "number of embeddings.\n"
                f"Images: {len(self.image_paths)}\n"
                f"Embeddings: {len(self.embeddings)}"
            )

        print(
            f"Loaded {len(self.embeddings)} page embeddings."
        )


    # ========================================================
    # CREATE QUERY VECTOR
    # ========================================================

    def create_query_vector(self, query):

        """
        Temporary lightweight query representation.

        This is NOT the final semantic ColQwen2.5
        implementation. It is used so the complete
        multimodal RAG pipeline can be tested locally
        without downloading the 7+ GB model.
        """

        # Convert text to bytes
        query_bytes = query.encode("utf-8")

        # Create deterministic vector
        vector = np.zeros(
            self.embeddings.shape[1],
            dtype=np.float32
        )

        for i, value in enumerate(query_bytes):

            index = i % len(vector)

            vector[index] += value / 255.0

        # Normalize
        norm = np.linalg.norm(vector)

        if norm > 0:
            vector = vector / norm

        return vector


    # ========================================================
    # RETRIEVE
    # ========================================================

    def retrieve(self, query, top_k=3):

        query_vector = self.create_query_vector(query)

        # Normalize stored embeddings
        embeddings = self.embeddings.astype(
            np.float32
        )

        norms = np.linalg.norm(
            embeddings,
            axis=1,
            keepdims=True
        )

        norms[norms == 0] = 1

        normalized_embeddings = (
            embeddings / norms
        )

        # Cosine similarity
        scores = np.dot(
            normalized_embeddings,
            query_vector
        )

        # Highest scores first
        indices = np.argsort(
            scores
        )[::-1][:top_k]

        results = []

        for index in indices:

            page_number = index + 1

            results.append({
                "page_number": page_number,
                "image_path": self.image_paths[index],
                "score": float(scores[index])
            })

        return results


    # ========================================================
    # SEARCH
    # ========================================================

    def search(self, query, top_k=3):

        return self.retrieve(
            query,
            top_k=top_k
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
    print("VISUAL RETRIEVER TEST")
    print("=" * 60)

    retriever = VisualRetriever()

    try:

        query = input(
            "\nEnter your question: "
        )

        results = retriever.retrieve(
            query,
            top_k=3
        )

        print("\nRetrieved Pages:")
        print("-" * 40)

        if not results:

            print("No pages found.")

        else:

            for result in results:

                print(
                    f"\nPage       : "
                    f"{result['page_number']}"
                )

                print(
                    f"Score      : "
                    f"{result['score']:.4f}"
                )

                print(
                    f"Image      : "
                    f"{result['image_path']}"
                )

    finally:

        retriever.close()