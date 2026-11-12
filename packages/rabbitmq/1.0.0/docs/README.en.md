# RabbitMQ

RabbitMQ node logs collected by Velox Agent from the log files on the host.

## Streams

| Stream | Signal | Default | Index | What it collects |
| --- | --- | --- | --- | --- |
| `log` | logs | on | `veloxagent-log.rabbitmq-v1` | `/var/log/rabbitmq/*.log`: one event per entry; continuation lines (crash reports) are joined to the entry above |

## Fields

`@timestamp`, `message`, `log.level` (`debug`, `info`, `notice`, `warning`, `error`, `critical`), `rabbitmq.pid` (Erlang pid, e.g. `0.123.0`), and for connection messages `source.ip`, `source.port` and `user.name`. ANSI colour codes are stripped before parsing. `event.outcome` is `unparsed` when a line has no RabbitMQ shape; `velox.*`.

## Requirements

- Linux. The agent user must read `/var/log/rabbitmq/*.log`. The `multiline` field chooses how continuation lines are joined (default: the package's Erlang parser).

## Dashboard

*RabbitMQ — overview*: log volume, errors over time, volume by level, level breakdown, top messages.
