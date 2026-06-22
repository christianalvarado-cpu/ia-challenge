"""Entrypoint to ingest the sales table."""
from src.ingest.extract_tables import ingest_table


def ingest_sales() -> int:
    return ingest_table("sales")


if __name__ == "__main__":
    ingest_sales()
