# OpenTelemetry

Receptor OTLP de logs, métricas e traces de SDKs e coletores OpenTelemetry.

## Streams

| Stream | Sinal | Padrão | Destino | O que coleta |
| --- | --- | --- | --- | --- |
| `logs` | logs | ligada | `veloxagent-logs.opentelemetry-v1` | Registros de log OTLP: `log.level`, `message`, `trace_id`, `span_id`, `service.name`, `resource.*`, `attributes.*` |
| `metrics` | metrics | desligada | Endpoint OTLP da política → Cortex | Métricas OTLP de aplicações e coletores |
| `traces` | traces | desligada | `veloxagent-traces.opentelemetry-v1` | Spans: `trace_id`, `span_id`, `parent_span_id`, `name`, `kind`, `start`, `end`, `duration`, `status`, `attributes.*` |

## Campos

Todos os streams: `listen` (padrão `0.0.0.0`), `port`, `tls` com `tls_crt_file`, `tls_key_file`, `tls_key_passwd` (segredo) e `tls_ca_file`, e `buffer_max_size`. `traces` tem também `raw_traces`. Logs e traces expõem `delete_after` (padrão 30d / 14d).

As portas padrão são distintas por stream: `logs` 4318, `metrics` 4319, `traces` 4320. Aponte cada exportador do SDK para a porta correspondente (`http://host:4318/v1/logs`, `:4319/v1/metrics`, `:4320/v1/traces`).

Campos de log indexados: `@timestamp` (de `time_unix_nano` quando existe), `log.level` (de `severity_text`, minúsculas), `otel.severity_number`, `message` (de `body`), `trace_id`, `span_id`, `service.name`, `host.name`, `resource.*`, `attributes.*`, `velox.*`.

## Requisitos

- A porta de escuta deve estar acessível às aplicações (firewall, rede de contêineres).
- `metrics` exige um endpoint OTLP na política (deployment com o stack OTel).

## Notas

No Fluent Bit os três sinais compartilham o mesmo plugin `opentelemetry` e um listener por input. Ativar dois streams faz o compilador emitir dois inputs, que precisam escutar em portas diferentes; por isso os padrões diferem. Se alterar uma porta, mantenha-as distintas (ou ative só um stream). O pacote fixa `tag_from_uri: false` para que os registros mantenham o tag do stream usado no roteamento. Só a porta HTTP é exposta; gRPC não é configurável como porta separada no plugin.

## Dashboard

*OpenTelemetry — logs*: volume por serviço, níveis de severidade, principais serviços e erros recentes por serviço.
