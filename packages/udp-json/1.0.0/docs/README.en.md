# UDP JSON

Opens a UDP listener for senders that fire and forget. Choose JSON objects (one event each, with the time taken from the object) or plain lines.

## Streams

| Stream | Signal | Default | Index | What it receives |
| --- | --- | --- | --- | --- |
| `json` | logs | on | `veloxagent-json.udp-json-v1` | JSON objects on UDP 5170 (all interfaces) |
| `raw` | logs | off | `veloxagent-raw.udp-json-v1` | plain text lines on UDP 5171 |

## Fields

`@timestamp`, `message` and every key the sender includes (strings are mapped as keyword, so `level`, `host`, `service` can be aggregated), `velox.*`.

`json` takes the event time from `time`, then `timestamp`, then `@timestamp` when it is a string (ISO 8601, `yyyy-MM-dd HH:mm:ss`, access-log style, epoch seconds or milliseconds); the source key is removed once parsed. A value that cannot be parsed stays as sent and the event keeps its arrival time. The `timezone` field applies to times without an offset.

`raw` stores each line in `message`; the time is the arrival time.

Try it: `echo '{"time":"2026-11-12T10:15:02Z","level":"info","message":"hello"}' | nc -u -w1 localhost 5170`; raw: `echo "a plain line" | nc -u -w1 localhost 5171`.

## Requirements

- Open the port in the host firewall; the `json` and `raw` streams use different ports so they can run together.
- `json` needs one complete JSON object per message; a stream of concatenated objects is fine over TCP.
- UDP has no delivery guarantee and one datagram must fit in the buffer: raise `Max buffer size` for large objects.

## Dashboard

*UDP JSON — overview*: events over time, events by level and top hosts (reads the `json` stream).
