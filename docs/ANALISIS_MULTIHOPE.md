# Analisis del proyecto base `multihope`

Origen analizado: `C:\Users\chris\Downloads\multihope`

Fecha de analisis: 2026-06-21

## 1. Resumen ejecutivo

`multihope` es un proyecto de datos con arquitectura Medallion implementada en Python y PySpark. El flujo principal es:

```text
MySQL fake -> RAW/BRONZE -> SILVER -> GOLD
```

Para este nuevo proyecto conviene reutilizar la misma estructura de carpetas, la misma configuracion JDBC/Spark y el mismo patron de modulos por capa:

- `config/`: configuracion de base de datos y Spark.
- `src/utils/`: utilidades compartidas.
- `src/raw_to_bronze/`: ingesta desde MySQL hacia Parquet Bronze.
- `src/bronze_to_silver/`: limpieza, tipado y reglas de calidad.
- `src/silver_to_gold/`: tablas analiticas listas para consumo.
- `catalog/comercial/`: catalogo funcional y tecnico de la base.
- `dags/`: orquestacion Airflow.
- `tests/`: pruebas unitarias con datos en memoria.
- `notebooks/`: ejecucion exploratoria por etapas.
- `data/`: salidas generadas, no debe versionarse.

La base de datos que se debe mantener es MySQL `fake`, alojada en `www.bigdataybi.com:3306`.

## 2. Base de datos

### Conexion

Archivo base: `config/database.yml`

```yaml
database:
  host: www.bigdataybi.com
  port: 3306
  name: fake
  driver: com.mysql.cj.jdbc.Driver
  options:
    useSSL: "false"
    allowPublicKeyRetrieval: "true"
```

Credenciales:

- Se leen desde `.env`.
- Variables requeridas: `DB_USER`, `DB_PASSWORD`.
- `.env` no debe versionarse ni mostrarse en documentacion.
- `.env.example` debe mantenerse como plantilla sin secretos.

### Tablas reales confirmadas

Consulta de solo lectura contra `information_schema` confirmo:

| Tabla | Filas aproximadas | Tipo | Motor |
|---|---:|---|---|
| `customers` | 10 | BASE TABLE | InnoDB |
| `products` | 5 | BASE TABLE | InnoDB |
| `sales` | 100 | BASE TABLE | InnoDB |
| `shops` | 3 | BASE TABLE | InnoDB |

### Esquema de tablas

#### `customers`

| Columna | Tipo MySQL | Nulo | Clave |
|---|---|---|---|
| `id_cliente` | `int` | NO | PRIMARY KEY |
| `identificacion` | `varchar(45)` | YES |  |
| `nombre` | `longtext` | YES |  |
| `email` | `longtext` | YES |  |
| `telefono` | `longtext` | YES |  |
| `direccion` | `longtext` | YES |  |
| `estado` | `longtext` | YES |  |
| `_loadtime` | `timestamp` | YES |  |

Uso recomendado:

- Dimension de clientes.
- Clave fisica real: `id_cliente`.
- En Silver el proyecto base renombra `id_cliente` a `customer_id`.
- `email` se normaliza a minusculas.

#### `products`

| Columna | Tipo MySQL | Nulo | Clave |
|---|---|---|---|
| `id_producto` | `int` | YES | clave logica |
| `nombre_producto` | `longtext` | YES |  |
| `descripcion` | `longtext` | YES |  |
| `precio_unitario` | `float` | YES |  |
| `stock` | `int` | YES |  |
| `marca` | `longtext` | YES |  |
| `_loadtime` | `timestamp` | YES |  |

Uso recomendado:

- Dimension de productos.
- `id_producto` no tiene PK formal en DDL, pero es unico y sin nulos en los datos actuales.
- Validar `precio_unitario >= 0` y `stock >= 0`.

#### `sales`

| Columna | Tipo MySQL | Nulo | Clave |
|---|---|---|---|
| `cod_factura` | `int` | YES | clave logica |
| `cod_sucursal` | `int` | YES | FK logica a `shops.id_sucursal` |
| `cod_cliente` | `int` | YES | FK logica a `customers.id_cliente` |
| `cod_producto` | `int` | YES | FK logica a `products.id_producto` |
| `fecha_venta` | `date` | YES |  |
| `cantidad` | `int` | YES |  |
| `precio_unitario` | `double` | YES |  |
| `_loadtime` | `timestamp` | YES |  |

Uso recomendado:

- Tabla de hechos transaccional.
- `cod_factura` es unico y sin nulos en los datos actuales, pero no tiene PK formal.
- Validar `cantidad > 0`, `precio_unitario >= 0` y castear `fecha_venta` como fecha.
- Subtotal de linea: `cantidad * precio_unitario`.

#### `shops`

| Columna | Tipo MySQL | Nulo | Clave |
|---|---|---|---|
| `id_sucursal` | `int` | YES | clave logica |
| `nombre_sucursal` | `longtext` | YES |  |
| `ciudad` | `longtext` | YES |  |
| `latitud` | `double` | YES |  |
| `longitud` | `double` | YES |  |
| `_loadtime` | `timestamp` | YES |  |

Uso recomendado:

- Dimension de sucursales.
- `id_sucursal` no tiene PK formal en DDL, pero es unico y sin nulos en los datos actuales.
- Validar latitud entre `-90` y `90`, longitud entre `-180` y `180`.

### Restricciones y relaciones

Restricciones fisicas confirmadas:

| Tabla | Columna | Restriccion |
|---|---|---|
| `customers` | `id_cliente` | PRIMARY KEY |

Relaciones logicas validadas por datos:

| Relacion | Coincidencias | Huerfanos | Nota |
|---|---:|---:|---|
| `sales.cod_cliente -> customers.id_cliente` | 100 | 0 | fuerte |
| `sales.cod_producto -> products.id_producto` | 100 | 0 | fuerte |
| `sales.cod_sucursal -> shops.id_sucursal` | 80 | 20 | hay ventas con sucursal sin match |

Importante: no hay foreign keys formales declaradas. Las relaciones con `products`, `sales` y `shops` deben tratarse como relaciones logicas, no garantizadas por la base.

## 3. Arquitectura del proyecto base

### Estructura recomendada para replicar

```text
ProyectoCursoIA/
|-- config/
|   |-- database.yml
|   `-- spark_config.yml
|-- catalog/
|   `-- comercial/
|       |-- catalog.md
|       `-- catalog.json
|-- dags/
|   `-- multihope_pipeline_dag.py
|-- notebooks/
|   |-- 00_precheck.ipynb
|   |-- 01_raw_to_bronze_*.ipynb
|   |-- 02_bronze_to_silver_*.ipynb
|   |-- 03_silver_to_gold_*.ipynb
|   `-- 04_silver_to_gold_*.ipynb
|-- src/
|   |-- __init__.py
|   |-- utils/
|   |   |-- __init__.py
|   |   |-- config_loader.py
|   |   `-- spark_session.py
|   |-- raw_to_bronze/
|   |   |-- __init__.py
|   |   |-- table_ingestion.py
|   |   |-- all_tables_ingestion.py
|   |   |-- customers_ingestion.py
|   |   |-- products_ingestion.py
|   |   |-- sales_ingestion.py
|   |   `-- shops_ingestion.py
|   |-- bronze_to_silver/
|   |   |-- __init__.py
|   |   |-- table_transform.py
|   |   |-- customers_transform.py
|   |   |-- products_transform.py
|   |   |-- sales_transform.py
|   |   |-- shops_transform.py
|   |   `-- products_sales_shops_transform.py
|   `-- silver_to_gold/
|       |-- __init__.py
|       |-- customers_aggregation.py
|       `-- commercial_sales.py
|-- tests/
|-- data/
|   |-- bronze/
|   |-- silver/
|   |-- gold/
|   `-- quarantine/
|-- .env.example
|-- .gitignore
|-- requirements.txt
`-- README.md
```

## 4. Archivos importantes y uso

### Configuracion

| Archivo | Importancia | Uso |
|---|---|---|
| `config/database.yml` | Alta | Fuente oficial de host, puerto, nombre de DB, driver JDBC y opciones MySQL. |
| `config/spark_config.yml` | Alta | Configura Spark local, memoria, particiones y paquete JDBC `mysql:mysql-connector-java:8.0.33`. |
| `.env.example` | Alta | Plantilla de credenciales. Debe contener solo nombres de variables. |
| `requirements.txt` | Alta | Dependencias principales: PySpark, dotenv, PyYAML, pytest, pandas, pyarrow, ipykernel, DQX. |

### Utilidades compartidas

| Archivo | Importancia | Uso |
|---|---|---|
| `src/utils/config_loader.py` | Alta | Carga `.env` y `config/database.yml`; construye el JDBC URL. |
| `src/utils/spark_session.py` | Alta | Crea la `SparkSession` con `spark_config.yml` y ajustes para Windows/Hadoop. |

### RAW -> BRONZE

| Archivo | Importancia | Uso |
|---|---|---|
| `src/raw_to_bronze/table_ingestion.py` | Alta | Helper central. Lee tablas MySQL por JDBC y escribe Parquet en `data/bronze/<tabla>`. |
| `src/raw_to_bronze/all_tables_ingestion.py` | Media | Ejecuta ingesta de todas las tablas configuradas. |
| `src/raw_to_bronze/customers_ingestion.py` | Media | Wrapper para `customers`. |
| `src/raw_to_bronze/products_ingestion.py` | Media | Wrapper para `products`. |
| `src/raw_to_bronze/sales_ingestion.py` | Media | Wrapper para `sales`. |
| `src/raw_to_bronze/shops_ingestion.py` | Media | Wrapper para `shops`. |

Patron clave:

```python
DEFAULT_TABLES = ("customers", "products", "sales", "shops")
```

La lectura JDBC usa:

```python
spark.read.format("jdbc")
  .option("url", jdbc_url)
  .option("dbtable", table_name)
  .option("user", db_config["user"])
  .option("password", db_config["password"])
  .option("driver", db_config["driver"])
  .load()
```

### BRONZE -> SILVER

| Archivo | Importancia | Uso |
|---|---|---|
| `src/bronze_to_silver/customers_transform.py` | Alta | Transformacion especial para clientes con DQX. Renombra `id_cliente` a `customer_id`, limpia strings, normaliza email y separa cuarentena. |
| `src/bronze_to_silver/table_transform.py` | Alta | Transformacion reusable para `products`, `sales` y `shops`. Define reglas por tabla. |
| `src/bronze_to_silver/products_transform.py` | Media | Wrapper para `products`. |
| `src/bronze_to_silver/sales_transform.py` | Media | Wrapper para `sales`. |
| `src/bronze_to_silver/shops_transform.py` | Media | Wrapper para `shops`. |
| `src/bronze_to_silver/products_sales_shops_transform.py` | Media | Ejecuta las tres transformaciones en bloque. |

Reglas principales:

- Limpiar strings con `trim`.
- Convertir strings vacios a `NULL` en `products`, `sales`, `shops`.
- Quitar duplicados.
- Validar columnas requeridas.
- Agregar `_ingested_at` y `_source_layer`.
- Separar registros validos de cuarentena.

### SILVER -> GOLD

| Archivo | Importancia | Uso |
|---|---|---|
| `src/silver_to_gold/customers_aggregation.py` | Media | Agregado de clientes por `estado`. |
| `src/silver_to_gold/commercial_sales.py` | Alta | Tabla gold denormalizada de ventas comerciales. Une `sales`, `customers`, `products` y `shops`. |

`commercial_sales.py` usa LEFT JOIN para mantener ventas con sucursal huerfana. Esto es correcto porque la base tiene 20 ventas cuyo `cod_sucursal` no existe en `shops`.

Columnas analiticas importantes en Gold:

- `invoice_id`
- `sale_date`
- `sale_month`
- `customer_id`, `customer_name`, `customer_status`
- `product_id`, `product_name`, `product_brand`
- `shop_id`, `shop_name`, `shop_city`
- `quantity`
- `sale_unit_price`
- `subtotal`
- `unit_price_delta`
- `is_orphan_customer`
- `is_orphan_product`
- `is_orphan_shop`

### Catalogo

| Archivo | Importancia | Uso |
|---|---|---|
| `catalog/comercial/catalog.md` | Alta | Documentacion legible de tablas, columnas, relaciones, consultas y glosario. |
| `catalog/comercial/catalog.json` | Alta | Version estructurada para IA o generacion de SQL. |
| `MODELO_DATOS_FAKE.md` | Alta | Resumen del modelo ER y advertencias de integridad. |
| `MODELO_DATOS_FAKE.drawio` | Media | Diagrama editable del modelo de datos. |

### Orquestacion

| Archivo | Importancia | Uso |
|---|---|---|
| `dags/multihope_pipeline_dag.py` | Alta | DAG Airflow con grupos `raw_to_bronze`, `bronze_to_silver`, `silver_to_gold` y validacion final de Gold. |
| `AIRFLOW_DAG_GRAFO.md` | Media | Documentacion visual/logica del DAG. |
| `REVISION_TECNICA_AIRFLOW_DAG.md` | Media | Riesgos y mejoras detectadas para Airflow. |

### Tests

| Archivo | Importancia | Uso |
|---|---|---|
| `tests/test_raw_to_bronze.py` | Alta | Valida JDBC URL, tablas default, escritura Bronze y wrappers. |
| `tests/test_products_sales_shops_to_silver.py` | Alta | Valida reglas Silver para productos, ventas y sucursales. |
| `tests/test_commercial_sales_gold.py` | Alta | Valida joins, subtotal, delta de precio y ventas con sucursal huerfana. |
| `tests/test_bronze_to_silver.py` | Media | Tests basicos antiguos de clientes. |
| `tests/test_silver_to_gold.py` | Media | Tests basicos antiguos de agregacion. |
| `tests/conftest.py` | Media | Configura Python para PySpark en tests. |

## 5. Dependencias importantes

Archivo base: `requirements.txt`

```text
pyspark==3.5.1
python-dotenv==1.0.1
PyYAML==6.0.3
pytest==8.1.1
pytest-mock==3.14.0
pandas==2.2.2
pyarrow==16.0.0
ipykernel
databricks-labs-dqx==0.13.0
```

Recomendacion operativa:

- En Windows usar Python 3.11.
- Java debe estar instalado para PySpark.
- Para Windows local, el proyecto base contempla `winutils` en `Downloads/winutils-master/hadoop-3.0.0`.

## 6. Comandos base

Crear entorno:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Configurar credenciales:

```powershell
Copy-Item .env.example .env
```

Editar `.env` manualmente:

```text
DB_USER=...
DB_PASSWORD=...
```

Ejecutar ingesta completa:

```powershell
.\.venv\Scripts\python.exe -m src.raw_to_bronze.all_tables_ingestion
```

Ejecutar por etapas:

```powershell
.\.venv\Scripts\python.exe -m src.raw_to_bronze.customers_ingestion
.\.venv\Scripts\python.exe -m src.bronze_to_silver.customers_transform
.\.venv\Scripts\python.exe -m src.silver_to_gold.customers_aggregation
.\.venv\Scripts\python.exe -m src.silver_to_gold.commercial_sales
```

Ejecutar tests:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

## 7. Puntos de cuidado para el nuevo proyecto

1. No copiar `.env` desde `multihope`; crear uno nuevo desde `.env.example`.
2. Mantener `config/database.yml` y `config/spark_config.yml` como fuentes oficiales de configuracion.
3. Mantener el patron de wrappers por tabla, aunque exista un helper generico.
4. Tratar `products.id_producto`, `shops.id_sucursal` y `sales.cod_factura` como claves logicas, no como constraints reales.
5. En Gold, usar LEFT JOIN cuando se necesite conservar ventas con sucursal no encontrada.
6. Documentar cualquier cambio de esquema en `catalog/comercial/catalog.md` y `catalog/comercial/catalog.json`.
7. Si se agregan tablas o nuevas capas, actualizar en conjunto: `src`, `tests`, `catalog`, `notebooks` y `dags`.
8. Evitar que `data/`, `.venv/`, `.pytest_cache/` y salidas temporales entren a Git.

## 8. Archivos que conviene copiar primero

Orden recomendado:

1. `requirements.txt`
2. `.gitignore`
3. `.env.example`
4. `config/database.yml`
5. `config/spark_config.yml`
6. `src/utils/config_loader.py`
7. `src/utils/spark_session.py`
8. `src/raw_to_bronze/`
9. `src/bronze_to_silver/`
10. `src/silver_to_gold/`
11. `catalog/comercial/`
12. `tests/`
13. `dags/multihope_pipeline_dag.py`
14. `notebooks/`, si se necesita trabajo exploratorio o demostracion paso a paso.

## 9. Conclusion

La base util del proyecto es solida para reutilizarse: MySQL remoto, PySpark local, capas Medallion en Parquet, catalogo comercial y pruebas unitarias. La estructura que debe preservarse es la separacion por capas bajo `src/`, configuracion en `config/`, catalogo en `catalog/comercial/` y pruebas en `tests/`.

El mayor punto funcional a recordar es la integridad parcial de `sales.cod_sucursal`: 20 de 100 ventas no tienen match en `shops`. Por eso, para analitica comercial, `commercial_sales.py` conserva esas filas con LEFT JOIN y marca `is_orphan_shop`.
