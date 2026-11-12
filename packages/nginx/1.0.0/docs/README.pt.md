# Nginx

Logs de acesso e de erros do nginx separados em campos ECS, e métricas opcionais do stub_status.

## Streams

| Stream | Sinal | Padrão | Índice / destino | O que coleta |
| --- | --- | --- | --- | --- |
| `access` | logs | ligado | `veloxagent-access.nginx-v1` | `/var/log/nginx/access.log` e `*access*.log` (formato combined) |
| `error` | logs | ligado | `veloxagent-error.nginx-v1` | `/var/log/nginx/error.log` |
| `metrics` | metrics | desligado | OTLP endpoint of the policy | conexões, accepted/handled e requisições do `stub_status` |

## Campos

`access`: `@timestamp`, `client.ip`, `user.name`, `http.request.method`, `url.original`, `http.version`, `http.response.status_code`, `http.response.body.bytes`, `http.request.referrer`, `user_agent.original` (mais `user_agent.name`, `user_agent.os.name`, `user_agent.device.name` com `parse_user_agent` ligado), `nginx.access.ident`, `nginx.access.raw_request` (requisições malformadas), `event.category`, `event.outcome` (`unparsed` em linhas que não casam), `velox.*`.

`error`: `@timestamp`, `log.level`, `process.pid`, `process.thread.id`, `nginx.error.connection_id`, `message` e, quando existem, `client.ip`, `nginx.error.server`, `nginx.error.upstream`, `nginx.error.host`, `http.request.method`, `url.original`, `http.version`, `http.request.referrer`. O error.log não traz fuso horário: configure `timezone` se o host não usa UTC.

Os nomes mudaram em relação ao 1.x (`clientip` agora é `client.ip`, `response` é `http.response.status_code`, `bytes` é `http.response.body.bytes`, `request` é `url.original`).

## Requisitos

- Linux. O usuário do agente deve ler `/var/log/nginx/` (normalmente grupo `adm`).
- `access` espera o formato de log `combined` padrão.
- `metrics` precisa do `stub_status` exposto em um location (por exemplo `location /status { stub_status; allow 127.0.0.1; deny all; }`) e de um endpoint OTLP na política (deployment com o stack OTel).

## Dashboard

*Nginx — overview*: requisições, clientes únicos, erros (4xx/5xx) e requisições por status ao longo do tempo, códigos de status, tráfego em bytes, URLs, clientes e user agents mais frequentes.
