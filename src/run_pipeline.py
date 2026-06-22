"""Pipeline entrypoint."""
from __future__ import annotations

import logging

from src.ingest.extract_tables import ingest_tables
from src.transform.build_comercial import build_comercial_table

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger(__name__)


def run_pipeline() -> dict[str, int]:
    """Run source ingestion and build the comercial analytical dataset."""
    logger.info("Starting source ingestion")
    counts = ingest_tables()
    logger.info("Source ingestion finished: %s", counts)

    logger.info("Building comercial analytical dataset")
    comercial_count = build_comercial_table()
    logger.info("Comercial dataset finished: %s rows", comercial_count)

    return {**counts, "comercial": comercial_count}


if __name__ == "__main__":
    run_pipeline()
