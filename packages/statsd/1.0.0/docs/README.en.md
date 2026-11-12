# StatsD

StatsD-compatible UDP listener for application counters, gauges and timers.

## Streams

| Stream | Signal | Default | Destination | What it collects |
| --- | --- | --- | --- | --- |
| `events` | metrics | on | `veloxagent-events.statsd-v1` | `type`, `bucket`, `value`, `sample_rate` per datagram |
| `metrics` | metrics | off | OTLP endpoint of the policy → Cortex | Counters, gauges and timers as metrics |

## Fields

Both streams: `listen` (default `0.0.0.0`) and `port` (UDP; `metrics` 8125, `events` 8126). `events` also exposes `delete_after` (default 14d).

Indexed fields (`events`): `@timestamp`, `type` (counter, gauge, timer), `bucket`, `value`, `sample_rate`, `velox.*`.

## Requirements

- Applications send StatsD over UDP to the agent's port.
- `metrics` needs an OTLP endpoint on the policy.

## Notes

The plugin's `metrics` option decides what it emits, so each stream fixes it (`events`: off, `metrics`: on). Both are separate listeners: keep their ports distinct if you enable both.

## Dashboard

*StatsD — samples*: sample volume by type and average value by bucket.
