# Fluent Forward

A Forward receiver: Fluent Bit and Fluentd instances send their events to this agent, which indexes them in OpenSearch.

## Streams

| Stream | Signal | Default | Index / destination | What it collects |
| --- | --- | --- | --- | --- |
| `logs` | logs | on | `veloxagent-logs.fluent-forward-v1` | Forward-protocol events listening on TCP 24224 (optional shared key) |

## Fields

`@timestamp` (from `time`, `timestamp` or `ts`, ISO-8601 or epoch seconds/milliseconds; ingest time otherwise), `host.name` (from a string `host` or `hostname`), `event.outcome`, `velox.*`. All other keys are kept as they arrive.

## Requirements

- The port (default 24224) must be reachable from the senders; the agent needs permission to listen.
- With `shared_key` the senders must use Secure Forward with the same key.

## Dashboard

*Fluent Forward — overview*: events over time by host, top hosts and records by outcome.
