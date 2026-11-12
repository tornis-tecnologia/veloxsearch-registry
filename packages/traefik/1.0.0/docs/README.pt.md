# Traefik

Logs de acesso do Traefik com router, serviço e duração, e o log do próprio Traefik.

## Streams

| Stream | Sinal | Padrão | Índice / destino | O que coleta |
| --- | --- | --- | --- | --- |
| `access` | logs | ligado | `veloxagent-access.traefik-v1` | `/var/log/traefik/access.log` (common log format) |
| `app` | logs | ligado | `veloxagent-app.traefik-v1` | `/var/log/traefik/traefik.log` (console com cores, ou logfmt) |

## Campos

`access`: os campos HTTP ECS do pacote nginx (`client.ip`, `http.request.method`, `url.original`, `http.response.status_code`, `http.response.body.bytes`, `user_agent.*`, ...) mais `traefik.router`, `traefik.service`, `traefik.request_count`, `traefik.duration_ms` e `event.duration` (nanossegundos).

`app`: `@timestamp`, `log.level` (`info`, `warning`, `error`, ...), `message` e, em linhas logfmt, `traefik.app.routerName`, `traefik.app.serviceName`, `traefik.app.entryPointName`, `traefik.app.providerName`.

## Requisitos

- Linux. O usuário do agente deve ler `/var/log/traefik/`.
- Ative o log em arquivo no Traefik: `accessLog.filePath: /var/log/traefik/access.log` (formato common, o padrão) e `log.filePath: /var/log/traefik/traefik.log`.

## Dashboard

*Traefik — overview*: requisições, clientes únicos, erros (4xx/5xx), requisições por status ao longo do tempo, códigos de status, routers, URLs e clientes mais frequentes.
