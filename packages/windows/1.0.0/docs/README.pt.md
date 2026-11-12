# Windows

Logs e métricas de hosts Windows, coletados pelo Velox Agent.

## Streams

| Stream | Sinal | Padrão | Índice / destino | O que coleta |
| --- | --- | --- | --- | --- |
| `eventlog` | logs | sim | `veloxagent-eventlog.windows-v1` | Application, System, Security e outros canais (API winevt) como winlog.*, event.code, log.level |
| `eventlog_legacy` | logs | não | `veloxagent-eventlog_legacy.windows-v1` | Os mesmos canais pela API winlog clássica (Windows antigo) |
| `stats` | metrics | não | `veloxagent-stats.windows-v1` | Contadores de CPU, memória, disco e rede como documentos (sem stack OTel) |
| `exporter_metrics` | metrics | não | Endpoint OTLP da política | Métricas compatíveis com Windows Exporter (exige o stack OTel) |
| `etw` | logs | não | `veloxagent-etw.windows-v1` | Sessão ETW de provedor ou do kernel |

## Campos

`eventlog`: `@timestamp` (de `TimeCreated`), `message`, `host.name`, `log.level` (critical, error, warning, information, verbose), `event.code`, `event.provider`, `event.category`/`event.outcome` (logon 4624/4625), `user.id`, `user.name`, `winlog.channel`, `winlog.provider_name`, `winlog.provider_guid`, `winlog.event_id`, `winlog.record_id`, `winlog.level`, `winlog.task`, `winlog.opcode`, `winlog.keywords`, `winlog.computer_name`, `winlog.process.pid`, `winlog.process.thread.id`, `winlog.string_inserts`, `event.original` (XML ou texto). `eventlog_legacy` mapeia o registro winlog para os mesmos campos. `stats` e `etw` mantêm os nomes de campo do plugin.

## Requisitos

- Windows com o Velox Agent rodando com conta de serviço que leia os canais; `Security` exige direitos de administrador.
- `exporter_metrics` exige um endpoint OTLP na política.
- `etw` precisa de nome ou GUID de provedor (sessão de provedor) ou do tipo `system`; uma sessão existente com o mesmo nome é parada e reiniciada.

## Dashboard

*Windows — overview*: eventos por canal, principais provedores, erros e eventos críticos ao longo do tempo, principais códigos de evento, logons com sucesso vs falha.
