import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()


NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


class Neo4jClient:

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

    def verify_connection(self):
        """
        Check whether Neo4j is reachable.
        """

        with self.driver.session() as session:
            result = session.run("RETURN 1 AS result")
            record = result.single()

            return record["result"] == 1

    def close(self):
        self.driver.close()


if __name__ == "__main__":

    print("Testing Neo4j connection...")

    client = Neo4jClient()

    try:
        if client.verify_connection():
            print("Neo4j connection successful!")
        else:
            print("Neo4j connection failed!")

    finally:
        client.close()