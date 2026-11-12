# MQTT

Un listener MQTT: dispositivos y gateways publican al agente, que indexa cada mensaje con su topic y su carga.

## Streams

| Stream | Señal | Por defecto | Índice / destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `messages` | logs | activado | `veloxagent-messages.mqtt-v1` | Mensajes MQTT publicados en el TCP 1883 |

## Campos

`@timestamp`, `mqtt.topic`, `mqtt.payload.*` (cargas que son objetos JSON), `message` (cualquier otra carga como texto), `event.outcome` (`unparsed` cuando la carga parece JSON pero está mal formada), `velox.*`.

## Requisitos

- Los clientes deben alcanzar el puerto (1883 por defecto); el agente necesita permiso para escuchar.
- El input no implementa autenticación ni TLS: manténlo en una red de confianza.

## Dashboard

*MQTT — overview*: mensajes en el tiempo por topic, topics principales y mensajes por resultado.
