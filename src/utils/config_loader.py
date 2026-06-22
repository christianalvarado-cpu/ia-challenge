"""Configuration helpers for database connectivity."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_CONFIG_PATH = PROJECT_ROOT / "config" / "database.yml"
ENV_PATH = PROJECT_ROOT / ".env"


class MissingDatabaseCredentialsError(ValueError):
    """Raised when required database credentials are not configured."""


def _read_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def load_db_config(require_credentials: bool = True) -> dict[str, Any]:
    """Load database settings from YAML and credentials from .env/environment."""
    load_dotenv(ENV_PATH)

    config = _read_yaml(DATABASE_CONFIG_PATH)
    db = config.get("database", {})

    db_config = {
        "host": db.get("host"),
        "port": db.get("port"),
        "database": db.get("name"),
        "driver": db.get("driver"),
        "options": db.get("options", {}),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    missing_settings = [key for key in ("host", "port", "database", "driver") if not db_config[key]]
    if missing_settings:
        raise ValueError(f"Missing database settings in config/database.yml: {missing_settings}")

    missing_credentials = [key for key in ("user", "password") if not db_config[key]]
    if require_credentials and missing_credentials:
        raise MissingDatabaseCredentialsError(
            "Missing DB_USER or DB_PASSWORD. Create .env from .env.example and fill both values."
        )

    return db_config


def get_jdbc_url(db_config: dict[str, Any]) -> str:
    """Build a MySQL JDBC URL from repository database configuration."""
    options = db_config.get("options") or {}
    query_string = "&".join(f"{key}={value}" for key, value in options.items())
    base_url = f"jdbc:mysql://{db_config['host']}:{db_config['port']}/{db_config['database']}"
    return f"{base_url}?{query_string}" if query_string else base_url


def get_source_metadata(db_config: dict[str, Any], table_name: str) -> dict[str, str]:
    """Return non-secret lineage metadata for an ingested source table."""
    return {
        "source_system": "mysql",
        "source_host": str(db_config["host"]),
        "source_database": str(db_config["database"]),
        "source_table": table_name,
    }
