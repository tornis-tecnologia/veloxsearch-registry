# Prometheus

Métricas en formato Prometheus de exporters, textfiles o remote write.

## Streams

| Stream | Señal | Predeterminado | Índice / destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `scrape` | metrics | sí | Endpoint OTLP de la política | Raspa `/metrics` de un host y puerto (TLS, basic auth y bearer token opcionales) |
| `textfile` | metrics | no | Endpoint OTLP de la política | Lee archivos `*.prom` del textfile collector |
| `remote_write` | metrics | no | Endpoint OTLP de la política | Recibe solicitudes remote-write de Prometheus en un puerto |

## Campos

Las métricas conservan sus nombres y labels de Prometheus; el agente agrega `velox_integration`, `velox_stream` y `velox_package_version`. No se escribe nada en OpenSearch.

## Requisitos

- Todos los streams requieren un endpoint OTLP en la política (deployment con el stack OTel); sin él la consola no los ofrece.
- `remote_write` abre un puerto de escucha en el host; manténgalo en una interfaz de confianza o active TLS.

## Dashboard

Ninguno. Los dashboards de métricas necesitan la datasource Prometheus del deployment; constrúyalos sobre los labels `velox_integration` y `velox_stream`.
