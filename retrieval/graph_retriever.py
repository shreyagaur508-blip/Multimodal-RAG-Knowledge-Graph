import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()


NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


class GraphRetriever:

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

    def search_entities(self, search_term):

        cypher_query = """
        MATCH (p:Page)-[:CONTAINS]->(e:Entity)

        WHERE toLower(e.name) CONTAINS toLower($search_term)

        RETURN
            e.name AS entity,
            e.type AS entity_type,
            p.page_number AS page_number,
            p.image_path AS image_path

        ORDER BY p.page_number
        """

        with self.driver.session() as session:

            result = session.run(
                cypher_query,
                search_term=search_term
            )

            results = []

            for record in result:

                results.append({
                    "entity": record["entity"],
                    "entity_type": record["entity_type"],
                    "page_number": record["page_number"],
                    "image_path": record["image_path"]
                })

            return results

    def close(self):

        self.driver.close()


if __name__ == "__main__":

    print("Testing Graph Retriever...")

    retriever = GraphRetriever()

    try:

        search_term = input("\nEnter an entity to search: ")

        results = retriever.search_entities(search_term)

        print("\nGraph Search Results:")
        print("--------------------")

        if not results:

            print("No matching entities found.")

        else:

            for result in results:

                print(
                    f"\nEntity      : {result['entity']}"
                )

                print(
                    f"Type        : {result['entity_type']}"
                )

                print(
                    f"Page        : {result['page_number']}"
                )

                print(
                    f"Image       : {result['image_path']}"
                )

    finally:

        retriever.close()