"""Entrypoint to ingest the customers table."""
from src.ingest.extract_tables import ingest_table


def ingest_customers() -> int:
    return ingest_table("customers")


if __name__ == "__main__":
    ingest_customers()
