# RabbitMQ

Logs do nó RabbitMQ coletados pelo Velox Agent a partir dos arquivos de log do host.

## Streams

| Stream | Sinal | Padrão | Índice | O que coleta |
| --- | --- | --- | --- | --- |
| `log` | logs | sim | `veloxagent-log.rabbitmq-v1` | `/var/log/rabbitmq/*.log`: um evento por entrada; linhas de continuação (crash reports) são juntadas à entrada anterior |

## Campos

`@timestamp`, `message`, `log.level` (`debug`, `info`, `notice`, `warning`, `error`, `critical`), `rabbitmq.pid` (pid do Erlang, ex.: `0.123.0`) e, em mensagens de conexão, `source.ip`, `source.port` e `user.name`. Códigos de cor ANSI são removidos antes do parse. `event.outcome` é `unparsed` quando a linha não tem formato RabbitMQ; `velox.*`.

## Requisitos

- Linux. O usuário do agente deve ler `/var/log/rabbitmq/*.log`. O campo `multiline` escolhe como as linhas de continuação são juntadas (padrão: o parser Erlang do pacote).

## Dashboard

*RabbitMQ — visão geral*: volume de logs, erros ao longo do tempo, volume por nível, quebra por nível, mensagens mais frequentes.
