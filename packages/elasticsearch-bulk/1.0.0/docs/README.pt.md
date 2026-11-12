# Receptor Elasticsearch bulk

Um endpoint Bulk API para Beats, Logstash e qualquer cliente que fale o protocolo bulk do Elasticsearch; os eventos são indexados no OpenSearch pelo agente.

## Streams

| Stream | Sinal | Padrão | Índice / destino | O que coleta |
| --- | --- | --- | --- | --- |
| `bulk` | logs | ligado | `veloxagent-bulk.elasticsearch-bulk-v1` | Documentos Bulk API enviados ao HTTP 9201 |

## Campos

`@timestamp` (mantido; normalizado para ISO-8601 UTC, hora de ingestão se ausente ou inválido), `host.name` (de um `host` string, `hostname` ou `agent.hostname`), `bulk.meta.*` (metadados da ação bulk), `event.outcome` (`unparsed` para timestamp inválido), `velox.*`. Os demais campos são mantidos.

## Requisitos

- Aponte Beats/Logstash para `http://<agente>:9201`; o agente precisa de permissão para escutar.
- O endpoint não tem autenticação: mantenha-o em uma rede confiável. Beats pode precisar de `setup.ilm.enabled: false` e `setup.template.enabled: false`.

## Dashboard

*Elasticsearch bulk — overview*: eventos ao longo do tempo por host, hosts principais, tipos de shipper e eventos por resultado.
