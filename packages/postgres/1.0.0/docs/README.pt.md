# PostgreSQL

Log do servidor PostgreSQL, coletado pelo Velox Agent.

## Streams

| Stream | Sinal | Padrão | Índice / destino | O que coleta |
| --- | --- | --- | --- | --- |
| `log` | logs | ligado | `veloxagent-log.postgres-v1` | arquivos de `log_directory`, comandos multilinha juntados; nível, pid, usuário, banco, duração e eventos de conexão |

## Campos

`@timestamp`, `message`, `log.level` (minúsculas; `debug1..5` → `debug`), `process.pid`, `user.name`, `postgres.database`, `postgres.statement`, `event.duration` (ns, de `duration: … ms`), `event.action` (`connection-received`, `connection-authorized`, `disconnection`), `source.ip`, `source.port`, `event.outcome` (`unparsed`), `velox.*`.

## Requisitos

- Linux. Ative `logging_collector = on` e `log_line_prefix = '%m [%p] %q%u@%d '`; use `log_min_duration_statement` e `log_connections` para durações e conexões. O usuário do agente deve ler os arquivos de log (grupo `postgres` ou `adm`).

## Dashboard

*PostgreSQL — visão geral*: eventos, erros ao longo do tempo, volume por nível, níveis, mensagens mais frequentes, bancos e usuários.
