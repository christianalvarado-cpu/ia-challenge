# AGENTS.md - Contexto para agentes IA

## Objetivo del proyecto

Construir el proyecto final `ia-challenge` conectado a la base MySQL real `fake`, ingiriendo `customers`, `products`, `sales` y `shops`, generando un dataset analitico unico llamado `comercial` en Parquet y un dashboard HTML local.

## Reglas tecnicas

- No hardcodear credenciales.
- Usar `.env` local y `.env.example` versionado.
- Mantener la estructura por capas: `ingest`, `transform`, `export`, `dashboard`.
- El dataset final debe llamarse `comercial` y guardarse en `data/analytics/comercial/`.
- El dashboard debe abrir sin servidor dedicado.
- Documentar decisiones relevantes en `docs/`.

## Base de datos

- Host: `www.bigdataybi.com`
- Puerto: `3306`
- Base: `fake`
- Tablas: `customers`, `products`, `sales`, `shops`

## Advertencia de datos

`sales.cod_sucursal` tiene registros sin correspondencia en `shops.id_sucursal`; el modelo analitico debe usar LEFT JOIN y conservar trazabilidad con `is_orphan_shop`.

## Comandos esperados

```powershell
.\.venv\Scripts\python.exe -m src.run_pipeline
.\.venv\Scripts\python.exe -m pytest tests/ -v
```
