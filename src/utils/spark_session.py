"""SparkSession factory for the ia-challenge pipeline."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import yaml
from pyspark.sql import SparkSession

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SPARK_CONFIG_PATH = PROJECT_ROOT / "config" / "spark_config.yml"
DEFAULT_WINDOWS_HADOOP_HOME = Path.home() / "Downloads" / "winutils-master" / "hadoop-3.0.0"


def _read_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _configure_local_windows_hadoop() -> str | None:
    hadoop_home = os.environ.get("HADOOP_HOME") or os.environ.get("hadoop.home.dir")
    bundled_winutils = DEFAULT_WINDOWS_HADOOP_HOME / "bin" / "winutils.exe"
    if not hadoop_home and bundled_winutils.exists():
        hadoop_home = str(DEFAULT_WINDOWS_HADOOP_HOME)

    if not hadoop_home:
        return None

    os.environ.setdefault("HADOOP_HOME", hadoop_home)
    os.environ.setdefault("hadoop.home.dir", hadoop_home)

    hadoop_bin = str(Path(hadoop_home) / "bin")
    path_entries = os.environ.get("PATH", "").split(os.pathsep)
    if hadoop_bin not in path_entries:
        os.environ["PATH"] = hadoop_bin + os.pathsep + os.environ.get("PATH", "")

    return hadoop_home


def create_spark_session(app_name: str = "IAChallenge") -> SparkSession:
    """Create a local SparkSession using config/spark_config.yml."""
    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)
    hadoop_home = _configure_local_windows_hadoop()

    config = _read_yaml(SPARK_CONFIG_PATH)
    spark_conf = config.get("spark", {})

    builder = SparkSession.builder.appName(app_name)
    builder = builder.config("spark.pyspark.python", sys.executable)
    builder = builder.config("spark.pyspark.driver.python", sys.executable)

    if hadoop_home:
        hadoop_home_java = Path(hadoop_home).as_posix()
        builder = builder.config("spark.hadoop.home.dir", hadoop_home_java)
        builder = builder.config("spark.driver.extraJavaOptions", f"-Dhadoop.home.dir={hadoop_home_java}")
        builder = builder.config("spark.executor.extraJavaOptions", f"-Dhadoop.home.dir={hadoop_home_java}")

    for key, value in spark_conf.items():
        builder = builder.config(key, str(value))

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark
