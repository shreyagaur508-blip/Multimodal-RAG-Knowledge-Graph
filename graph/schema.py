class GraphSchema:

    DOCUMENT = "Document"
    PAGE = "Page"
    ENTITY = "Entity"

    HAS_PAGE = "HAS_PAGE"
    CONTAINS = "CONTAINS"
    RELATED_TO = "RELATED_TO"


if __name__ == "__main__":
    print("Knowledge Graph schema loaded successfully!")

    print("\nNodes:")
    print(f"- {GraphSchema.DOCUMENT}")
    print(f"- {GraphSchema.PAGE}")
    print(f"- {GraphSchema.ENTITY}")

    print("\nRelationships:")
    print(f"- {GraphSchema.HAS_PAGE}")
    print(f"- {GraphSchema.CONTAINS}")
    print(f"- {GraphSchema.RELATED_TO}")