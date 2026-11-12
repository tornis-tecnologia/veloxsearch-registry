# Receptor Splunk HEC

Um endpoint HTTP compatível com HEC: forwarders, aplicações e scripts do Splunk que enviam para uma URL HEC podem enviar ao agente.

## Streams

| Stream | Sinal | Padrão | Índice / destino | O que coleta |
| --- | --- | --- | --- | --- |
| `events` | logs | ligado | `veloxagent-events.splunk-hec-v1` | Eventos HEC enviados ao HTTP 8088 |

## Campos

`@timestamp` (de `time`, epoch em segundos), `host.name`, `message` (eventos string), `splunk.event.*` (eventos objeto), `splunk.source`, `splunk.sourcetype`, `splunk.index`, `splunk.fields.*`, `velox.*`.

## Requisitos

- Os clientes devem alcançar a porta (8088 por padrão); o agente precisa de permissão para escutar.
- Defina um token HEC: sem ele o endpoint aceita qualquer requisição. O input do Fluent Bit não tem chaves TLS; termine o TLS na frente do agente se precisar.

## Dashboard

*Splunk HEC — overview*: eventos ao longo do tempo por sourcetype, hosts, sources e índices principais.
