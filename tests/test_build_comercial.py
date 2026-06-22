"""Tests for the comercial analytical dataset."""

import pytest

from src.transform.build_comercial import build_comercial_dataset
from src.utils.spark_session import create_spark_session


@pytest.fixture(scope="session")
def spark():
    session = create_spark_session("test_build_comercial")
    yield session
    session.stop()


def test_build_comercial_dataset_keeps_sales_and_calculates_metrics(spark):
    customers = spark.createDataFrame(
        [(1, " Alice ", "Alice@Example.COM", "activo")],
        ["id_cliente", "nombre", "email", "estado"],
    )
    products = spark.createDataFrame(
        [(10, " Detergente ", "desc", 8.0, 20, " Marca A ")],
        ["id_producto", "nombre_producto", "descripcion", "precio_unitario", "stock", "marca"],
    )
    sales = spark.createDataFrame(
        [(100, 1, 1, 10, "2025-06-01", 3, 7.5)],
        [
            "cod_factura",
            "cod_sucursal",
            "cod_cliente",
            "cod_producto",
            "fecha_venta",
            "cantidad",
            "precio_unitario",
        ],
    )
    shops = spark.createDataFrame(
        [(1, " Sucursal Quito Sur ", " Quito ", -0.25, -78.52)],
        ["id_sucursal", "nombre_sucursal", "ciudad", "latitud", "longitud"],
    )

    row = build_comercial_dataset(customers, products, sales, shops).collect()[0]

    assert row["invoice_id"] == 100
    assert row["sale_month"] == "2025-06"
    assert row["customer_name"] == "Alice"
    assert row["customer_email"] == "alice@example.com"
    assert row["product_name"] == "Detergente"
    assert row["product_brand"] == "Marca A"
    assert row["shop_name"] == "Sucursal Quito Sur"
    assert row["shop_city"] == "Quito"
    assert row["subtotal"] == 22.5
    assert row["unit_price_delta"] == -0.5
    assert row["is_orphan_customer"] is False
    assert row["is_orphan_product"] is False
    assert row["is_orphan_shop"] is False


def test_build_comercial_dataset_preserves_orphan_shop_sale(spark):
    customers = spark.createDataFrame(
        [(1, "Alice", "alice@example.com", "activo")],
        ["id_cliente", "nombre", "email", "estado"],
    )
    products = spark.createDataFrame(
        [(10, "Detergente", "desc", 8.0, 20, "Marca A")],
        ["id_producto", "nombre_producto", "descripcion", "precio_unitario", "stock", "marca"],
    )
    sales = spark.createDataFrame(
        [(101, 99, 1, 10, "2025-06-01", 1, 9.0)],
        [
            "cod_factura",
            "cod_sucursal",
            "cod_cliente",
            "cod_producto",
            "fecha_venta",
            "cantidad",
            "precio_unitario",
        ],
    )
    shops = spark.createDataFrame(
        [(1, "Sucursal Quito Sur", "Quito", -0.25, -78.52)],
        ["id_sucursal", "nombre_sucursal", "ciudad", "latitud", "longitud"],
    )

    row = build_comercial_dataset(customers, products, sales, shops).collect()[0]

    assert row["invoice_id"] == 101
    assert row["shop_id"] == 99
    assert row["shop_name"] is None
    assert row["is_orphan_shop"] is True
