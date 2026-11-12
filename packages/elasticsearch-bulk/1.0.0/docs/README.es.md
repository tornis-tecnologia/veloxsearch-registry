# Receptor Elasticsearch bulk

Un endpoint Bulk API para Beats, Logstash y cualquier cliente que hable el protocolo bulk de Elasticsearch; los eventos se indexan en OpenSearch a través del agente.

## Streams

| Stream | Señal | Por defecto | Índice / destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `bulk` | logs | activado | `veloxagent-bulk.elasticsearch-bulk-v1` | Documentos Bulk API enviados al HTTP 9201 |

## Campos

`@timestamp` (se conserva; normalizado a ISO-8601 UTC, hora de ingesta si falta o es inválido), `host.name` (de un `host` string, `hostname` o `agent.hostname`), `bulk.meta.*` (metadatos de la acción bulk), `event.outcome` (`unparsed` por timestamp inválido), `velox.*`. Los demás campos se conservan.

## Requisitos

- Apunta Beats/Logstash a `http://<agente>:9201`; el agente necesita permiso para escuchar.
- El endpoint no tiene autenticación: manténlo en una red de confianza. Beats puede necesitar `setup.ilm.enabled: false` y `setup.template.enabled: false`.

## Dashboard

*Elasticsearch bulk — overview*: eventos en el tiempo por host, hosts principales, tipos de shipper y eventos por resultado.
