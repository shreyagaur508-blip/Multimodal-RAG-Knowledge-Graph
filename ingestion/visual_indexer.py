import os
import numpy as np
from PIL import Image


def create_visual_index(
    pages_dir="data/pages",
    index_path="indexes/page_embeddings.npy"
):
    """
    Create a temporary lightweight visual index.

    This version is used to test the complete indexing pipeline
    without downloading the large ColQwen2.5 model.
    """

    print("Starting lightweight visual indexing...")

    os.makedirs(os.path.dirname(index_path), exist_ok=True)

    image_files = sorted(
        [
            os.path.join(pages_dir, file)
            for file in os.listdir(pages_dir)
            if file.lower().endswith((".png", ".jpg", ".jpeg"))
        ]
    )

    if not image_files:
        raise FileNotFoundError(
            f"No page images found in {pages_dir}"
        )

    embeddings = []

    print(f"Found {len(image_files)} page images.")

    for image_path in image_files:
        print(f"Processing: {image_path}")

        image = Image.open(image_path).convert("RGB")

        # Resize image to a small fixed size
        image = image.resize((32, 32))

        # Convert image to numpy array
        array = np.asarray(image, dtype=np.float32)

        # Normalize pixel values
        array = array / 255.0

        # Flatten image into a vector
        embedding = array.flatten()

        # Normalize embedding
        norm = np.linalg.norm(embedding)

        if norm > 0:
            embedding = embedding / norm

        embeddings.append(embedding)

    embeddings = np.array(embeddings, dtype=np.float32)

    np.save(index_path, embeddings)

    print("\nLightweight visual index created successfully!")
    print(f"Index saved to: {index_path}")
    print(f"Embedding shape: {embeddings.shape}")

    return embeddings


if __name__ == "__main__":
    create_visual_index()