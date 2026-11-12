# Windows

Logs y métricas de hosts Windows, recolectados por Velox Agent.

## Streams

| Stream | Señal | Predeterminado | Índice / destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `eventlog` | logs | sí | `veloxagent-eventlog.windows-v1` | Application, System, Security y otros canales (API winevt) como winlog.*, event.code, log.level |
| `eventlog_legacy` | logs | no | `veloxagent-eventlog_legacy.windows-v1` | Los mismos canales con la API winlog clásica (Windows antiguo) |
| `stats` | metrics | no | `veloxagent-stats.windows-v1` | Contadores de CPU, memoria, disco y red como documentos (sin stack OTel) |
| `exporter_metrics` | metrics | no | Endpoint OTLP de la política | Métricas compatibles con Windows Exporter (requiere el stack OTel) |
| `etw` | logs | no | `veloxagent-etw.windows-v1` | Sesión ETW de proveedor o del kernel |

## Campos

`eventlog`: `@timestamp` (de `TimeCreated`), `message`, `host.name`, `log.level` (critical, error, warning, information, verbose), `event.code`, `event.provider`, `event.category`/`event.outcome` (logon 4624/4625), `user.id`, `user.name`, `winlog.channel`, `winlog.provider_name`, `winlog.provider_guid`, `winlog.event_id`, `winlog.record_id`, `winlog.level`, `winlog.task`, `winlog.opcode`, `winlog.keywords`, `winlog.computer_name`, `winlog.process.pid`, `winlog.process.thread.id`, `winlog.string_inserts`, `event.original` (XML o texto). `eventlog_legacy` mapea el registro winlog a los mismos campos. `stats` y `etw` conservan los nombres de campo del plugin.

## Requisitos

- Windows con Velox Agent ejecutándose con una cuenta de servicio que lea los canales; `Security` requiere derechos de administrador.
- `exporter_metrics` requiere un endpoint OTLP en la política.
- `etw` necesita nombre o GUID de proveedor (sesión de proveedor) o el tipo `system`; una sesión existente con el mismo nombre se detiene y se reinicia.

## Dashboard

*Windows — overview*: eventos por canal, proveedores principales, errores y eventos críticos en el tiempo, códigos de evento principales, logons exitosos vs fallidos.
