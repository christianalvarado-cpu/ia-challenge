"""Build the comercial analytical dataset from raw source tables."""
from __future__ import annotations

import logging
from pathlib import Path

import pyspark.sql.functions as F
from pyspark.sql import DataFrame, SparkSession

from src.utils.spark_session import create_spark_session

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "data" / "raw"
ANALYTICS_ROOT = PROJECT_ROOT / "data" / "analytics"
COMERCIAL_OUTPUT = ANALYTICS_ROOT / "comercial"
SOURCE_TABLES = ("customers", "products", "sales", "shops")


def _trim_string_columns(df: DataFrame) -> DataFrame:
    columns = []
    for column_name, dtype in df.dtypes:
        column = F.col(column_name)
        if dtype == "string":
            columns.append(F.trim(column).alias(column_name))
        else:
            columns.append(column)
    return df.select(columns)


def prepare_customers(customers_df: DataFrame) -> DataFrame:
    """Prepare customer attributes used by the analytical dataset."""
    return (
        _trim_string_columns(customers_df)
        .select(
            F.col("id_cliente").cast("int").alias("customer_pk"),
            F.col("nombre").cast("string").alias("customer_name"),
            F.lower(F.col("email").cast("string")).alias("customer_email"),
            F.col("estado").cast("string").alias("customer_status"),
        )
        .dropDuplicates(["customer_pk"])
    )


def prepare_products(products_df: DataFrame) -> DataFrame:
    """Prepare product attributes used by the analytical dataset."""
    return (
        _trim_string_columns(products_df)
        .select(
            F.col("id_producto").cast("int").alias("product_pk"),
            F.col("nombre_producto").cast("string").alias("product_name"),
            F.col("marca").cast("string").alias("product_brand"),
            F.col("precio_unitario").cast("double").alias("catalog_unit_price"),
            F.col("stock").cast("int").alias("product_stock"),
        )
        .dropDuplicates(["product_pk"])
    )


def prepare_shops(shops_df: DataFrame) -> DataFrame:
    """Prepare shop attributes used by the analytical dataset."""
    return (
        _trim_string_columns(shops_df)
        .select(
            F.col("id_sucursal").cast("int").alias("shop_pk"),
            F.col("nombre_sucursal").cast("string").alias("shop_name"),
            F.col("ciudad").cast("string").alias("shop_city"),
            F.col("latitud").cast("double").alias("shop_latitude"),
            F.col("longitud").cast("double").alias("shop_longitude"),
        )
        .dropDuplicates(["shop_pk"])
    )


def prepare_sales(sales_df: DataFrame) -> DataFrame:
    """Prepare sales facts used as the grain of the analytical dataset."""
    return sales_df.select(
        F.col("cod_factura").cast("int").alias("invoice_id"),
        F.to_date(F.col("fecha_venta")).alias("sale_date"),
        F.col("cod_cliente").cast("int").alias("customer_id"),
        F.col("cod_producto").cast("int").alias("product_id"),
        F.col("cod_sucursal").cast("int").alias("shop_id"),
        F.col("cantidad").cast("int").alias("quantity"),
        F.col("precio_unitario").cast("double").alias("sale_unit_price"),
    )


def build_comercial_dataset(
    customers_df: DataFrame,
    products_df: DataFrame,
    sales_df: DataFrame,
    shops_df: DataFrame,
) -> DataFrame:
    """Return the comercial analytical dataset as one denormalized DataFrame."""
    sales = prepare_sales(sales_df).alias("s")
    customers = prepare_customers(customers_df).alias("c")
    products = prepare_products(products_df).alias("p")
    shops = prepare_shops(shops_df).alias("sh")

    return (
        sales.join(customers, F.col("s.customer_id") == F.col("c.customer_pk"), "left")
        .join(products, F.col("s.product_id") == F.col("p.product_pk"), "left")
        .join(shops, F.col("s.shop_id") == F.col("sh.shop_pk"), "left")
        .select(
            F.col("s.invoice_id"),
            F.col("s.sale_date"),
            F.date_format(F.col("s.sale_date"), "yyyy-MM").alias("sale_month"),
            F.col("s.customer_id"),
            F.col("c.customer_name"),
            F.col("c.customer_email"),
            F.col("c.customer_status"),
            F.col("s.product_id"),
            F.col("p.product_name"),
            F.col("p.product_brand"),
            F.col("p.catalog_unit_price"),
            F.col("p.product_stock"),
            F.col("s.shop_id"),
            F.col("sh.shop_name"),
            F.col("sh.shop_city"),
            F.col("sh.shop_latitude"),
            F.col("sh.shop_longitude"),
            F.col("s.quantity"),
            F.col("s.sale_unit_price"),
            F.round(F.col("s.quantity") * F.col("s.sale_unit_price"), 2).alias("subtotal"),
            F.round(F.col("s.sale_unit_price") - F.col("p.catalog_unit_price"), 2).alias(
                "unit_price_delta"
            ),
            F.col("c.customer_pk").isNull().alias("is_orphan_customer"),
            F.col("p.product_pk").isNull().alias("is_orphan_product"),
            F.col("sh.shop_pk").isNull().alias("is_orphan_shop"),
            F.lit(",".join(SOURCE_TABLES)).alias("_source_tables"),
            F.current_timestamp().alias("_created_at"),
        )
    )


def read_raw_tables(spark: SparkSession) -> tuple[DataFrame, DataFrame, DataFrame, DataFrame]:
    """Read required raw Parquet tables from data/raw."""
    missing = [table for table in SOURCE_TABLES if not (RAW_ROOT / table).exists()]
    if missing:
        raise FileNotFoundError(f"Missing raw table folders: {missing}. Run source ingestion first.")

    customers_df = spark.read.parquet(str(RAW_ROOT / "customers"))
    products_df = spark.read.parquet(str(RAW_ROOT / "products"))
    sales_df = spark.read.parquet(str(RAW_ROOT / "sales"))
    shops_df = spark.read.parquet(str(RAW_ROOT / "shops"))
    return customers_df, products_df, sales_df, shops_df


def write_comercial_dataset(df: DataFrame, output_path: Path = COMERCIAL_OUTPUT) -> None:
    """Write the comercial dataset to Parquet."""
    logger.info("Writing comercial dataset to %s", output_path)
    df.write.mode("overwrite").parquet(str(output_path))


def build_comercial_table(spark: SparkSession | None = None) -> int:
    """Build and persist data/analytics/comercial, returning row count."""
    owns_spark = spark is None
    active_spark = spark or create_spark_session("build_comercial")

    try:
        customers_df, products_df, sales_df, shops_df = read_raw_tables(active_spark)
        comercial_df = build_comercial_dataset(customers_df, products_df, sales_df, shops_df)
        row_count = comercial_df.count()
        write_comercial_dataset(comercial_df)
        logger.info("Comercial dataset written with %s rows", row_count)
        return row_count
    finally:
        if owns_spark:
            active_spark.stop()


if __name__ == "__main__":
    build_comercial_table()
