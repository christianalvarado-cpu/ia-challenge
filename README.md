# ia-challenge

Proyecto final de datos que se conecta a una base MySQL real, ingiere tablas fuente, construye un dataset analitico unico llamado `comercial`, lo guarda en formato Parquet y genera un dashboard HTML local.

## Objetivo del proyecto

El objetivo es construir una solucion reproducible de analitica comercial que permita:

- Conectarse a una base de datos real.
- Ingerir tablas transaccionales y maestras.
- Integrarlas en un unico dataset analitico llamado `comercial`.
- Guardar el resultado en formato Parquet.
- Generar un dashboard HTML que pueda abrirse en navegador sin servidor dedicado.

## Proceso realizado

El flujo implementado es:

```text
MySQL fake -> data/raw/*.parquet -> data/analytics/comercial/*.parquet -> dashboard/index.html
```

Pasos principales:

1. Se definio la configuracion no secreta de conexion en `config/database.yml`.
2. Las credenciales se leen desde `.env`, que no se versiona.
3. Se creo una `SparkSession` centralizada en `src/utils/spark_session.py`.
4. Se ingirieron las tablas fuente con `src/ingest/extract_tables.py`.
5. Se guardaron las tablas crudas en `data/raw/<tabla>/` en formato Parquet.
6. Se construyo el dataset analitico `comercial` con `src/transform/build_comercial.py`.
7. Se guardo `comercial` en `data/analytics/comercial/` en formato Parquet.
8. Se generaron agregados para visualizacion con `src/export/dashboard_data.py`.
9. Se genero el dashboard final en `dashboard/index.html`.

## Tablas usadas

La fuente es la base MySQL `fake`, ubicada en `www.bigdataybi.com:3306`.

Tablas ingeridas:

| Tabla | Rol en el modelo |
|---|---|
| `customers` | Dimension de clientes |
| `products` | Dimension de productos |
| `sales` | Tabla de hechos de ventas |
| `shops` | Dimension de tiendas o sucursales |

## Como se construyo `comercial`

El dataset `comercial` usa `sales` como tabla principal porque cada fila representa una venta.

Joins aplicados:

| Desde `sales` | Hacia | Tipo |
|---|---|---|
| `cod_cliente` | `customers.id_cliente` | LEFT JOIN |
| `cod_producto` | `products.id_producto` | LEFT JOIN |
| `cod_sucursal` | `shops.id_sucursal` | LEFT JOIN |

Se usa `LEFT JOIN` para conservar todas las ventas aunque falte informacion en alguna dimension. Esto es importante porque existen ventas con sucursal sin correspondencia en `shops`.

Columnas utiles incluidas en `comercial`:

- `invoice_id`
- `sale_date`
- `sale_month`
- `customer_id`
- `customer_name`
- `customer_status`
- `product_id`
- `product_name`
- `product_brand`
- `shop_id`
- `shop_name`
- `shop_city`
- `quantity`
- `sale_unit_price`
- `subtotal`
- `unit_price_delta`
- `is_orphan_customer`
- `is_orphan_product`
- `is_orphan_shop`

Codigo principal:

```text
src/transform/build_comercial.py
```

Ruta del Parquet final:

```text
data/analytics/comercial/
```

Documentacion tecnica:

```text
docs/MODELO_LOGICO_COMERCIAL.md
docs/PARQUET_COMERCIAL.md
```

## Dashboard

El dashboard se encuentra en:

```text
dashboard/index.html
```

Ese es el archivo HTML final que debe abrirse en navegador.

El dashboard incluye:

- KPI del total vendido.
- Tendencia diaria de ventas de los ultimos 30 dias.
- Grafico de pastel de participacion de ventas por tienda.
- Grafico de barras de ventas por producto.
- Grafico de barras de ventas por estado de cliente.

El HTML es autocontenido: los datos agregados quedan embebidos dentro de `index.html` y los graficos usan Chart.js por CDN.

Codigo generador:

```text
src/export/dashboard_data.py
```

Regenerar dashboard:

```powershell
.\.venv\Scripts\python.exe -m src.export.dashboard_data
```

## Como ejecutar el proyecto

### 1. Crear entorno local

En Windows PowerShell:

```powershell
cd C:\Users\chris\Downloads\ia-challenge
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Mas detalle:

```text
docs/ENTORNO_LOCAL.md
```

### 2. Configurar credenciales

Crear `.env` desde la plantilla:

```powershell
Copy-Item .env.example .env
```

Editar `.env`:

```text
DB_USER=tu_usuario
DB_PASSWORD=tu_password
```

`.env` esta excluido de Git y no debe subirse.

### 3. Ejecutar pipeline completo

```powershell
.\.venv\Scripts\python.exe -m src.run_pipeline
```

Este comando ejecuta la ingesta y construye `comercial`.

### 4. Regenerar dashboard

```powershell
.\.venv\Scripts\python.exe -m src.export.dashboard_data
```

### 5. Abrir dashboard

Abrir directamente este archivo en el navegador:

```text
dashboard/index.html
```

No se requiere servidor web.

## Como revisar el proyecto sin ejecutar todo

1. Revisar el dataset final en:

```text
data/analytics/comercial/
```

2. Abrir el dashboard:

```text
dashboard/index.html
```

3. Revisar el modelo logico:

```text
docs/MODELO_LOGICO_COMERCIAL.md
```

4. Revisar el plan del dashboard:

```text
docs/DASHBOARD_PLAN.md
```

5. Revisar el notebook de pruebas:

```text
notebooks/00_pipeline_pruebas.ipynb
notebooks/01_generar_entregables.ipynb
```

## Validaciones

Ejecutar pruebas:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\ -q
```

Validar sintaxis:

```powershell
.\.venv\Scripts\python.exe -m compileall src tests
```

Validar filas de `comercial`:

```powershell
.\.venv\Scripts\python.exe -c "import pyarrow.dataset as ds; d=ds.dataset('data/analytics/comercial', format='parquet'); print(d.count_rows())"
```

## Nota importante para Windows: Hadoop/winutils

PySpark en Windows requiere `winutils.exe` para trabajar correctamente con archivos locales y Parquet. Las instrucciones para usar la ruta por defecto en Descargas o cambiarla a cualquier carpeta estan en:

```text
docs/ENTORNO_LOCAL.md
```

Busca la seccion "Configuracion de Hadoop/winutils en Windows".

## Archivos minimos del repositorio

| Requisito | Ruta | Estado |
|---|---|---|
| Dashboard HTML | `dashboard/index.html` | Incluido |
| Codigo fuente de ingesta | `src/ingest/` | Incluido |
| Codigo fuente de transformacion | `src/transform/build_comercial.py` | Incluido |
| Codigo fuente de dashboard/exportacion | `src/export/dashboard_data.py` | Incluido |
| README | `README.md` | Incluido |
| Contexto IA para agentes | `AGENTS.md` | Incluido |
| Contexto IA/OpenAI | `OPENAI.md` | Incluido |
| Configuracion no secreta | `config/` | Incluido |
| Documentacion tecnica | `docs/` | Incluido |



