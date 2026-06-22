# ia-challenge

Proyecto final para construir un dataset analitico comercial desde una base MySQL real y generar un dashboard HTML local.

## Estado actual

Implementado hasta Parte C:

- Estructura inicial del proyecto.
- Archivos de contexto IA.
- Configuracion de conexion no secreta.
- Carga de credenciales desde `.env`.
- Ingesta reproducible de tablas fuente.

## Tablas fuente

La ingesta lee estas tablas desde la base MySQL `fake`:

- `customers`
- `products`
- `sales`
- `shops`

## Configuracion de credenciales

Copia la plantilla:

```powershell
Copy-Item .env.example .env
```

Edita `.env` con tus credenciales reales:

```text
DB_USER=tu_usuario
DB_PASSWORD=tu_password
```

`.env` esta excluido de Git y no debe subirse al repositorio.

## Ejecutar ingesta

Instala dependencias en un entorno virtual y ejecuta:

```powershell
python -m src.run_pipeline
```

Tambien puedes ejecutar tablas individuales:

```powershell
python -m src.ingest.ingest_customers
python -m src.ingest.ingest_products
python -m src.ingest.ingest_sales
python -m src.ingest.ingest_shops
```

## Salida de ingesta

Los datos crudos quedan en formato Parquet bajo:

```text
data/raw/customers/
data/raw/products/
data/raw/sales/
data/raw/shops/
```

Cada tabla ingerida incluye columnas de trazabilidad:

- `_source_system`
- `_source_host`
- `_source_database`
- `_source_table`
- `_extracted_at`

## Documentacion

- `docs/ANALISIS_MULTIHOPE.md`: analisis del proyecto base y base de datos.
- `docs/PLAN_RUTA_IA_CHALLENGE.md`: plan general del proyecto.
- `docs/ESTRUCTURA_INICIAL.txt`: estructura sugerida por IA.

## Notebook de pruebas

Para probar el flujo paso a paso puedes abrir:

`	ext
notebooks/00_pipeline_pruebas.ipynb
`



## Entorno local

Las instrucciones completas para crear el entorno virtual estan en:

```text
docs/ENTORNO_LOCAL.md
```

Resumen rapido en PowerShell:

```powershell
cd C:\Users\chris\Downloads\ia-challenge
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Nota importante para Windows: Hadoop/winutils

PySpark en Windows requiere `winutils.exe` para trabajar correctamente con archivos locales y Parquet. Las instrucciones para usar la ruta por defecto en Descargas o cambiarla a cualquier carpeta estan en:

```text
docs/ENTORNO_LOCAL.md
```

Busca la seccion "Configuracion de Hadoop/winutils en Windows".
