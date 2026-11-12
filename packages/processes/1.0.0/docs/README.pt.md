# Processos

CPU, memória, E/S e descritores de arquivo por processo, mais verificações de saúde de um processo.

## Streams

| Stream | Sinal | Padrão | Destino | O que coleta |
| --- | --- | --- | --- | --- |
| `exporter` | metrics | ligada | Endpoint OTLP da política → Cortex | CPU, E/S, memória, estado, trocas de contexto, descritores e threads por processo |
| `process` | metrics | desligada | `veloxagent-process.processes-v1` | `name`, `pid`, `alive`, `mem.*`, `fd` de um processo |

## Campos

`exporter`: `scrape_interval` (padrão 5), `collectors` (cpu, io, memory, state, context_switches, fd, start_time, thread_wchan, thread), `process_include_pattern` (regex, padrão `.+`) e `process_exclude_pattern` (regex).

`process`: `proc_name` (obrigatório), `interval` (segundos, padrão 10), `mem`, `fd`, `alert` (avançado) e `delete_after` (padrão 14d). Campos indexados: `@timestamp`, `name`, `pid`, `alive`, `mem.*`, `fd`, `velox.*`.

## Requisitos

- Linux. O usuário do agente deve ler `/proc` dos processos a vigiar (normalmente root para processos de outros usuários).
- `exporter` exige um endpoint OTLP na política (deployment com o stack OTel).

## Notas

`process` segue um único nome de processo; para vários use `exporter` com um padrão de inclusão.
