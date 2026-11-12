# HTTP endpoint

Receives JSON events posted to an HTTP endpoint on the agent.

## Streams

| Stream | Signal | Default | Index | What it receives |
| --- | --- | --- | --- | --- |
| `json` | logs | on | `veloxagent-json.http-endpoint-v1` | POST bodies with a JSON object or a list of objects, on port 8888 |

## Fields

`@timestamp`, `message`, every key the sender includes (strings are mapped as keyword), `source.address` (when `Record the client address` is on), `velox.*`.

The event time comes from `time`, then `timestamp`, then `@timestamp` when it is a string (ISO 8601, `yyyy-MM-dd HH:mm:ss`, access-log style, epoch seconds or milliseconds); a value that cannot be parsed stays as sent and the event keeps its arrival time. The `timezone` field applies to times without an offset.

Try it: `curl -X POST http://localhost:8888/ -H 'Content-Type: application/json' -d '{"time":"2026-11-12T10:15:02Z","level":"info","message":"hello"}'`.

## Requirements

- Open the port in the host firewall. The listener speaks plain HTTP: put it behind a TLS proxy when it faces an untrusted network, or require an OAuth 2.0 token (JWKS) in the advanced fields.
- The Fluent Bit catalogue lists no TLS or basic-auth keys for this input, so the package does not expose them.
- The tag-from-record option (`tag_key`) is not offered: it would re-route events away from the stream's index.

## Dashboard

*HTTP endpoint — overview*: events over time, events by level, top hosts and top client addresses.
