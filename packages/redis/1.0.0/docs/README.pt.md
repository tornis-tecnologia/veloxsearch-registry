# Redis

Logs do servidor Redis coletados pelo Velox Agent a partir dos arquivos de log do host.

## Streams

| Stream | Sinal | Padrão | Índice | O que coleta |
| --- | --- | --- | --- | --- |
| `log` | logs | sim | `veloxagent-log.redis-v1` | `/var/log/redis/redis-server.log`, `/var/log/redis/*.log`: um evento por linha |

## Campos

`@timestamp` (a hora do próprio log, com ou sem ano), `message`, `process.pid`, `redis.role` (`master`, `replica`, `child`, `sentinel`), `log.level` (`debug`, `verbose`, `notice`, `warning`), `event.outcome` (`unparsed` quando a linha não tem formato Redis), `velox.*`.

## Requisitos

- Linux. O usuário do agente deve ler os logs do Redis (configure `logfile /var/log/redis/redis-server.log`; por padrão o Redis escreve em stdout).

## Dashboard

*Redis — visão geral*: volume de logs, avisos ao longo do tempo, volume por papel, quebras por nível e papel, mensagens mais frequentes.
