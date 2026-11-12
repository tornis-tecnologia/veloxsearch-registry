# collectd

Receive collectd network-protocol metrics from collectd daemons.

## Streams

| Stream | Signal | Default | Destination | What it collects |
| --- | --- | --- | --- | --- |
| `metrics` | metrics | on | `veloxagent-metrics.collectd-v1` | `host`, `plugin`, `plugin_instance`, `type`, `type_instance`, `values` |

## Fields

`listen` (default `0.0.0.0`), `port` (UDP, default 25826), `typesdb` (advanced, default `/usr/share/collectd/types.db`; several paths allowed) and `delete_after` (default 14d).

Indexed fields: `@timestamp`, `host`, `plugin`, `plugin_instance`, `type`, `type_instance`, `dsnames`, `dstypes`, `values`, `interval`, `velox.*`.

## Requirements

- Linux. A collectd daemon with the `network` write plugin pointing at the agent.
- The `types.db` file must exist on the host running the agent.
