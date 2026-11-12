# MQTT

An MQTT listener: devices and gateways publish to the agent, which indexes each message with its topic and payload.

## Streams

| Stream | Signal | Default | Index / destination | What it collects |
| --- | --- | --- | --- | --- |
| `messages` | logs | on | `veloxagent-messages.mqtt-v1` | MQTT messages published to TCP 1883 |

## Fields

`@timestamp`, `mqtt.topic`, `mqtt.payload.*` (JSON object payloads), `message` (any other payload kept as text), `event.outcome` (`unparsed` when a payload looks like JSON but is malformed), `velox.*`.

## Requirements

- Clients must reach the port (default 1883); the agent needs permission to listen.
- The input does not implement authentication or TLS: keep it on a trusted network.

## Dashboard

*MQTT — overview*: messages over time by topic, top topics and messages by outcome.
