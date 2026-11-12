# MySQL / MariaDB

MySQL and MariaDB server logs, collected by Velox Agent.

## Streams

| Stream | Signal | Default | Index / destination | What it collects |
| --- | --- | --- | --- | --- |
| `error` | logs | on | `veloxagent-error.mysql-v1` | error log of MySQL 5.7/8.x and MariaDB: level, thread, error code, subsystem |
| `slowlog` | logs | off | `veloxagent-slowlog.mysql-v1` | slow query log, one event per entry: user, host, query time, lock time, rows, query |

## Fields

`error`: `@timestamp`, `message`, `log.level` (`note`/`system` → `info`), `mysql.thread_id`, `mysql.error_code`, `mysql.subsystem`. `slowlog`: `@timestamp`, `message` (the query), `user.name`, `source.address`, `source.ip`, `event.duration` (ns), `mysql.slowlog.lock_time` (seconds), `mysql.slowlog.rows_sent`, `mysql.slowlog.rows_examined`, `mysql.slowlog.query`. Both: `event.outcome` (`unparsed`), `velox.*`.

## Requirements

- Linux. The agent user must read the log files. For `slowlog` set `slow_query_log=ON`, `slow_query_log_file` and `long_query_time` on the server.

## Dashboard

*MySQL / MariaDB — overview*: events, errors over time, volume by level, levels, subsystems, top messages and slow queries over time.
