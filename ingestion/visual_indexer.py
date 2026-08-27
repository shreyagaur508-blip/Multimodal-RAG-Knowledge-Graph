import os
import numpy as np
import torch
from PIL import Image
from colpali_engine.models import ColQwen2_5, ColQwen2_5_Processor


MODEL_NAME = "vidore/colqwen2.5-v1.0"


def create_visual_index(
    pages_dir="data/pages",
    index_path="indexes/page_embeddings.npy"
):
    """
    Create visual embeddings for all PDF page images.
    """

    print("Loading ColQwen2.5 model...")

    model = ColQwen2_5.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float32,
        device_map="cpu"
    ).eval()

    processor = ColQwen2_5_Processor.from_pretrained(MODEL_NAME)

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

        batch = processor.process_images([image])

        with torch.no_grad():
            embedding = model(**batch)

        embedding = embedding.cpu().numpy()

        # Average token embeddings to create one vector per page
        embedding = embedding.mean(axis=1).squeeze()

        embeddings.append(embedding)

    embeddings = np.array(embeddings)

    np.save(index_path, embeddings)

    print("\nVisual index created successfully!")
    print(f"Index saved to: {index_path}")
    print(f"Embedding shape: {embeddings.shape}")

    return embeddings


if __name__ == "__main__":
    create_visual_index()