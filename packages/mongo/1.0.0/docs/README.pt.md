# MongoDB

Log do servidor MongoDB, coletado pelo Velox Agent.

## Streams

| Stream | Sinal | Padrão | Índice / destino | O que coleta |
| --- | --- | --- | --- | --- |
| `log` | logs | ligado | `veloxagent-log.mongo-v1` | `mongod.log`: linhas JSON (4.4+) com severidade, componente, contexto, mensagem e `attr`; linhas de texto legadas como fallback |

## Campos

`@timestamp`, `message`, `log.level` (`F`→`fatal`, `E`→`error`, `W`→`warning`, `I`→`info`, `D1..5`→`debug`), `mongo.component`, `mongo.context`, `mongo.id`, `mongo.attr` (`flat_object`, pesquisável por caminho com pontos), `event.duration` (ns, de `attr.durationMillis`), `event.outcome` (`unparsed`), `velox.*`.

## Requisitos

- Linux. `systemLog.destination: file` com `systemLog.path`; o usuário do agente deve ler o arquivo (grupo `mongodb` ou `adm`). Consultas lentas aparecem com `operationProfiling.slowOpThresholdMs`. `mongo.attr` requer OpenSearch 2.7+ (`flat_object`).

## Dashboard

*MongoDB — visão geral*: eventos, erros ao longo do tempo, volume por severidade, severidade, componentes e mensagens mais frequentes.
