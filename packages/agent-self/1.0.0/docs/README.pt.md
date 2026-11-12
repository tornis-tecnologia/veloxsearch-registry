# Velox Agent self-monitoring

O agente observando a si mesmo: seu próprio log do Fluent Bit, verificações de alcance TCP e métricas internas.

## Streams

| Stream | Sinal | Padrão | Índice / destino | O que coleta |
| --- | --- | --- | --- | --- |
| `logs` | logs | sim | `veloxagent-logs.agent-self-v1` | Linhas do log do Fluent Bit separadas em nível, componente e mensagem |
| `health` | logs | não | `veloxagent-health.agent-self-v1` | Verificações de conexão TCP a um host e porta: ativo ou fora do ar |
| `metrics` | metrics | não | Endpoint OTLP da política | Métricas internas do Fluent Bit (exige o stack OTel) |

## Campos

`logs`: `@timestamp`, `message`, `log.level`, `fluentbit.component`, `event.original`, `event.outcome` (`unparsed`). `health`: `health.alive`, `destination.address`, `destination.port`, `event.outcome` (`success`/`failure`), `event.category`. Todos: `velox.*`.

## Requisitos

- `health` precisa de host e porta; o stream fica desligado até informá-los.
- `metrics` exige um endpoint OTLP na política.
- Os timestamps do log são lidos como UTC; o Fluent Bit imprime hora local.

## Dashboard

*Agent self-monitoring — overview*: linhas de log por nível, componentes mais ruidosos, erros e avisos por componente, verificações TCP ao longo do tempo e por destino.
