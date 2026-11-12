# PostgreSQL

Log del servidor PostgreSQL, recolectado por Velox Agent.

## Streams

| Stream | Señal | Por defecto | Índice / destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `log` | logs | sí | `veloxagent-log.postgres-v1` | archivos de `log_directory`, sentencias multilínea unidas; nivel, pid, usuario, base de datos, duración y eventos de conexión |

## Campos

`@timestamp`, `message`, `log.level` (minúsculas; `debug1..5` → `debug`), `process.pid`, `user.name`, `postgres.database`, `postgres.statement`, `event.duration` (ns, de `duration: … ms`), `event.action` (`connection-received`, `connection-authorized`, `disconnection`), `source.ip`, `source.port`, `event.outcome` (`unparsed`), `velox.*`.

## Requisitos

- Linux. Activa `logging_collector = on` y `log_line_prefix = '%m [%p] %q%u@%d '`; usa `log_min_duration_statement` y `log_connections` para duraciones y conexiones. El usuario del agente debe leer los archivos de log (grupo `postgres` o `adm`).

## Dashboard

*PostgreSQL — resumen*: eventos, errores en el tiempo, volumen por nivel, niveles, mensajes más frecuentes, bases de datos y usuarios.
