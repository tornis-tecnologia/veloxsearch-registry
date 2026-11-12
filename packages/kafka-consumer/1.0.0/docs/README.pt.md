# Consumidor Kafka

Inscreve o agente em tópicos do Kafka como consumidor e indexa cada mensagem com suas coordenadas do Kafka.

## Streams

| Stream | Sinal | Padrão | Índice / destino | O que coleta |
| --- | --- | --- | --- | --- |
| `messages` | logs | ligado | `veloxagent-messages.kafka-consumer-v1` | Mensagens dos tópicos Kafka escolhidos (defina brokers e tópicos antes de usar) |

## Campos

`@timestamp`, `kafka.topic`, `kafka.partition`, `kafka.offset`, `kafka.key`, `kafka.payload.*` (cargas que são objetos JSON), `message` (qualquer outra carga como texto), `event.outcome` (`unparsed` quando a carga parece JSON mas está malformada), `velox.*`.

A autenticação (SASL/TLS) é configurada pelo campo avançado `Propriedades do librdkafka` com chaves `rdkafka.*`; o input Kafka do Fluent Bit não tem chaves dedicadas de usuário/senha.

## Requisitos

- Acesso de rede do agente aos brokers Kafka.
- Um grupo de consumidores (`group_id`) com permissão de leitura nos tópicos.

## Dashboard

*Kafka consumer — overview*: mensagens por tópico ao longo do tempo, tópicos principais, mensagens por partição e por resultado.
