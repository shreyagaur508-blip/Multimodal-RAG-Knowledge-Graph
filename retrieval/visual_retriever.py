import os
import numpy as np
from PIL import Image


INDEX_PATH = "indexes/page_embeddings.npy"
PAGES_DIR = "data/pages"


def create_query_embedding(query):
    """
    Create a lightweight query representation.

    This is a temporary retrieval implementation used
    while the real ColQwen2.5 model is not loaded.
    """

    # Convert text into a deterministic numeric representation
    vector = np.zeros(3072, dtype=np.float32)

    encoded = query.lower().encode("utf-8")

    for i, value in enumerate(encoded):
        vector[i % 3072] += value

    # Normalize
    norm = np.linalg.norm(vector)

    if norm > 0:
        vector = vector / norm

    return vector


def retrieve_pages(query, top_k=3):
    """
    Retrieve the most relevant PDF pages for a query.
    """

    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(
            f"Visual index not found: {INDEX_PATH}"
        )

    embeddings = np.load(INDEX_PATH)

    query_embedding = create_query_embedding(query)

    # Calculate cosine similarity
    similarities = embeddings @ query_embedding

    # Get highest scoring pages
    ranked_indices = np.argsort(similarities)[::-1]

    results = []

    for index in ranked_indices[:top_k]:

        page_number = int(index) + 1

        page_path = os.path.join(
            PAGES_DIR,
            f"page_{page_number}.png"
        )

        results.append(
            {
                "page": page_number,
                "score": float(similarities[index]),
                "image": page_path,
            }
        )

    return results


if __name__ == "__main__":

    query = input("Enter your question: ")

    results = retrieve_pages(query)

    print("\nRetrieved pages:\n")

    for result in results:
        print(
            f"Page {result['page']} "
            f"| Score: {result['score']:.4f} "
            f"| {result['image']}"
        )