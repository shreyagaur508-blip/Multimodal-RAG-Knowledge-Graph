import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()


NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


class GraphBuilder:

    def __init__(self):

        if not NEO4J_URI:
            raise ValueError("NEO4J_URI is not set in .env")

        if not NEO4J_USERNAME:
            raise ValueError("NEO4J_USERNAME is not set in .env")

        if not NEO4J_PASSWORD:
            raise ValueError("NEO4J_PASSWORD is not set in .env")

        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )

    def create_document(self, document_name):

        query = """
        MERGE (d:Document {name: $document_name})
        RETURN d
        """

        with self.driver.session() as session:
            session.run(
                query,
                document_name=document_name
            )

    def create_page(self, document_name, page_number, image_path):

        query = """
        MATCH (d:Document {name: $document_name})

        MERGE (p:Page {
            document: $document_name,
            page_number: $page_number
        })

        SET p.image_path = $image_path

        MERGE (d)-[:HAS_PAGE]->(p)

        RETURN p
        """

        with self.driver.session() as session:
            session.run(
                query,
                document_name=document_name,
                page_number=page_number,
                image_path=image_path
            )

    def create_entity(
        self,
        document_name,
        page_number,
        entity_name,
        entity_type="Concept"
    ):

        query = """
        MATCH (p:Page {
            document: $document_name,
            page_number: $page_number
        })

        MERGE (e:Entity {
            name: $entity_name
        })

        SET e.type = $entity_type

        MERGE (p)-[:CONTAINS]->(e)

        RETURN e
        """

        with self.driver.session() as session:
            session.run(
                query,
                document_name=document_name,
                page_number=page_number,
                entity_name=entity_name,
                entity_type=entity_type
            )

    def close(self):

        self.driver.close()


if __name__ == "__main__":

    print("Building Knowledge Graph...")

    builder = GraphBuilder()

    try:

        # --------------------------------------------------
        # DOCUMENT
        # --------------------------------------------------

        document_name = "test.pdf"

        print(f"\nCreating document: {document_name}")

        builder.create_document(document_name)

        # --------------------------------------------------
        # PAGES
        # --------------------------------------------------

        pages_directory = "data/pages"

        page_files = sorted(
            [
                file_name
                for file_name in os.listdir(pages_directory)
                if file_name.lower().endswith(".png")
            ]
        )

        print(f"Found {len(page_files)} page images.")

        for index, file_name in enumerate(page_files, start=1):

            image_path = os.path.join(
                pages_directory,
                file_name
            )

            print(
                f"Creating Page {index}: {image_path}"
            )

            builder.create_page(
                document_name,
                index,
                image_path
            )

        # --------------------------------------------------
        # TEST ENTITIES
        # --------------------------------------------------

        print("\nAdding entities to Knowledge Graph...")

        # Page 1
        builder.create_entity(
            document_name,
            1,
            "Machine Learning",
            "Concept"
        )

        builder.create_entity(
            document_name,
            1,
            "Artificial Intelligence",
            "Concept"
        )

        # Page 2
        builder.create_entity(
            document_name,
            2,
            "Supervised Learning",
            "Technique"
        )

        builder.create_entity(
            document_name,
            2,
            "Unsupervised Learning",
            "Technique"
        )

        # Page 3
        builder.create_entity(
            document_name,
            3,
            "Neural Networks",
            "Technique"
        )

        builder.create_entity(
            document_name,
            3,
            "Deep Learning",
            "Concept"
        )

        print("\nEntities added successfully!")

        print("\nKnowledge Graph created successfully!")

    finally:

        builder.close()