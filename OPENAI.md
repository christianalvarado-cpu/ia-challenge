# OPENAI.md - Registro de uso de IA

Este proyecto usa asistencia de IA para planificacion, documentacion y apoyo en implementacion.

## Solicitudes principales a IA

1. Analizar el proyecto base `multihope`.
2. Proponer estructura inicial de carpetas y archivos.
3. Explicar el modelo logico del dataset `comercial` antes de codificar.
4. Proponer estructura del dashboard HTML, librerias de graficos y datos requeridos.
5. Implementar el pipeline reproducible sin exponer credenciales.

## Decisiones tomadas con IA

- Mantener una arquitectura por capas: ingesta, transformacion, exportacion y dashboard.
- Usar Parquet para salidas de datos.
- Usar `Chart.js` por CDN para el dashboard HTML.
- Generar HTML autocontenido para evitar problemas CORS al abrir localmente.
- Usar LEFT JOIN desde `sales` hacia dimensiones para conservar todas las ventas.
