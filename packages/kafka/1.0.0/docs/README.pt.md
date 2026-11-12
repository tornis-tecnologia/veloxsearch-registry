# Apache Kafka

Logs do broker Apache Kafka coletados pelo Velox Agent a partir dos arquivos de log do host.

## Streams

| Stream | Sinal | Padrão | Índice | O que coleta |
| --- | --- | --- | --- | --- |
| `server` | logs | sim | `veloxagent-server.kafka-v1` | `server.log`: log do broker; stack traces Java são juntados em um evento |
| `controller` | logs | não | `veloxagent-controller.kafka-v1` | `controller.log`: atividade do controller |
| `state_change` | logs | não | `veloxagent-state_change.kafka-v1` | `state-change.log`: transições de partições e réplicas |

## Campos

`@timestamp`, `message`, `log.level` (`trace`, `debug`, `info`, `warn`, `error`, `fatal`), `kafka.logger` (classe entre parênteses, ex.: `kafka.controller.KafkaController`), `kafka.context` (contexto entre colchetes, ex.: `Controller id=1`), `error.stack_trace` (quando um stack trace Java segue a entrada), `event.outcome` (`unparsed` quando a linha não tem formato log4j), `velox.*`.

## Requisitos

- Linux. O usuário do agente deve ler o diretório de logs do Kafka (`/var/log/kafka` ou `<kafka>/logs`). O campo `multiline` escolhe como juntar stack traces: o parser do pacote ou o `java` embutido do Fluent Bit.

## Dashboard

*Kafka — visão geral* (stream `server`): volume de logs, erros ao longo do tempo, volume por nível, quebra por nível, loggers e mensagens mais frequentes.
