# eBPF tracing

Kernel-level events (signals, allocations, binds) captured with eBPF.

## Streams

| Stream | Signal | Default | Destination | What it collects |
| --- | --- | --- | --- | --- |
| `events` | logs | on | `veloxagent-events.ebpf-v1` | Kernel events with `process.pid`, `process.name` and trace-specific fields |

## Fields

`trace` (required, repeatable; default `trace_signal`) and advanced `poll_ms`. `delete_after` (default 90d).

Indexed fields: `@timestamp`, `event.kind`, `event.module`, `process.pid`, `process.name`, plus the trace-specific numbers dynamically mapped, `velox.*`.

## Requirements

- Linux with eBPF support and a Fluent Bit build that includes the `ebpf` input.
- The agent must run as root (or with `CAP_BPF`/`CAP_SYS_ADMIN`).

## Notes

Experimental: field names depend on the trace program and may change.
