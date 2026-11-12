# Traefik

Traefik access logs with router, service and duration, and Traefik's own log.

## Streams

| Stream | Signal | Default | Index / destination | What it collects |
| --- | --- | --- | --- | --- |
| `access` | logs | on | `veloxagent-access.traefik-v1` | `/var/log/traefik/access.log` (common log format) |
| `app` | logs | on | `veloxagent-app.traefik-v1` | `/var/log/traefik/traefik.log` (console with colours, or logfmt) |

## Fields

`access`: the ECS HTTP fields of the nginx package (`client.ip`, `http.request.method`, `url.original`, `http.response.status_code`, `http.response.body.bytes`, `user_agent.*`, ...) plus `traefik.router`, `traefik.service`, `traefik.request_count`, `traefik.duration_ms` and `event.duration` (nanoseconds).

`app`: `@timestamp`, `log.level` (`info`, `warning`, `error`, ...), `message`, and for logfmt lines `traefik.app.routerName`, `traefik.app.serviceName`, `traefik.app.entryPointName`, `traefik.app.providerName`.

## Requirements

- Linux. The agent user must read `/var/log/traefik/`.
- Enable file logging in Traefik: `accessLog.filePath: /var/log/traefik/access.log` (common format, the default) and `log.filePath: /var/log/traefik/traefik.log`.

## Dashboard

*Traefik — overview*: requests, unique clients, errors (4xx/5xx), requests by status over time, status codes, top routers, top URLs and top clients.
