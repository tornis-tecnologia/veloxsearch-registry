# Rastreamento eBPF

Eventos em nível de kernel (sinais, alocações, binds) capturados com eBPF.

## Streams

| Stream | Sinal | Padrão | Destino | O que coleta |
| --- | --- | --- | --- | --- |
| `events` | logs | ligada | `veloxagent-events.ebpf-v1` | Eventos do kernel com `process.pid`, `process.name` e campos próprios de cada trace |

## Campos

`trace` (obrigatório, repetível; padrão `trace_signal`) e `poll_ms` (avançado). `delete_after` (padrão 90d).

Campos indexados: `@timestamp`, `event.kind`, `event.module`, `process.pid`, `process.name`, mais os números próprios de cada trace com mapeamento dinâmico, `velox.*`.

## Requisitos

- Linux com suporte a eBPF e um Fluent Bit que inclua o input `ebpf`.
- O agente deve rodar como root (ou com `CAP_BPF`/`CAP_SYS_ADMIN`).

## Notas

Experimental: os nomes dos campos dependem do programa de trace e podem mudar.
