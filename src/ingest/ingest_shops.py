"""Entrypoint to ingest the shops table."""
from src.ingest.extract_tables import ingest_table


def ingest_shops() -> int:
    return ingest_table("shops")


if __name__ == "__main__":
    ingest_shops()
