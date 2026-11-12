# Kubernetes events

Kubernetes API events (scheduling, image pulls, back-offs, node conditions) as searchable logs.

## Streams

| Stream | Signal | Default | Destination | What it collects |
| --- | --- | --- | --- | --- |
| `events` | logs | on | `veloxagent-events.kubernetes-events-v1` | `kubernetes.event.reason`, `.type`, `.message`, `.count`, `.involved_object.*` |

## Fields

`kube_url`, `kube_namespace` (empty = all), `tls_verify`, and advanced `kube_token_file`, `kube_ca_file`, `kube_retention_time`, `interval_sec` and `interval_nsec`. The checkpoint database is fixed under the agent state directory. `delete_after` (default 14d).

Indexed fields: `@timestamp` (from `lastTimestamp`), `message`, `kubernetes.event.reason`, `.type` (Normal/Warning), `.message`, `.count`, `.action`, `.first_timestamp`, `.involved_object.kind|name|namespace|uid`, `.source.component|host`, `velox.*`. A record without a reason gets `event.outcome: unparsed`.

## Requirements

- Reachability of the Kubernetes API server (`kube_api`), normally from inside the cluster with a service account token.
- RBAC: `get`, `list` and `watch` on `events`. Run one agent per cluster, otherwise events are duplicated.

## Dashboard

*Kubernetes — events*: events over time by type, top reasons, top namespaces and the objects with the most warnings.
