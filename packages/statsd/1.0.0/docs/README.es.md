# StatsD

Listener UDP compatible con StatsD para contadores, gauges y timers de aplicaciones.

## Streams

| Stream | Señal | Por defecto | Destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `events` | metrics | activa | `veloxagent-events.statsd-v1` | `type`, `bucket`, `value`, `sample_rate` por datagrama |
| `metrics` | metrics | inactiva | Endpoint OTLP de la política → Cortex | Contadores, gauges y timers como métricas |

## Campos

Ambos streams: `listen` (por defecto `0.0.0.0`) y `port` (UDP; `metrics` 8125, `events` 8126). `events` expone además `delete_after` (por defecto 14d).

Campos indexados (`events`): `@timestamp`, `type` (counter, gauge, timer), `bucket`, `value`, `sample_rate`, `velox.*`.

## Requisitos

- Las aplicaciones envían StatsD por UDP al puerto del agente.
- `metrics` requiere un endpoint OTLP en la política.

## Notas

La opción `metrics` del plugin decide lo que emite, por eso cada stream la fija (`events`: off, `metrics`: on). Son listeners separados: mantenga sus puertos distintos si activa ambos.

## Dashboard

*StatsD — muestras*: volumen de muestras por tipo y valor medio por bucket.
