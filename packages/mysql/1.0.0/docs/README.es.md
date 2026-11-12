# MySQL / MariaDB

Logs de servidores MySQL y MariaDB, recolectados por Velox Agent.

## Streams

| Stream | Señal | Por defecto | Índice / destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `error` | logs | sí | `veloxagent-error.mysql-v1` | log de errores de MySQL 5.7/8.x y MariaDB: nivel, hilo, código de error, subsistema |
| `slowlog` | logs | no | `veloxagent-slowlog.mysql-v1` | log de consultas lentas, un evento por entrada: usuario, host, tiempo, bloqueo, filas, consulta |

## Campos

`error`: `@timestamp`, `message`, `log.level` (`note`/`system` → `info`), `mysql.thread_id`, `mysql.error_code`, `mysql.subsystem`. `slowlog`: `@timestamp`, `message` (la consulta), `user.name`, `source.address`, `source.ip`, `event.duration` (ns), `mysql.slowlog.lock_time` (segundos), `mysql.slowlog.rows_sent`, `mysql.slowlog.rows_examined`, `mysql.slowlog.query`. Ambos: `event.outcome` (`unparsed`), `velox.*`.

## Requisitos

- Linux. El usuario del agente debe leer los archivos de log. Para `slowlog` define `slow_query_log=ON`, `slow_query_log_file` y `long_query_time` en el servidor.

## Dashboard

*MySQL / MariaDB — resumen*: eventos, errores en el tiempo, volumen por nivel, niveles, subsistemas, mensajes más frecuentes y consultas lentas en el tiempo.
