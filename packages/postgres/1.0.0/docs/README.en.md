# PostgreSQL

PostgreSQL server log, collected by Velox Agent.

## Streams

| Stream | Signal | Default | Index / destination | What it collects |
| --- | --- | --- | --- | --- |
| `log` | logs | on | `veloxagent-log.postgres-v1` | `log_directory` files, multi-line statements joined; level, pid, user, database, duration and connection events parsed |

## Fields

`@timestamp`, `message`, `log.level` (lowercase; `debug1..5` → `debug`), `process.pid`, `user.name`, `postgres.database`, `postgres.statement`, `event.duration` (ns, from `duration: … ms`), `event.action` (`connection-received`, `connection-authorized`, `disconnection`), `source.ip`, `source.port`, `event.outcome` (`unparsed`), `velox.*`.

## Requirements

- Linux. Set `logging_collector = on` and `log_line_prefix = '%m [%p] %q%u@%d '`; use `log_min_duration_statement` and `log_connections` for durations and connections. The agent user must read the log files (group `postgres` or `adm`).

## Dashboard

*PostgreSQL — overview*: events, errors over time, volume by level, levels, top messages, databases and users.
