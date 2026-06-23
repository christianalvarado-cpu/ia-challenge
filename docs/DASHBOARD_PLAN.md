# Plan del dashboard HTML

## Objetivo

Construir un dashboard HTML usando el dataset analitico `comercial` generado en Parquet.

El archivo final debe abrir directamente en navegador, sin servidor dedicado.

## Archivo final

```text
dashboard/index.html
```

## Libreria sugerida para graficos

Se usara Chart.js por CDN.

Motivos:

- Soporta graficos de linea, pastel y barras.
- Es suficiente para el alcance del proyecto.
- Permite un HTML simple y facil de revisar.
- No requiere backend ni framework frontend.

## Estructura del HTML

El dashboard se organiza en cuatro bloques principales:

1. Encabezado con titulo, descripcion y fecha de generacion.
2. KPI del total vendido.
3. Grafico de linea para tendencia diaria de ventas de los ultimos 30 dias.
4. Tres graficos comparativos: pastel por tienda, barras por producto y barras por estado de cliente.

## Componentes requeridos

| Componente | Tipo | Fuente |
|---|---|---|
| KPI total vendido | Card numerica | `SUM(subtotal)` |
| Tendencia diaria ultimos 30 dias | Line chart | `sale_date`, `SUM(subtotal)` |
| Participacion por tienda | Pie chart | `shop_name`, `SUM(subtotal)` |
| Ventas por producto | Bar chart | `product_name`, `SUM(subtotal)` |`n| Ventas por estado de cliente | Horizontal bar chart | `customer_status`, `SUM(subtotal)` |

## Organizacion de datos requerida

El HTML recibe datos embebidos en una variable JavaScript `dashboardData` con:

- `metadata`
- `kpis`
- `daily_sales_last_30_days`
- `sales_by_shop`
- `sales_by_product`

## Decision para apertura local

No se usara `fetch()` para cargar JSON local porque algunos navegadores bloquean esa lectura con `file://`.

Decision final: generar `dashboard/index.html` autocontenido con datos embebidos.

## Codigo generador

```text
src/export/dashboard_data.py
```

Este script lee `data/analytics/comercial/`, calcula los agregados y escribe `dashboard/index.html`.

