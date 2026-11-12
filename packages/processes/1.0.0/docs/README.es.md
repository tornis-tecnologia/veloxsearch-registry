# Procesos

CPU, memoria, E/S y descriptores de archivo por proceso, más comprobaciones de salud de un proceso.

## Streams

| Stream | Señal | Por defecto | Destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `exporter` | metrics | activa | Endpoint OTLP de la política → Cortex | CPU, E/S, memoria, estado, cambios de contexto, descriptores e hilos por proceso |
| `process` | metrics | inactiva | `veloxagent-process.processes-v1` | `name`, `pid`, `alive`, `mem.*`, `fd` de un proceso |

## Campos

`exporter`: `scrape_interval` (por defecto 5), `collectors` (cpu, io, memory, state, context_switches, fd, start_time, thread_wchan, thread), `process_include_pattern` (regex, por defecto `.+`) y `process_exclude_pattern` (regex).

`process`: `proc_name` (obligatorio), `interval` (segundos, por defecto 10), `mem`, `fd`, `alert` (avanzado) y `delete_after` (por defecto 14d). Campos indexados: `@timestamp`, `name`, `pid`, `alive`, `mem.*`, `fd`, `velox.*`.

## Requisitos

- Linux. El usuario del agente debe leer `/proc` de los procesos a vigilar (normalmente root para procesos de otros usuarios).
- `exporter` requiere un endpoint OTLP en la política (deployment con el stack OTel).

## Notas

`process` sigue un solo nombre de proceso; para varios use `exporter` con un patrón de inclusión.
