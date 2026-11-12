# Apache Kafka

Logs del broker Apache Kafka recogidos por Velox Agent desde los archivos de log del host.

## Streams

| Stream | Señal | Por defecto | Índice | Qué recoge |
| --- | --- | --- | --- | --- |
| `server` | logs | sí | `veloxagent-server.kafka-v1` | `server.log`: log del broker; los stack traces Java se unen en un evento |
| `controller` | logs | no | `veloxagent-controller.kafka-v1` | `controller.log`: actividad del controller |
| `state_change` | logs | no | `veloxagent-state_change.kafka-v1` | `state-change.log`: transiciones de particiones y réplicas |

## Campos

`@timestamp`, `message`, `log.level` (`trace`, `debug`, `info`, `warn`, `error`, `fatal`), `kafka.logger` (clase entre paréntesis, p. ej. `kafka.controller.KafkaController`), `kafka.context` (contexto entre corchetes, p. ej. `Controller id=1`), `error.stack_trace` (cuando un stack trace Java sigue a la entrada), `event.outcome` (`unparsed` cuando una línea no tiene forma log4j), `velox.*`.

## Requisitos

- Linux. El usuario del agente debe leer el directorio de logs de Kafka (`/var/log/kafka` o `<kafka>/logs`). El campo `multiline` elige cómo unir stack traces: el parser del paquete o el `java` integrado de Fluent Bit.

## Dashboard

*Kafka — resumen* (stream `server`): volumen de logs, errores en el tiempo, volumen por nivel, desglose por nivel, loggers y mensajes más frecuentes.
