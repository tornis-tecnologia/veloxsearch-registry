# Nginx

Logs de acceso y de errores de nginx separados en campos ECS, y métricas opcionales de stub_status.

## Streams

| Stream | Señal | Por defecto | Índice / destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `access` | logs | activo | `veloxagent-access.nginx-v1` | `/var/log/nginx/access.log` y `*access*.log` (formato combined) |
| `error` | logs | activo | `veloxagent-error.nginx-v1` | `/var/log/nginx/error.log` |
| `metrics` | metrics | inactivo | OTLP endpoint of the policy | conexiones, accepted/handled y peticiones de `stub_status` |

## Campos

`access`: `@timestamp`, `client.ip`, `user.name`, `http.request.method`, `url.original`, `http.version`, `http.response.status_code`, `http.response.body.bytes`, `http.request.referrer`, `user_agent.original` (más `user_agent.name`, `user_agent.os.name`, `user_agent.device.name` con `parse_user_agent` activo), `nginx.access.ident`, `nginx.access.raw_request` (peticiones malformadas), `event.category`, `event.outcome` (`unparsed` en líneas que no coinciden), `velox.*`.

`error`: `@timestamp`, `log.level`, `process.pid`, `process.thread.id`, `nginx.error.connection_id`, `message` y, cuando existen, `client.ip`, `nginx.error.server`, `nginx.error.upstream`, `nginx.error.host`, `http.request.method`, `url.original`, `http.version`, `http.request.referrer`. error.log no trae zona horaria: configure `timezone` si el host no usa UTC.

Los nombres cambiaron respecto de 1.x (`clientip` ahora es `client.ip`, `response` es `http.response.status_code`, `bytes` es `http.response.body.bytes`, `request` es `url.original`).

## Requisitos

- Linux. El usuario del agente debe leer `/var/log/nginx/` (normalmente grupo `adm`).
- `access` espera el formato de log `combined` por defecto.
- `metrics` necesita `stub_status` expuesto en un location (por ejemplo `location /status { stub_status; allow 127.0.0.1; deny all; }`) y un endpoint OTLP en la política (deployment con el stack OTel).

## Dashboard

*Nginx — overview*: peticiones, clientes únicos, errores (4xx/5xx) y peticiones por estado en el tiempo, códigos de estado, tráfico en bytes, URLs, clientes y user agents más frecuentes.
