# OpenTelemetry

OTLP receiver for logs, metrics and traces from OpenTelemetry SDKs and collectors.

## Streams

| Stream | Signal | Default | Destination | What it collects |
| --- | --- | --- | --- | --- |
| `logs` | logs | on | `veloxagent-logs.opentelemetry-v1` | OTLP log records: `log.level`, `message`, `trace_id`, `span_id`, `service.name`, `resource.*`, `attributes.*` |
| `metrics` | metrics | off | OTLP endpoint of the policy → Cortex | OTLP metrics from applications and collectors |
| `traces` | traces | off | `veloxagent-traces.opentelemetry-v1` | Spans: `trace_id`, `span_id`, `parent_span_id`, `name`, `kind`, `start`, `end`, `duration`, `status`, `attributes.*` |

## Fields

All streams: `listen` (default `0.0.0.0`), `port`, `tls` with `tls_crt_file`, `tls_key_file`, `tls_key_passwd` (secret) and `tls_ca_file`, and `buffer_max_size`. `traces` also has `raw_traces`. Logs and traces expose `delete_after` (default 30d / 14d).

Default ports are distinct per stream: `logs` 4318, `metrics` 4319, `traces` 4320. Point each SDK exporter at the matching port (`http://host:4318/v1/logs`, `:4319/v1/metrics`, `:4320/v1/traces`).

Indexed log fields: `@timestamp` (from `time_unix_nano` when present), `log.level` (from `severity_text`, lower case), `otel.severity_number`, `message` (from `body`), `trace_id`, `span_id`, `service.name`, `host.name`, `resource.*`, `attributes.*`, `velox.*`.

## Requirements

- The listening port must be reachable by the applications (firewall, container networking).
- `metrics` needs an OTLP endpoint on the policy (deployment with the OTel stack).

## Notes

In Fluent Bit all three signals share the same `opentelemetry` input plugin and one listener per input. Enabling two streams makes the compiler emit two inputs, so they must listen on different ports; that is why the defaults differ. If you change a port, keep them distinct (or enable only one stream). The package fixes `tag_from_uri: false` so records keep the stream tag used for routing. Only the HTTP port is exposed; gRPC is not configurable as a separate port in the plugin.

## Dashboard

*OpenTelemetry — logs*: volume by service, severity levels, top services and recent errors by service.
