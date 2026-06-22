"""Extract MySQL source tables into the local raw Parquet layer."""
from __future__ import annotations

import logging
from pathlib import Path

import pyspark.sql.functions as F
from pyspark.sql import DataFrame, SparkSession

from src.utils.config_loader import get_jdbc_url, get_source_metadata, load_db_config
from src.utils.spark_session import create_spark_session

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "data" / "raw"
DEFAULT_TABLES = ("customers", "products", "sales", "shops")


def validate_table_name(table_name: str) -> None:
    """Restrict extraction to the approved source tables."""
    if table_name not in DEFAULT_TABLES:
        raise ValueError(f"Unsupported source table: {table_name}. Allowed: {DEFAULT_TABLES}")


def read_source_table(spark: SparkSession, table_name: str) -> DataFrame:
    """Read one approved MySQL table through JDBC."""
    validate_table_name(table_name)
    db_config = load_db_config(require_credentials=True)
    jdbc_url = get_jdbc_url(db_config)

    logger.info(
        "Reading source table %s from %s:%s/%s",
        table_name,
        db_config["host"],
        db_config["port"],
        db_config["database"],
    )

    return (
        spark.read.format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", table_name)
        .option("user", db_config["user"])
        .option("password", db_config["password"])
        .option("driver", db_config["driver"])
        .load()
    )


def add_source_lineage(df: DataFrame, table_name: str) -> DataFrame:
    """Add non-secret lineage columns to preserve source traceability."""
    validate_table_name(table_name)
    db_config = load_db_config(require_credentials=False)
    metadata = get_source_metadata(db_config, table_name)

    return (
        df.withColumn("_source_system", F.lit(metadata["source_system"]))
        .withColumn("_source_host", F.lit(metadata["source_host"]))
        .withColumn("_source_database", F.lit(metadata["source_database"]))
        .withColumn("_source_table", F.lit(metadata["source_table"]))
        .withColumn("_extracted_at", F.current_timestamp())
    )


def write_raw_table(df: DataFrame, table_name: str) -> None:
    """Write an ingested table to data/raw/<table_name> in Parquet format."""
    validate_table_name(table_name)
    output_path = RAW_ROOT / table_name
    logger.info("Writing raw table %s to %s", table_name, output_path)
    df.write.mode("overwrite").parquet(str(output_path))


def ingest_table(table_name: str, spark: SparkSession | None = None) -> int:
    """Ingest a single source table and return the number of rows written."""
    validate_table_name(table_name)
    owns_spark = spark is None
    active_spark = spark or create_spark_session(f"ingest_{table_name}")

    try:
        source_df = read_source_table(active_spark, table_name)
        raw_df = add_source_lineage(source_df, table_name)
        row_count = raw_df.count()
        write_raw_table(raw_df, table_name)
        logger.info("Ingested %s rows from %s", row_count, table_name)
        return row_count
    finally:
        if owns_spark:
            active_spark.stop()


def ingest_tables(table_names: tuple[str, ...] = DEFAULT_TABLES) -> dict[str, int]:
    """Ingest multiple source tables using one SparkSession."""
    spark = create_spark_session("ingest_source_tables")
    try:
        results: dict[str, int] = {}
        for table_name in table_names:
            results[table_name] = ingest_table(table_name, spark=spark)
        return results
    finally:
        spark.stop()


if __name__ == "__main__":
    counts = ingest_tables()
    for table, count in counts.items():
        logger.info("%s: %s rows written to raw", table, count)
