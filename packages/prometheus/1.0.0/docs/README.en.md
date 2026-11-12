# Prometheus

Prometheus-format metrics from exporters, textfiles or remote write.

## Streams

| Stream | Signal | Default | Index / destination | What it collects |
| --- | --- | --- | --- | --- |
| `scrape` | metrics | on | OTLP endpoint of the policy | Scrapes `/metrics` of one host and port (optional TLS, basic auth, bearer token) |
| `textfile` | metrics | off | OTLP endpoint of the policy | Reads `*.prom` textfile collector files |
| `remote_write` | metrics | off | OTLP endpoint of the policy | Receives Prometheus remote-write requests on a port |

## Fields

Metrics keep their Prometheus names and labels; the agent adds `velox_integration`, `velox_stream` and `velox_package_version`. Nothing is written to OpenSearch.

## Requirements

- Every stream needs an OTLP endpoint on the policy (a deployment with the OTel stack); without it the console does not offer them.
- `remote_write` opens a listening port on the host; keep it on a trusted interface or enable TLS.

## Dashboard

None. Metrics dashboards need the deployment's Prometheus datasource; build them on the labels `velox_integration` and `velox_stream`.
