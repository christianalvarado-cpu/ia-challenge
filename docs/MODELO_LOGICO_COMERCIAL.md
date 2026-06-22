# Modelo logico del dataset `comercial`

## Objetivo

Construir una unica estructura analitica llamada `comercial` a partir de las tablas fuente `customers`, `products`, `sales` y `shops`.

El dataset debe servir como base para analisis comercial y dashboard, evitando que el HTML o las consultas de consumo tengan que repetir joins o reglas de negocio.

## Grano del dataset

El grano de `comercial` es una linea de venta.

Cada fila representa una venta registrada en `sales`, enriquecida con datos del cliente, producto y tienda cuando existe correspondencia.

## Tabla principal

La tabla principal es `sales` porque contiene los eventos comerciales:

- factura
- fecha de venta
- cliente
- producto
- sucursal
- cantidad
- precio unitario real de venta

Todas las filas de `sales` deben conservarse.

## Dimensiones usadas

| Tabla | Rol | Clave logica |
|---|---|---|
| `customers` | Dimension de clientes | `id_cliente` |
| `products` | Dimension de productos | `id_producto` |
| `shops` | Dimension de tiendas/sucursales | `id_sucursal` |

## Joins definidos

| Desde `sales` | Hacia dimension | Tipo de join | Motivo |
|---|---|---|---|
| `cod_cliente` | `customers.id_cliente` | LEFT JOIN | Mantener ventas aunque falte cliente. |
| `cod_producto` | `products.id_producto` | LEFT JOIN | Mantener ventas aunque falte producto. |
| `cod_sucursal` | `shops.id_sucursal` | LEFT JOIN | Existen ventas con sucursal sin match. |

Se usa LEFT JOIN desde `sales` para no perder ventas. Si una dimension no encuentra correspondencia, los atributos quedan nulos y se activa una bandera de huerfano.

## Columnas finales

| Columna | Tipo esperado | Fuente/calculo | Uso analitico |
|---|---|---|---|
| `invoice_id` | int | `sales.cod_factura` | Identificar factura. |
| `sale_date` | date | `sales.fecha_venta` | Tendencia diaria. |
| `sale_month` | string | `yyyy-MM` de `sale_date` | Analisis mensual. |
| `customer_id` | int | `sales.cod_cliente` | Identificar cliente. |
| `customer_name` | string | `customers.nombre` | Reportes por cliente. |
| `customer_email` | string | `customers.email` | Contacto/segmentacion. |
| `customer_status` | string | `customers.estado` | Estado comercial del cliente. |
| `product_id` | int | `sales.cod_producto` | Identificar producto. |
| `product_name` | string | `products.nombre_producto` | Ventas por producto. |
| `product_brand` | string | `products.marca` | Analisis por marca. |
| `catalog_unit_price` | double | `products.precio_unitario` | Comparacion con precio real. |
| `product_stock` | int | `products.stock` | Referencia de inventario. |
| `shop_id` | int | `sales.cod_sucursal` | Identificar tienda. |
| `shop_name` | string | `shops.nombre_sucursal` | Participacion por tienda. |
| `shop_city` | string | `shops.ciudad` | Analisis geografico. |
| `shop_latitude` | double | `shops.latitud` | Mapa o geografia. |
| `shop_longitude` | double | `shops.longitud` | Mapa o geografia. |
| `quantity` | int | `sales.cantidad` | Unidades vendidas. |
| `sale_unit_price` | double | `sales.precio_unitario` | Precio real cobrado. |
| `subtotal` | double | `quantity * sale_unit_price` | Total vendido por linea. |
| `unit_price_delta` | double | `sale_unit_price - catalog_unit_price` | Diferencia contra catalogo. |
| `is_orphan_customer` | boolean | cliente sin match | Calidad referencial. |
| `is_orphan_product` | boolean | producto sin match | Calidad referencial. |
| `is_orphan_shop` | boolean | tienda sin match | Calidad referencial. |
| `_source_tables` | string | literal | Trazabilidad de tablas usadas. |
| `_created_at` | timestamp | timestamp del proceso | Auditoria de construccion. |

## Reglas de consistencia

- `sale_date` debe ser tipo `date`.
- `quantity` debe ser entero.
- `sale_unit_price`, `catalog_unit_price`, `subtotal` y `unit_price_delta` deben ser numericos `double`.
- `subtotal` se redondea a 2 decimales.
- `sale_month` se genera con formato `yyyy-MM`.
- Los nombres finales deben estar en ingles y en `snake_case` para facilitar consumo analitico.

## Ruta de salida

El dataset final se guarda como Parquet en:

```text
data/analytics/comercial/
```

## Nota de integridad

En la base fuente, `sales.cod_sucursal` tiene ventas sin correspondencia en `shops.id_sucursal`. Por eso `comercial` usa LEFT JOIN con `shops` y conserva esas filas con `is_orphan_shop = true`.
