# Velox Agent self-monitoring

El agente observándose a sí mismo: su propio log de Fluent Bit, comprobaciones de alcance TCP y métricas internas.

## Streams

| Stream | Señal | Predeterminado | Índice / destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `logs` | logs | sí | `veloxagent-logs.agent-self-v1` | Líneas del log de Fluent Bit separadas en nivel, componente y mensaje |
| `health` | logs | no | `veloxagent-health.agent-self-v1` | Comprobaciones de conexión TCP a un host y puerto: arriba o caído |
| `metrics` | metrics | no | Endpoint OTLP de la política | Métricas internas de Fluent Bit (requiere el stack OTel) |

## Campos

`logs`: `@timestamp`, `message`, `log.level`, `fluentbit.component`, `event.original`, `event.outcome` (`unparsed`). `health`: `health.alive`, `destination.address`, `destination.port`, `event.outcome` (`success`/`failure`), `event.category`. Todos: `velox.*`.

## Requisitos

- `health` necesita host y puerto; el stream queda apagado hasta que los indique.
- `metrics` requiere un endpoint OTLP en la política.
- Las marcas de tiempo del log se leen como UTC; Fluent Bit imprime hora local.

## Dashboard

*Agent self-monitoring — overview*: líneas de log por nivel, componentes más ruidosos, errores y avisos por componente, comprobaciones TCP en el tiempo y por destino.
