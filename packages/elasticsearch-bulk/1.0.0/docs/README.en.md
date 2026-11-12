# Elasticsearch bulk receiver

A Bulk API endpoint for Beats, Logstash and any client that speaks the Elasticsearch bulk protocol; events are indexed in OpenSearch through the agent.

## Streams

| Stream | Signal | Default | Index / destination | What it collects |
| --- | --- | --- | --- | --- |
| `bulk` | logs | on | `veloxagent-bulk.elasticsearch-bulk-v1` | Bulk API documents posted to HTTP 9201 |

## Fields

`@timestamp` (kept; normalized to UTC ISO-8601, ingest time if missing or invalid), `host.name` (from a string `host`, `hostname` or `agent.hostname`), `bulk.meta.*` (bulk action metadata), `event.outcome` (`unparsed` for an invalid timestamp), `velox.*`. All other fields are kept.

## Requirements

- Point Beats/Logstash at `http://<agent>:9201`; the agent needs permission to listen.
- The endpoint has no authentication: keep it on a trusted network. Beats may need `setup.ilm.enabled: false` and `setup.template.enabled: false`.

## Dashboard

*Elasticsearch bulk — overview*: events over time by host, top hosts, shipper types and events by outcome.
