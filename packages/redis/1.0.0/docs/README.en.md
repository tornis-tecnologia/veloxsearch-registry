# Redis

Redis server logs collected by Velox Agent from the log files on the host.

## Streams

| Stream | Signal | Default | Index | What it collects |
| --- | --- | --- | --- | --- |
| `log` | logs | on | `veloxagent-log.redis-v1` | `/var/log/redis/redis-server.log`, `/var/log/redis/*.log`: one event per line |

## Fields

`@timestamp` (the log's own time, with or without year), `message`, `process.pid`, `redis.role` (`master`, `replica`, `child`, `sentinel`), `log.level` (`debug`, `verbose`, `notice`, `warning`), `event.outcome` (`unparsed` when a line has no Redis shape), `velox.*`.

## Requirements

- Linux. The agent user must be able to read the Redis log files (log to a file with `logfile /var/log/redis/redis-server.log`; Redis logs to stdout by default).

## Dashboard

*Redis — overview*: log volume, warnings over time, volume by role, level and role breakdowns, top messages.
