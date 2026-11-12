# OpenTelemetry

Receptor OTLP de logs, métricas y trazas desde SDKs y colectores OpenTelemetry.

## Streams

| Stream | Señal | Por defecto | Destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `logs` | logs | activa | `veloxagent-logs.opentelemetry-v1` | Registros de log OTLP: `log.level`, `message`, `trace_id`, `span_id`, `service.name`, `resource.*`, `attributes.*` |
| `metrics` | metrics | inactiva | Endpoint OTLP de la política → Cortex | Métricas OTLP de aplicaciones y colectores |
| `traces` | traces | inactiva | `veloxagent-traces.opentelemetry-v1` | Spans: `trace_id`, `span_id`, `parent_span_id`, `name`, `kind`, `start`, `end`, `duration`, `status`, `attributes.*` |

## Campos

Todos los streams: `listen` (por defecto `0.0.0.0`), `port`, `tls` con `tls_crt_file`, `tls_key_file`, `tls_key_passwd` (secreto) y `tls_ca_file`, y `buffer_max_size`. `traces` tiene además `raw_traces`. Logs y trazas exponen `delete_after` (por defecto 30d / 14d).

Los puertos por defecto son distintos por stream: `logs` 4318, `metrics` 4319, `traces` 4320. Apunte cada exportador del SDK al puerto correspondiente (`http://host:4318/v1/logs`, `:4319/v1/metrics`, `:4320/v1/traces`).

Campos de log indexados: `@timestamp` (de `time_unix_nano` si existe), `log.level` (de `severity_text`, en minúsculas), `otel.severity_number`, `message` (de `body`), `trace_id`, `span_id`, `service.name`, `host.name`, `resource.*`, `attributes.*`, `velox.*`.

## Requisitos

- El puerto de escucha debe ser accesible para las aplicaciones (firewall, red de contenedores).
- `metrics` requiere un endpoint OTLP en la política (deployment con el stack OTel).

## Notas

En Fluent Bit las tres señales comparten el mismo plugin `opentelemetry` y un listener por input. Activar dos streams hace que el compilador emita dos inputs, que deben escuchar en puertos distintos; por eso los valores por defecto difieren. Si cambia un puerto, manténgalos distintos (o active un solo stream). El paquete fija `tag_from_uri: false` para que los registros conserven el tag del stream usado en el enrutamiento. Solo se expone el puerto HTTP; gRPC no es configurable como puerto aparte en el plugin.

## Dashboard

*OpenTelemetry — logs*: volumen por servicio, niveles de severidad, servicios principales y errores recientes por servicio.
