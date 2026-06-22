"""Pipeline entrypoint.

Part C currently runs source-table ingestion. Later phases will add the
commercial transform and dashboard export steps.
"""
from __future__ import annotations

import logging

from src.ingest.extract_tables import ingest_tables

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger(__name__)


def run_pipeline() -> dict[str, int]:
    """Run the implemented pipeline stages and return row counts."""
    logger.info("Starting source ingestion")
    counts = ingest_tables()
    logger.info("Source ingestion finished: %s", counts)
    return counts


if __name__ == "__main__":
    run_pipeline()
