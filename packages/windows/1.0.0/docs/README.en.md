# Windows

Logs and metrics of Windows hosts, collected by Velox Agent.

## Streams

| Stream | Signal | Default | Index / destination | What it collects |
| --- | --- | --- | --- | --- |
| `eventlog` | logs | on | `veloxagent-eventlog.windows-v1` | Application, System, Security and other channels (winevt API) as winlog.*, event.code, log.level |
| `eventlog_legacy` | logs | off | `veloxagent-eventlog_legacy.windows-v1` | The same channels through the classic winlog API (old Windows) |
| `stats` | metrics | off | `veloxagent-stats.windows-v1` | CPU, memory, disk and network counters as documents (no OTel stack needed) |
| `exporter_metrics` | metrics | off | OTLP endpoint of the policy | Windows Exporter compatible metrics (needs the OTel stack) |
| `etw` | logs | off | `veloxagent-etw.windows-v1` | Event Tracing for Windows provider or kernel session |

## Fields

`eventlog`: `@timestamp` (from `TimeCreated`), `message`, `host.name`, `log.level` (critical, error, warning, information, verbose), `event.code`, `event.provider`, `event.category`/`event.outcome` (logon 4624/4625), `user.id`, `user.name`, `winlog.channel`, `winlog.provider_name`, `winlog.provider_guid`, `winlog.event_id`, `winlog.record_id`, `winlog.level`, `winlog.task`, `winlog.opcode`, `winlog.keywords`, `winlog.computer_name`, `winlog.process.pid`, `winlog.process.thread.id`, `winlog.string_inserts`, `event.original` (XML or text rendering). `eventlog_legacy` maps the winlog record to the same fields. `stats` and `etw` keep the plugin's own field names.

## Requirements

- Windows with the Velox Agent running as a service account that can read the channels; `Security` needs administrator rights.
- `exporter_metrics` needs an OTLP endpoint on the policy.
- `etw` needs a provider name or GUID (provider session) or the `system` session type; an existing session with the same name is stopped and restarted.

## Dashboard

*Windows — overview*: events by channel, top providers, errors and critical events over time, top event codes, logon success vs failure.
