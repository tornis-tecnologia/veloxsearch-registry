# Redis

Logs del servidor Redis recogidos por Velox Agent desde los archivos de log del host.

## Streams

| Stream | Señal | Por defecto | Índice | Qué recoge |
| --- | --- | --- | --- | --- |
| `log` | logs | sí | `veloxagent-log.redis-v1` | `/var/log/redis/redis-server.log`, `/var/log/redis/*.log`: un evento por línea |

## Campos

`@timestamp` (la hora del propio log, con o sin año), `message`, `process.pid`, `redis.role` (`master`, `replica`, `child`, `sentinel`), `log.level` (`debug`, `verbose`, `notice`, `warning`), `event.outcome` (`unparsed` cuando una línea no tiene forma de Redis), `velox.*`.

## Requisitos

- Linux. El usuario del agente debe poder leer los logs de Redis (configure `logfile /var/log/redis/redis-server.log`; por defecto Redis escribe en stdout).

## Dashboard

*Redis — resumen*: volumen de logs, advertencias en el tiempo, volumen por rol, desgloses por nivel y rol, mensajes más frecuentes.
