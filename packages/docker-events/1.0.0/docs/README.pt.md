# Docker events

Eventos do daemon Docker do host, coletados pelo Velox Agent.

## Streams

| Stream | Sinal | Padrão | Índice / destino | O que coleta |
| --- | --- | --- | --- | --- |
| `events` | logs | sim | `veloxagent-events.docker-events-v1` | Eventos do daemon Docker: ação, tipo de objeto, id, nome e imagem do contêiner e código de saída. |

## Campos

`@timestamp` (de `time`), `event.action`, `event.category`, `docker.type`, `docker.scope`, `docker.status`, `docker.exit_code`, `docker.actor.id`, `docker.actor.name`, `container.id`, `container.name`, `container.image.name`, `event.outcome` (`unparsed` se a linha não é um evento), `velox.*`.

## Requisitos

- Linux com Docker; o usuário do agente precisa ler `/var/run/docker.sock` (grupo `docker`).
- Só eventos a partir da conexão do agente são coletados; o Docker não reenvia histórico.

## Dashboard

*Docker events — overview*: eventos por ação ao longo do tempo, principais contêineres, contêineres que morreram ou sofreram OOM, eventos por tipo de objeto.
