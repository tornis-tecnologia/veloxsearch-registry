# Consumidor Kafka

Suscribe el agente a topics de Kafka como consumidor e indexa cada mensaje con sus coordenadas de Kafka.

## Streams

| Stream | Señal | Por defecto | Índice / destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `messages` | logs | activado | `veloxagent-messages.kafka-consumer-v1` | Mensajes de los topics Kafka elegidos (define brokers y topics antes de usar) |

## Campos

`@timestamp`, `kafka.topic`, `kafka.partition`, `kafka.offset`, `kafka.key`, `kafka.payload.*` (cargas que son objetos JSON), `message` (cualquier otra carga como texto), `event.outcome` (`unparsed` cuando la carga parece JSON pero está mal formada), `velox.*`.

La autenticación (SASL/TLS) se configura con el campo avanzado `Propiedades de librdkafka` mediante claves `rdkafka.*`; el input Kafka de Fluent Bit no tiene claves dedicadas de usuario/contraseña.

## Requisitos

- Acceso de red del agente a los brokers Kafka.
- Un grupo de consumidores (`group_id`) con permiso de lectura en los topics.

## Dashboard

*Kafka consumer — overview*: mensajes por topic en el tiempo, topics principales, mensajes por partición y por resultado.
