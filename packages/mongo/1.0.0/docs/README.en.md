# MongoDB

MongoDB server log, collected by Velox Agent.

## Streams

| Stream | Signal | Default | Index / destination | What it collects |
| --- | --- | --- | --- | --- |
| `log` | logs | on | `veloxagent-log.mongo-v1` | `mongod.log`: JSON lines (4.4+) with severity, component, context, message and `attr`; legacy text lines as fallback |

## Fields

`@timestamp`, `message`, `log.level` (`F`→`fatal`, `E`→`error`, `W`→`warning`, `I`→`info`, `D1..5`→`debug`), `mongo.component`, `mongo.context`, `mongo.id`, `mongo.attr` (`flat_object`, searchable by dotted path), `event.duration` (ns, from `attr.durationMillis`), `event.outcome` (`unparsed`), `velox.*`.

## Requirements

- Linux. `systemLog.destination: file` with `systemLog.path`; the agent user must read the file (group `mongodb` or `adm`). Slow queries appear with `operationProfiling.slowOpThresholdMs`. `mongo.attr` needs OpenSearch 2.7+ (`flat_object`).

## Dashboard

*MongoDB — overview*: events, errors over time, volume by severity, severity, components and top messages.
