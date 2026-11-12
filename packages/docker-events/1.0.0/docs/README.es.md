# Docker events

Eventos del demonio Docker del host, recolectados por Velox Agent.

## Streams

| Stream | Señal | Predeterminado | Índice / destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `events` | logs | sí | `veloxagent-events.docker-events-v1` | Eventos del demonio Docker: acción, tipo de objeto, id, nombre e imagen del contenedor y código de salida. |

## Campos

`@timestamp` (de `time`), `event.action`, `event.category`, `docker.type`, `docker.scope`, `docker.status`, `docker.exit_code`, `docker.actor.id`, `docker.actor.name`, `container.id`, `container.name`, `container.image.name`, `event.outcome` (`unparsed` si la línea no es un evento), `velox.*`.

## Requisitos

- Linux con Docker; el usuario del agente debe leer `/var/run/docker.sock` (grupo `docker`).
- Solo se recolectan eventos desde que el agente se conecta; Docker no reenvía el historial.

## Dashboard

*Docker events — overview*: eventos por acción en el tiempo, contenedores principales, contenedores que murieron o sufrieron OOM, eventos por tipo de objeto.
