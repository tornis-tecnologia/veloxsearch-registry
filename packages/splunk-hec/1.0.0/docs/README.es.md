# Receptor Splunk HEC

Un endpoint HTTP compatible con HEC: forwarders, aplicaciones y scripts de Splunk que envían a una URL HEC pueden enviar al agente.

## Streams

| Stream | Señal | Por defecto | Índice / destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `events` | logs | activado | `veloxagent-events.splunk-hec-v1` | Eventos HEC enviados al HTTP 8088 |

## Campos

`@timestamp` (de `time`, epoch en segundos), `host.name`, `message` (eventos string), `splunk.event.*` (eventos objeto), `splunk.source`, `splunk.sourcetype`, `splunk.index`, `splunk.fields.*`, `velox.*`.

## Requisitos

- Los clientes deben alcanzar el puerto (8088 por defecto); el agente necesita permiso para escuchar.
- Define un token HEC: sin él el endpoint acepta cualquier solicitud. El input de Fluent Bit no tiene claves TLS; termina el TLS delante del agente si lo necesitas.

## Dashboard

*Splunk HEC — overview*: eventos en el tiempo por sourcetype, hosts, sources e índices principales.
