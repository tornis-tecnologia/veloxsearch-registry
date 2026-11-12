# Apache Kafka

Apache Kafka broker logs collected by Velox Agent from the log files on the host.

## Streams

| Stream | Signal | Default | Index | What it collects |
| --- | --- | --- | --- | --- |
| `server` | logs | on | `veloxagent-server.kafka-v1` | `server.log`: broker log; Java stack traces are joined into one event |
| `controller` | logs | off | `veloxagent-controller.kafka-v1` | `controller.log`: controller activity |
| `state_change` | logs | off | `veloxagent-state_change.kafka-v1` | `state-change.log`: partition and replica transitions |

## Fields

`@timestamp`, `message`, `log.level` (`trace`, `debug`, `info`, `warn`, `error`, `fatal`), `kafka.logger` (class in parentheses, e.g. `kafka.controller.KafkaController`), `kafka.context` (bracketed context, e.g. `Controller id=1`), `error.stack_trace` (when a Java stack trace follows the entry), `event.outcome` (`unparsed` when a line has no log4j shape), `velox.*`.

## Requirements

- Linux. The agent user must read the Kafka log directory (`/var/log/kafka` or `<kafka>/logs`). The `multiline` field picks the stack-trace joiner: the package parser or Fluent Bit's built-in `java`.

## Dashboard

*Kafka — overview* (stream `server`): log volume, errors over time, volume by level, level breakdown, top loggers, top messages.
