# Prompt sugerido para documentacion final

## Rol

Actua como un documentador tecnico.

## Objetivo

Ayudame a redactar el README final del proyecto `ia-challenge`.

## Contexto del proyecto

El proyecto `ia-challenge` construye una solucion analitica comercial completa:

1. Se conecta a una base de datos MySQL real llamada `fake`.
2. Ingiere las tablas fuente `customers`, `products`, `sales` y `shops`.
3. Guarda las tablas crudas en formato Parquet bajo `data/raw/`.
4. Construye un unico dataset analitico llamado `comercial`.
5. Guarda `comercial` en formato Parquet bajo `data/analytics/comercial/`.
6. Genera un dashboard HTML local en `dashboard/index.html`.

## Requisitos de redaccion

- Explica claramente el flujo realizado.
- Menciona las tablas de origen.
- Explica el dataset `comercial`.
- Indica donde esta el dashboard `index.html`.
- Explica como ejecutar o revisar el proyecto.
- Redacta en espanol claro y tecnico.
- No incluyas contrasenas ni secretos.
- Menciona que las credenciales se configuran con `.env` y que `.env.example` es la plantilla.

## Estructura esperada del README

1. Titulo del proyecto.
2. Objetivo.
3. Flujo general.
4. Tablas usadas.
5. Construccion del dataset `comercial`.
6. Ubicacion del Parquet final.
7. Dashboard HTML.
8. Instrucciones de entorno local.
9. Instrucciones de ejecucion.
10. Como revisar el resultado sin ejecutar todo.
11. Archivos principales del repositorio.

## Prompt completo para usar con IA

```text
# Rol
Actua como un documentador tecnico.

# Objetivo
Ayudame a redactar el README final del proyecto `ia-challenge`.

# Contexto
El proyecto se conecta a una base de datos MySQL real llamada `fake`, ingiere las tablas `customers`, `products`, `sales` y `shops`, construye un dataset analitico unico llamado `comercial`, lo almacena en formato Parquet en `data/analytics/comercial/` y genera un dashboard HTML en `dashboard/index.html`.

# Requisitos
- Explica claramente el flujo realizado.
- Menciona las tablas de origen.
- Explica como se construye el dataset `comercial`.
- Indica donde esta el dashboard `index.html`.
- Explica como ejecutar el proyecto desde cero.
- Explica como revisar el resultado si no se quiere ejecutar todo.
- Redacta en espanol claro y tecnico.
- No incluyas secretos ni credenciales reales.

# Archivos importantes
- `config/database.yml`: configuracion no secreta de conexion.
- `.env.example`: plantilla de credenciales.
- `src/ingest/extract_tables.py`: ingesta de tablas fuente.
- `src/transform/build_comercial.py`: construccion del dataset `comercial`.
- `src/export/dashboard_data.py`: generacion del dashboard.
- `data/analytics/comercial/`: salida Parquet final.
- `dashboard/index.html`: dashboard HTML final.
- `notebooks/00_pipeline_pruebas.ipynb`: notebook de pruebas paso a paso.
```
