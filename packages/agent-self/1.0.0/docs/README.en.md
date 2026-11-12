# Velox Agent self-monitoring

The agent observing itself: its own Fluent Bit log, TCP reachability checks and internal metrics.

## Streams

| Stream | Signal | Default | Index / destination | What it collects |
| --- | --- | --- | --- | --- |
| `logs` | logs | on | `veloxagent-logs.agent-self-v1` | Fluent Bit log lines parsed into level, component and message |
| `health` | logs | off | `veloxagent-health.agent-self-v1` | TCP connect checks of a host and port: up or down |
| `metrics` | metrics | off | OTLP endpoint of the policy | Fluent Bit internal metrics (needs the OTel stack) |

## Fields

`logs`: `@timestamp`, `message`, `log.level`, `fluentbit.component`, `event.original`, `event.outcome` (`unparsed`). `health`: `health.alive`, `destination.address`, `destination.port`, `event.outcome` (`success`/`failure`), `event.category`. All: `velox.*`.

## Requirements

- `health` needs a host and port; the stream is off until you give them.
- `metrics` needs an OTLP endpoint on the policy.
- Log timestamps are read as UTC; Fluent Bit prints local time.

## Dashboard

*Agent self-monitoring — overview*: log lines by level, noisiest components, errors and warnings by component, TCP checks over time and per target.
