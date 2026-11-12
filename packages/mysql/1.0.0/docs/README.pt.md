# MySQL / MariaDB

Logs de servidores MySQL e MariaDB, coletados pelo Velox Agent.

## Streams

| Stream | Sinal | Padrão | Índice / destino | O que coleta |
| --- | --- | --- | --- | --- |
| `error` | logs | ligado | `veloxagent-error.mysql-v1` | log de erros do MySQL 5.7/8.x e MariaDB: nível, thread, código de erro, subsistema |
| `slowlog` | logs | desligado | `veloxagent-slowlog.mysql-v1` | log de consultas lentas, um evento por entrada: usuário, host, tempo, lock, linhas, consulta |

## Campos

`error`: `@timestamp`, `message`, `log.level` (`note`/`system` → `info`), `mysql.thread_id`, `mysql.error_code`, `mysql.subsystem`. `slowlog`: `@timestamp`, `message` (a consulta), `user.name`, `source.address`, `source.ip`, `event.duration` (ns), `mysql.slowlog.lock_time` (segundos), `mysql.slowlog.rows_sent`, `mysql.slowlog.rows_examined`, `mysql.slowlog.query`. Ambos: `event.outcome` (`unparsed`), `velox.*`.

## Requisitos

- Linux. O usuário do agente deve ler os arquivos de log. Para `slowlog` defina `slow_query_log=ON`, `slow_query_log_file` e `long_query_time` no servidor.

## Dashboard

*MySQL / MariaDB — visão geral*: eventos, erros ao longo do tempo, volume por nível, níveis, subsistemas, mensagens mais frequentes e consultas lentas ao longo do tempo.
