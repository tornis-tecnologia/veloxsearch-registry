# Kafka consumer

Subscribes the agent to Kafka topics as a consumer and indexes every message with its Kafka coordinates.

## Streams

| Stream | Signal | Default | Index / destination | What it collects |
| --- | --- | --- | --- | --- |
| `messages` | logs | on | `veloxagent-messages.kafka-consumer-v1` | Messages of the chosen Kafka topics (set brokers and topics before use) |

## Fields

`@timestamp`, `kafka.topic`, `kafka.partition`, `kafka.offset`, `kafka.key`, `kafka.payload.*` (JSON object payloads), `message` (any other payload as text), `event.outcome` (`unparsed` when a payload looks like JSON but is malformed), `velox.*`.

Authentication (SASL/TLS) is configured through the advanced `librdkafka properties` field using `rdkafka.*` keys; the Fluent Bit Kafka input has no dedicated username/password keys.

## Requirements

- Network access from the agent to the Kafka brokers.
- A consumer group (`group_id`) with read permission on the topics.

## Dashboard

*Kafka consumer — overview*: messages by topic over time, top topics, messages by partition and by outcome.
