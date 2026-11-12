# StatsD

Listener UDP compatível com StatsD para contadores, gauges e timers de aplicações.

## Streams

| Stream | Sinal | Padrão | Destino | O que coleta |
| --- | --- | --- | --- | --- |
| `events` | metrics | ligada | `veloxagent-events.statsd-v1` | `type`, `bucket`, `value`, `sample_rate` por datagrama |
| `metrics` | metrics | desligada | Endpoint OTLP da política → Cortex | Contadores, gauges e timers como métricas |

## Campos

Ambos os streams: `listen` (padrão `0.0.0.0`) e `port` (UDP; `metrics` 8125, `events` 8126). `events` expõe também `delete_after` (padrão 14d).

Campos indexados (`events`): `@timestamp`, `type` (counter, gauge, timer), `bucket`, `value`, `sample_rate`, `velox.*`.

## Requisitos

- As aplicações enviam StatsD por UDP para a porta do agente.
- `metrics` exige um endpoint OTLP na política.

## Notas

A opção `metrics` do plugin decide o que ele emite, por isso cada stream a fixa (`events`: off, `metrics`: on). São listeners separados: mantenha as portas distintas se ativar ambos.

## Dashboard

*StatsD — amostras*: volume de amostras por tipo e valor médio por bucket.
