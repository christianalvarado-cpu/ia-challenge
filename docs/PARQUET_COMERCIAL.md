# Parte E - Dataset comercial en Parquet

## Resultado requerido

El resultado analitico final del proyecto se llama `comercial` y se almacena en formato Parquet.

## Ruta oficial

```text
data/analytics/comercial/
```

Spark escribe Parquet como un directorio de dataset, no como un unico archivo fijo. Por eso la ruta contiene uno o mas archivos con extension `.parquet`.

Ejemplo actual:

```text
data/analytics/comercial/part-00000-*.snappy.parquet
```

Los archivos auxiliares de Spark/Hadoop como `_SUCCESS` y `*.crc` no forman parte del entregable principal y estan ignorados por Git.

## Codigo que genera el Parquet

Archivo principal:

```text
src/transform/build_comercial.py
```

Constante de salida:

```python
COMERCIAL_OUTPUT = ANALYTICS_ROOT / "comercial"
```

Funcion de escritura:

```python
def write_comercial_dataset(df: DataFrame, output_path: Path = COMERCIAL_OUTPUT) -> None:
    df.write.mode("overwrite").parquet(str(output_path))
```

## Como regenerar el dataset

Desde la raiz del proyecto:

```powershell
.\.venv\Scripts\python.exe -m src.transform.build_comercial
```

Si tambien quieres ejecutar ingesta y transformacion en un solo flujo:

```powershell
.\.venv\Scripts\python.exe -m src.run_pipeline
```

## Como validar el Parquet

Con PyArrow:

```powershell
.\.venv\Scripts\python.exe -c "import pyarrow.dataset as ds; d=ds.dataset('data/analytics/comercial', format='parquet'); print(d.count_rows()); print(d.schema.names)"
```

Resultado esperado actual:

```text
100
```

Columnas principales:

- `invoice_id`
- `sale_date`
- `sale_month`
- `customer_id`
- `customer_name`
- `product_id`
- `product_name`
- `shop_id`
- `shop_name`
- `quantity`
- `sale_unit_price`
- `subtotal`
- `is_orphan_shop`

## Nota de versionamiento

El proyecto conserva el Parquet final `comercial` como evidencia del entregable. Los datos crudos de `data/raw/` se consideran generados y no se suben al repositorio.
