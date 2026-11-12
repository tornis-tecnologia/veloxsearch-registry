# RabbitMQ

Logs del nodo RabbitMQ recogidos por Velox Agent desde los archivos de log del host.

## Streams

| Stream | Señal | Por defecto | Índice | Qué recoge |
| --- | --- | --- | --- | --- |
| `log` | logs | sí | `veloxagent-log.rabbitmq-v1` | `/var/log/rabbitmq/*.log`: un evento por entrada; las líneas de continuación (crash reports) se unen a la entrada anterior |

## Campos

`@timestamp`, `message`, `log.level` (`debug`, `info`, `notice`, `warning`, `error`, `critical`), `rabbitmq.pid` (pid de Erlang, p. ej. `0.123.0`) y, en mensajes de conexión, `source.ip`, `source.port` y `user.name`. Los códigos de color ANSI se eliminan antes de analizar. `event.outcome` es `unparsed` cuando una línea no tiene forma de RabbitMQ; `velox.*`.

## Requisitos

- Linux. El usuario del agente debe leer `/var/log/rabbitmq/*.log`. El campo `multiline` elige cómo se unen las líneas de continuación (por defecto, el parser Erlang del paquete).

## Dashboard

*RabbitMQ — resumen*: volumen de logs, errores en el tiempo, volumen por nivel, desglose por nivel, mensajes más frecuentes.
