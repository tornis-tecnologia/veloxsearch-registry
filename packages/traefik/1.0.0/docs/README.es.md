# Traefik

Logs de acceso de Traefik con router, servicio y duración, y el log propio de Traefik.

## Streams

| Stream | Señal | Por defecto | Índice / destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `access` | logs | activo | `veloxagent-access.traefik-v1` | `/var/log/traefik/access.log` (formato common log) |
| `app` | logs | activo | `veloxagent-app.traefik-v1` | `/var/log/traefik/traefik.log` (consola con colores, o logfmt) |

## Campos

`access`: los campos HTTP ECS del paquete nginx (`client.ip`, `http.request.method`, `url.original`, `http.response.status_code`, `http.response.body.bytes`, `user_agent.*`, ...) más `traefik.router`, `traefik.service`, `traefik.request_count`, `traefik.duration_ms` y `event.duration` (nanosegundos).

`app`: `@timestamp`, `log.level` (`info`, `warning`, `error`, ...), `message` y, en líneas logfmt, `traefik.app.routerName`, `traefik.app.serviceName`, `traefik.app.entryPointName`, `traefik.app.providerName`.

## Requisitos

- Linux. El usuario del agente debe leer `/var/log/traefik/`.
- Active el log en archivo en Traefik: `accessLog.filePath: /var/log/traefik/access.log` (formato common, el predeterminado) y `log.filePath: /var/log/traefik/traefik.log`.

## Dashboard

*Traefik — overview*: peticiones, clientes únicos, errores (4xx/5xx), peticiones por estado en el tiempo, códigos de estado, routers, URLs y clientes más frecuentes.
