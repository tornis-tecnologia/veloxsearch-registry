# Splunk HEC receiver

An HEC-compatible HTTP endpoint: Splunk forwarders, apps and scripts that send to a HEC URL can send to the agent instead.

## Streams

| Stream | Signal | Default | Index / destination | What it collects |
| --- | --- | --- | --- | --- |
| `events` | logs | on | `veloxagent-events.splunk-hec-v1` | HEC events posted to HTTP 8088 |

## Fields

`@timestamp` (from `time`, epoch seconds), `host.name`, `message` (string events), `splunk.event.*` (object events), `splunk.source`, `splunk.sourcetype`, `splunk.index`, `splunk.fields.*`, `velox.*`.

## Requirements

- Clients must reach the port (default 8088); the agent needs permission to listen.
- Set a HEC token: without it the endpoint accepts any request. The Fluent Bit input has no TLS keys; terminate TLS in front of the agent if needed.

## Dashboard

*Splunk HEC — overview*: events over time by sourcetype, top hosts, sources and indexes.
