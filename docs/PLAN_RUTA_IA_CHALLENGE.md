# Plan de ruta - Proyecto final `ia-challenge`

## 1. Objetivo

Desarrollar un proyecto final completo que:

- Se conecte a la base de datos real MySQL `fake`.
- Ingiera las tablas `customers`, `products`, `sales` y `shops`.
- Construya un unico dataset analitico llamado `comercial`.
- Almacene `comercial` en formato Parquet.
- Genere un dashboard HTML que abra directamente en navegador, sin servidor dedicado.
- Publique toda la solucion en un repositorio publico de GitHub llamado exactamente `ia-challenge`.

El proyecto tomara como base tecnica el analisis documentado en `docs/ANALISIS_MULTIHOPE.md`.

## 2. Entregables finales

El repositorio final debe contener como minimo:

| Entregable | Ruta sugerida | Descripcion |
|---|---|---|
| Codigo de conexion | `src/config.py` o `src/utils/config_loader.py` | Carga configuracion y credenciales sin hardcodear password. |
| Codigo de ingesta | `src/ingest/` | Extrae `customers`, `products`, `sales`, `shops` desde MySQL. |
| Codigo de transformacion | `src/transform/build_comercial.py` | Construye el dataset analitico `comercial`. |
| Dataset Parquet | `data/analytics/comercial/` | Salida analitica final en formato Parquet. |
| Dashboard HTML | `dashboard/index.html` | Pagina auto-contenida o con librerias CDN para visualizar resultados. |
| Datos para dashboard | `dashboard/assets/comercial_summary.json` | Agregados listos para graficos en HTML. |
| README | `README.md` | Explica objetivo, proceso, ejecucion y dashboard. |
| Contexto IA | `AGENTS.md`, `OPENAI.md` o `CLAUDE.md` | Instrucciones y decisiones usadas con IA. |
| Plantilla de variables | `.env.example` | Variables requeridas sin secretos. |
| Dependencias | `requirements.txt` | Librerias Python necesarias. |
| Git ignore | `.gitignore` | Evita subir `.env`, `.venv`, caches y datos temporales sensibles. |

## 3. Estructura de carpetas sugerida

```text
ia-challenge/
|-- AGENTS.md
|-- OPENAI.md
|-- README.md
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- config/
|   |-- database.yml
|   `-- spark_config.yml
|-- docs/
|   |-- ANALISIS_MULTIHOPE.md
|   |-- PLAN_RUTA_IA_CHALLENGE.md
|   |-- MODELO_LOGICO_COMERCIAL.md
|   `-- DASHBOARD_PLAN.md
|-- src/
|   |-- __init__.py
|   |-- utils/
|   |   |-- __init__.py
|   |   |-- config_loader.py
|   |   `-- spark_session.py
|   |-- ingest/
|   |   |-- __init__.py
|   |   |-- extract_tables.py
|   |   |-- ingest_customers.py
|   |   |-- ingest_products.py
|   |   |-- ingest_sales.py
|   |   `-- ingest_shops.py
|   |-- transform/
|   |   |-- __init__.py
|   |   `-- build_comercial.py
|   |-- export/
|   |   |-- __init__.py
|   |   `-- dashboard_data.py
|   `-- run_pipeline.py
|-- data/
|   |-- raw/
|   |-- analytics/
|   |   `-- comercial/
|   `-- dashboard/
|-- dashboard/
|   |-- index.html
|   `-- assets/
|       `-- comercial_summary.json
`-- tests/
    |-- __init__.py
    |-- test_build_comercial.py
    `-- test_dashboard_data.py
```

## 4. Proposito de cada archivo principal

| Archivo | Proposito |
|---|---|
| `AGENTS.md` | Contexto para agentes IA: reglas del proyecto, comandos, estructura y criterios de entrega. |
| `OPENAI.md` | Registro breve de prompts/decisiones hechas con IA, si se usa OpenAI/Codex como herramienta principal. |
| `README.md` | Documento publico principal del repositorio. Debe explicar como revisar y ejecutar el proyecto. |
| `requirements.txt` | Dependencias exactas para reproducir el proyecto. |
| `.env.example` | Plantilla con `DB_USER` y `DB_PASSWORD`, sin valores reales. |
| `.gitignore` | Excluye `.env`, `.venv`, caches, logs y archivos generados que no deban subirse. |
| `config/database.yml` | Host, puerto, nombre de base, driver JDBC y opciones de conexion. |
| `config/spark_config.yml` | Configuracion de Spark local y conector MySQL. |
| `docs/ANALISIS_MULTIHOPE.md` | Analisis del proyecto base y esquema real de datos. |
| `docs/PLAN_RUTA_IA_CHALLENGE.md` | Este plan de ruta. |
| `docs/MODELO_LOGICO_COMERCIAL.md` | Explicacion previa del modelo logico antes del codigo final. |
| `docs/DASHBOARD_PLAN.md` | Estructura HTML, librerias sugeridas y organizacion de datos del dashboard. |
| `src/utils/config_loader.py` | Carga `.env`, YAML y arma la configuracion de conexion. |
| `src/utils/spark_session.py` | Crea la sesion Spark con configuracion centralizada. |
| `src/ingest/extract_tables.py` | Funcion generica para leer tablas desde MySQL y escribirlas en `data/raw/<tabla>/`. |
| `src/ingest/ingest_customers.py` | Entrada especifica para `customers`. |
| `src/ingest/ingest_products.py` | Entrada especifica para `products`. |
| `src/ingest/ingest_sales.py` | Entrada especifica para `sales`. |
| `src/ingest/ingest_shops.py` | Entrada especifica para `shops`. |
| `src/transform/build_comercial.py` | Une las cuatro tablas y genera el dataset analitico `comercial`. |
| `src/export/dashboard_data.py` | Lee Parquet `comercial` y genera JSON agregado para el dashboard. |
| `src/run_pipeline.py` | Ejecuta el flujo completo: ingesta, transformacion y exportacion para dashboard. |
| `data/raw/` | Datos crudos por tabla en Parquet. |
| `data/analytics/comercial/` | Dataset final `comercial` en Parquet. |
| `dashboard/index.html` | Dashboard final para abrir con doble clic o desde el navegador. |
| `dashboard/assets/comercial_summary.json` | Agregados para KPI y graficos. |
| `tests/` | Pruebas unitarias de transformaciones y agregados principales. |

## 5. Modelo logico esperado de `comercial`

Antes de escribir codigo, se debe documentar el modelo en `docs/MODELO_LOGICO_COMERCIAL.md`.

### Fuente

| Tabla | Rol |
|---|---|
| `sales` | Tabla de hechos principal. Cada fila representa una venta. |
| `customers` | Dimension de clientes. |
| `products` | Dimension de productos. |
| `shops` | Dimension de tiendas/sucursales. |

### Joins

| Desde | Hacia | Tipo recomendado | Motivo |
|---|---|---|---|
| `sales.cod_cliente` | `customers.id_cliente` | LEFT JOIN | Mantener todas las ventas aunque falte cliente. |
| `sales.cod_producto` | `products.id_producto` | LEFT JOIN | Mantener todas las ventas aunque falte producto. |
| `sales.cod_sucursal` | `shops.id_sucursal` | LEFT JOIN | La base tiene ventas con sucursal huerfana. |

### Columnas sugeridas en `comercial`

| Columna final | Fuente/calculo | Uso |
|---|---|---|
| `invoice_id` | `sales.cod_factura` | Identificador de factura. |
| `sale_date` | `sales.fecha_venta` | Tendencia diaria. |
| `sale_month` | derivada de `sale_date` | Analisis mensual. |
| `customer_id` | `sales.cod_cliente` | Relacion con cliente. |
| `customer_name` | `customers.nombre` | Reportes. |
| `customer_status` | `customers.estado` | Segmentacion. |
| `product_id` | `sales.cod_producto` | Relacion con producto. |
| `product_name` | `products.nombre_producto` | Grafico de barras por producto. |
| `product_brand` | `products.marca` | Analisis por marca. |
| `shop_id` | `sales.cod_sucursal` | Relacion con tienda. |
| `shop_name` | `shops.nombre_sucursal` | Grafico de pastel por tienda. |
| `shop_city` | `shops.ciudad` | Analisis geografico. |
| `quantity` | `sales.cantidad` | Unidades vendidas. |
| `unit_price` | `sales.precio_unitario` | Precio real vendido. |
| `subtotal` | `quantity * unit_price` | Total vendido por linea. |
| `is_orphan_shop` | `shops.id_sucursal IS NULL` | Trazabilidad de integridad. |
| `_source_tables` | literal/lista | Trazabilidad de origen. |
| `_created_at` | timestamp de proceso | Auditoria del dataset. |

### Ruta del dataset final

```text
data/analytics/comercial/
```

Formato:

```text
parquet
```

## 6. Plan del dashboard HTML

Antes de implementar `dashboard/index.html`, se debe documentar el plan en `docs/DASHBOARD_PLAN.md`.

### Libreria sugerida

Usar `Chart.js` mediante CDN porque:

- Permite graficos de linea, pastel y barras.
- Funciona en un HTML simple.
- No requiere backend.
- Es facil de revisar en navegador.

Alternativa aceptable: Plotly por CDN.

### Componentes minimos

| Componente | Fuente de datos | Visual |
|---|---|---|
| KPI total vendido | `SUM(subtotal)` | Tarjeta KPI. |
| Tendencia diaria ultimos 30 dias | `sale_date`, `SUM(subtotal)` | Line chart. |
| Participacion por tienda | `shop_name`, `SUM(subtotal)` | Pie chart. |
| Ventas por producto | `product_name`, `SUM(subtotal)` | Bar chart. |

### Datos requeridos para el dashboard

Archivo sugerido:

```text
dashboard/assets/comercial_summary.json
```

Estructura sugerida:

```json
{
  "kpis": {
    "total_sold": 0
  },
  "daily_sales_last_30_days": [
    {"sale_date": "2025-06-01", "total_sold": 0}
  ],
  "sales_by_shop": [
    {"shop_name": "Sucursal Quito Sur", "total_sold": 0}
  ],
  "sales_by_product": [
    {"product_name": "Detergente Multiusos", "total_sold": 0}
  ]
}
```

### Requisito de apertura local

El HTML debe abrir en navegador sin servidor dedicado. Para evitar problemas de CORS con `fetch()` sobre archivos locales, hay dos opciones:

1. Incrustar el JSON directamente dentro de `index.html`.
2. Generar `index.html` desde Python reemplazando una variable JavaScript con los agregados.

Decision recomendada: generar un `index.html` autocontenido con los datos embebidos en una variable `const dashboardData = ...`.

## 7. Orden recomendado de implementacion

### Fase 0 - Preparacion GitHub

1. Crear en GitHub un repositorio publico llamado exactamente `ia-challenge`.
2. Clonarlo en la maquina local.
3. Copiar o crear la estructura base del proyecto.
4. Confirmar que el remoto apunta al repositorio correcto.

Comandos esperados, ajustando usuario:

```powershell
git clone https://github.com/<usuario>/ia-challenge.git
cd ia-challenge
git remote -v
```

### Fase 1 - Contexto IA y documentacion inicial

1. Crear `AGENTS.md`.
2. Crear `OPENAI.md` o `CLAUDE.md`, segun herramienta usada.
3. Copiar `docs/ANALISIS_MULTIHOPE.md`.
4. Mantener `docs/PLAN_RUTA_IA_CHALLENGE.md`.
5. Crear `docs/MODELO_LOGICO_COMERCIAL.md`.
6. Crear `docs/DASHBOARD_PLAN.md`.

### Fase 2 - Configuracion

1. Crear `requirements.txt`.
2. Crear `.gitignore`.
3. Crear `.env.example`.
4. Crear `config/database.yml`.
5. Crear `config/spark_config.yml`.
6. Crear entorno virtual local.
7. Instalar dependencias.

### Fase 3 - Conexion e ingesta

1. Implementar `src/utils/config_loader.py`.
2. Implementar `src/utils/spark_session.py`.
3. Implementar `src/ingest/extract_tables.py`.
4. Implementar wrappers por tabla:
   - `ingest_customers.py`
   - `ingest_products.py`
   - `ingest_sales.py`
   - `ingest_shops.py`
5. Ejecutar ingesta.
6. Verificar que existan:
   - `data/raw/customers/`
   - `data/raw/products/`
   - `data/raw/sales/`
   - `data/raw/shops/`

### Fase 4 - Construccion de `comercial`

1. Implementar `src/transform/build_comercial.py`.
2. Leer las cuatro tablas desde `data/raw/`.
3. Aplicar casts y nombres claros.
4. Hacer LEFT JOIN desde `sales`.
5. Calcular `subtotal`.
6. Agregar columnas de trazabilidad.
7. Guardar en:

```text
data/analytics/comercial/
```

### Fase 5 - Agregados para dashboard

1. Implementar `src/export/dashboard_data.py`.
2. Leer `data/analytics/comercial/`.
3. Calcular:
   - total vendido.
   - tendencia diaria ultimos 30 dias.
   - ventas por tienda.
   - ventas por producto.
4. Generar datos embebibles para HTML.

### Fase 6 - Dashboard HTML

1. Crear estructura visual de `dashboard/index.html`.
2. Usar Chart.js por CDN.
3. Incluir:
   - KPI total vendido.
   - linea de tendencia diaria.
   - pastel por tienda.
   - barras por producto.
4. Asegurar que abra localmente sin servidor.
5. Probar en navegador.

### Fase 7 - README

El `README.md` debe explicar:

1. Objetivo del proyecto.
2. Base de datos usada.
3. Tablas usadas: `customers`, `products`, `sales`, `shops`.
4. Proceso realizado.
5. Como se construyo `comercial`.
6. Donde esta el Parquet.
7. Donde esta el dashboard.
8. Cual es el archivo `index.html`.
9. Como ejecutar el proyecto.
10. Como revisar el resultado sin ejecutar nada.

### Fase 8 - Pruebas y validacion

1. Crear pruebas unitarias para el join principal.
2. Crear pruebas para calculo de `subtotal`.
3. Crear pruebas para agregados del dashboard.
4. Ejecutar tests.
5. Verificar que no se suba `.env`.
6. Verificar que el HTML abre localmente.

### Fase 9 - Publicacion

1. Revisar estado de Git.
2. Hacer commit.
3. Hacer push a GitHub.
4. Verificar que el repositorio sea publico.
5. Verificar que `README.md` se renderice correctamente.
6. Verificar que `dashboard/index.html` este disponible en el repo.

## 8. Criterios de aceptacion

El proyecto se considera completo cuando:

- Existe repositorio publico `ia-challenge`.
- No hay credenciales hardcodeadas.
- Se ingieren las cuatro tablas requeridas.
- Existe un unico dataset analitico `comercial`.
- `comercial` queda guardado en Parquet.
- El dashboard HTML incluye los cuatro componentes requeridos.
- `index.html` abre sin servidor dedicado.
- El README explica claramente ejecucion y revision.
- Existen archivos de contexto IA.
- El repositorio contiene codigo fuente reproducible.

## 9. Riesgos y decisiones tecnicas

| Riesgo | Decision |
|---|---|
| Exponer password en GitHub | Usar `.env`, `.env.example` y `.gitignore`. |
| HTML local no puede leer JSON por CORS | Generar HTML autocontenido con datos embebidos. |
| `sales.cod_sucursal` tiene huerfanos | Usar LEFT JOIN y columna `is_orphan_shop`. |
| Datos generados pueden ocupar espacio | Mantener solo salidas necesarias o documentar regeneracion. |
| Diferencias de entorno Windows | Usar Python 3.11 y centralizar Spark en `spark_session.py`. |

## 10. Proximo paso

El siguiente paso recomendado es crear la estructura inicial del repositorio local `ia-challenge`, copiar este plan y empezar por los archivos de contexto IA:

1. `AGENTS.md`
2. `OPENAI.md`
3. `docs/MODELO_LOGICO_COMERCIAL.md`
4. `docs/DASHBOARD_PLAN.md`

Despues de eso se debe implementar la configuracion, ingesta y transformacion.
