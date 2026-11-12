# Custom logs

Reads any log file on the host with the Fluent Bit `tail` input and indexes each
line into `veloxagent-log.custom-logs-v1`.

## Streams

| Stream | Signal | What it collects |
| --- | --- | --- |
| `log` | logs | Lines of the files matched by **Paths** |

## Configuration

- **Paths** — files to read, wildcards allowed (default `/var/log/*.log`).
- **Exclude paths**, **Read from head**, **Refresh interval** — advanced.
- **Multiline** — built-in Fluent Bit multiline parser for stack traces.
- **Parser** — `json` or `logfmt` to split the line into fields.
- **Exclusion rules** — drop records whose field matches a regex.
- **Backend** — replicas, keep the original line, retention.

Example package of the registry Spec 2.0 (docs/spec/README.md).
