"""Tests for source ingestion configuration helpers."""

import pytest

from src.ingest.extract_tables import DEFAULT_TABLES, validate_table_name
from src.utils.config_loader import get_jdbc_url


def test_default_source_tables_are_required_tables():
    assert DEFAULT_TABLES == ("customers", "products", "sales", "shops")


def test_jdbc_url_uses_mysql_fake_database():
    config = {
        "host": "www.bigdataybi.com",
        "port": 3306,
        "database": "fake",
        "options": {"useSSL": "false", "allowPublicKeyRetrieval": "true"},
    }

    url = get_jdbc_url(config)

    assert url.startswith("jdbc:mysql://www.bigdataybi.com:3306/fake")
    assert "useSSL=false" in url
    assert "allowPublicKeyRetrieval=true" in url


def test_validate_table_name_rejects_unapproved_table():
    with pytest.raises(ValueError, match="Unsupported source table"):
        validate_table_name("users")
