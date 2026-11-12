# MongoDB

Log del servidor MongoDB, recolectado por Velox Agent.

## Streams

| Stream | Señal | Por defecto | Índice / destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `log` | logs | sí | `veloxagent-log.mongo-v1` | `mongod.log`: líneas JSON (4.4+) con severidad, componente, contexto, mensaje y `attr`; líneas de texto heredadas como respaldo |

## Campos

`@timestamp`, `message`, `log.level` (`F`→`fatal`, `E`→`error`, `W`→`warning`, `I`→`info`, `D1..5`→`debug`), `mongo.component`, `mongo.context`, `mongo.id`, `mongo.attr` (`flat_object`, buscable por ruta con puntos), `event.duration` (ns, de `attr.durationMillis`), `event.outcome` (`unparsed`), `velox.*`.

## Requisitos

- Linux. `systemLog.destination: file` con `systemLog.path`; el usuario del agente debe leer el archivo (grupo `mongodb` o `adm`). Las consultas lentas aparecen con `operationProfiling.slowOpThresholdMs`. `mongo.attr` requiere OpenSearch 2.7+ (`flat_object`).

## Dashboard

*MongoDB — resumen*: eventos, errores en el tiempo, volumen por severidad, severidad, componentes y mensajes más frecuentes.
