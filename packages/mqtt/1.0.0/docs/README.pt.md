# MQTT

Um listener MQTT: dispositivos e gateways publicam no agente, que indexa cada mensagem com seu tópico e sua carga.

## Streams

| Stream | Sinal | Padrão | Índice / destino | O que coleta |
| --- | --- | --- | --- | --- |
| `messages` | logs | ligado | `veloxagent-messages.mqtt-v1` | Mensagens MQTT publicadas na TCP 1883 |

## Campos

`@timestamp`, `mqtt.topic`, `mqtt.payload.*` (cargas que são objetos JSON), `message` (qualquer outra carga como texto), `event.outcome` (`unparsed` quando a carga parece JSON mas está malformada), `velox.*`.

## Requisitos

- Os clientes devem alcançar a porta (1883 por padrão); o agente precisa de permissão para escutar.
- O input não implementa autenticação nem TLS: mantenha-o em uma rede confiável.

## Dashboard

*MQTT — overview*: mensagens ao longo do tempo por tópico, tópicos principais e mensagens por resultado.
