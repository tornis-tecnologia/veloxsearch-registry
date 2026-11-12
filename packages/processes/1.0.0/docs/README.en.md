# Processes

Per-process CPU, memory, I/O and file descriptors, plus single-process health checks.

## Streams

| Stream | Signal | Default | Destination | What it collects |
| --- | --- | --- | --- | --- |
| `exporter` | metrics | on | OTLP endpoint of the policy → Cortex | CPU, I/O, memory, state, context switches, file descriptors and threads per process |
| `process` | metrics | off | `veloxagent-process.processes-v1` | `name`, `pid`, `alive`, `mem.*`, `fd` of one process |

## Fields

`exporter`: `scrape_interval` (default 5), `collectors` (cpu, io, memory, state, context_switches, fd, start_time, thread_wchan, thread), `process_include_pattern` (regex, default `.+`) and `process_exclude_pattern` (regex).

`process`: `proc_name` (required), `interval` (seconds, default 10), `mem`, `fd`, advanced `alert`, and `delete_after` (default 14d). Indexed fields: `@timestamp`, `name`, `pid`, `alive`, `mem.*`, `fd`, `velox.*`.

## Requirements

- Linux. The agent user must read `/proc` of the processes to watch (usually root for other users' processes).
- `exporter` needs an OTLP endpoint on the policy (deployment with the OTel stack).

## Notes

`process` follows a single process name; enable it once per process you care about by using a policy per service, or use `exporter` with an include pattern for many.
