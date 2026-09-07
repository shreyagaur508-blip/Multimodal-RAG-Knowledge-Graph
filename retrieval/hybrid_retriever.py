import os
import sys

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, PROJECT_ROOT)

from retrieval.visual_retriever import VisualRetriever
from retrieval.graph_retriever import GraphRetriever


class HybridRetriever:

    def __init__(self):
        self.visual_retriever = VisualRetriever()
        self.graph_retriever = GraphRetriever()

    def retrieve(self, query, top_k=3):

        print("\nRunning visual retrieval...")

        visual_results = self.visual_retriever.retrieve(
            query,
            top_k=top_k
        )

        print("Running graph retrieval...")

        graph_results = self.graph_retriever.search_entities(query)

        results = []

        # Add visual results
        for result in visual_results:

            results.append({
                "page_number": result["page_number"],
                "image_path": result["image_path"],
                "score": result["score"],
                "source": "visual"
            })

        # Add graph results
        for result in graph_results:

            page_number = result["page_number"]
            image_path = result["image_path"]

            existing = None

            for item in results:
                if item["page_number"] == page_number:
                    existing = item
                    break

            if existing:

                existing["source"] = "visual + graph"

                existing["graph_entity"] = result["entity"]

                # Small boost for graph match
                existing["score"] += 0.1

            else:

                results.append({
                    "page_number": page_number,
                    "image_path": image_path,
                    "score": 0.1,
                    "source": "graph",
                    "graph_entity": result["entity"]
                })

        # Sort by score
        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return results[:top_k]

    def close(self):

        if hasattr(self.visual_retriever, "close"):
            self.visual_retriever.close()

        if hasattr(self.graph_retriever, "close"):
            self.graph_retriever.close()


if __name__ == "__main__":

    print("=" * 60)
    print("HYBRID RETRIEVER")
    print("=" * 60)

    retriever = HybridRetriever()

    try:

        query = input("\nEnter your question: ")

        results = retriever.retrieve(
            query,
            top_k=3
        )

        print("\nHybrid Retrieval Results:")
        print("-" * 40)

        if not results:

            print("No relevant pages found.")

        else:

            for result in results:

                print(f"\nPage       : {result['page_number']}")
                print(f"Score      : {result['score']:.4f}")
                print(f"Source     : {result['source']}")
                print(f"Image      : {result['image_path']}")

                if "graph_entity" in result:
                    print(
                        f"Entity     : {result['graph_entity']}"
                    )

    finally:

        retriever.close()