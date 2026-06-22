"""Entrypoint to ingest the products table."""
from src.ingest.extract_tables import ingest_table


def ingest_products() -> int:
    return ingest_table("products")


if __name__ == "__main__":
    ingest_products()
