# Nginx

Access and error logs of nginx parsed into ECS fields, and optional stub_status metrics.

## Streams

| Stream | Signal | Default | Index / destination | What it collects |
| --- | --- | --- | --- | --- |
| `access` | logs | on | `veloxagent-access.nginx-v1` | `/var/log/nginx/access.log` and `*access*.log` (combined format) |
| `error` | logs | on | `veloxagent-error.nginx-v1` | `/var/log/nginx/error.log` |
| `metrics` | metrics | off | OTLP endpoint of the policy | connections, accepted/handled and requests from `stub_status` |

## Fields

`access`: `@timestamp`, `client.ip`, `user.name`, `http.request.method`, `url.original`, `http.version`, `http.response.status_code`, `http.response.body.bytes`, `http.request.referrer`, `user_agent.original` (plus `user_agent.name`, `user_agent.os.name`, `user_agent.device.name` when `parse_user_agent` is on), `nginx.access.ident`, `nginx.access.raw_request` (malformed requests), `event.category`, `event.outcome` (`unparsed` for lines that do not match), `velox.*`.

`error`: `@timestamp`, `log.level`, `process.pid`, `process.thread.id`, `nginx.error.connection_id`, `message`, and when present `client.ip`, `nginx.error.server`, `nginx.error.upstream`, `nginx.error.host`, `http.request.method`, `url.original`, `http.version`, `http.request.referrer`. error.log has no time zone: set the `timezone` field if the host does not run in UTC.

The field names changed from 1.x (`clientip` is now `client.ip`, `response` is `http.response.status_code`, `bytes` is `http.response.body.bytes`, `request` is `url.original`).

## Requirements

- Linux. The agent user must read `/var/log/nginx/` (usually group `adm`).
- `access` expects the default `combined` log format.
- `metrics` needs `stub_status` exposed on a location (for example `location /status { stub_status; allow 127.0.0.1; deny all; }`) and an OTLP endpoint on the policy (deployment with the OTel stack).

## Dashboard

*Nginx — overview*: requests, unique clients, errors (4xx/5xx) and requests by status over time, status codes, traffic in bytes, top URLs, top clients and top user agents.
