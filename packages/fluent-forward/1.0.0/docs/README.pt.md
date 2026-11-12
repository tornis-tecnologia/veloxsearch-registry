# Fluent Forward

Um receptor Forward: instâncias do Fluent Bit e do Fluentd enviam seus eventos a este agente, que os indexa no OpenSearch.

## Streams

| Stream | Sinal | Padrão | Índice / destino | O que coleta |
| --- | --- | --- | --- | --- |
| `logs` | logs | ligado | `veloxagent-logs.fluent-forward-v1` | Eventos do protocolo Forward no TCP 24224 (chave compartilhada opcional) |

## Campos

`@timestamp` (de `time`, `timestamp` ou `ts`, ISO-8601 ou epoch em segundos/milissegundos; hora de ingestão se ausente), `host.name` (de um `host` string ou `hostname`), `event.outcome`, `velox.*`. As demais chaves são mantidas como chegam.

## Requisitos

- A porta (24224 por padrão) deve ser alcançável pelos emissores; o agente precisa de permissão para escutar.
- Com `shared_key`, os emissores devem usar Secure Forward com a mesma chave.

## Dashboard

*Fluent Forward — overview*: eventos ao longo do tempo por host, hosts principais e registros por resultado.
