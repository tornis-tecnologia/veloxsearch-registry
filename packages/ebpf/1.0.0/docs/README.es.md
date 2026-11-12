# Trazado eBPF

Eventos a nivel de kernel (señales, asignaciones, binds) capturados con eBPF.

## Streams

| Stream | Señal | Por defecto | Destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `events` | logs | activa | `veloxagent-events.ebpf-v1` | Eventos del kernel con `process.pid`, `process.name` y campos propios de cada traza |

## Campos

`trace` (obligatorio, repetible; por defecto `trace_signal`) y `poll_ms` (avanzado). `delete_after` (por defecto 90d).

Campos indexados: `@timestamp`, `event.kind`, `event.module`, `process.pid`, `process.name`, más los números propios de cada traza con mapeo dinámico, `velox.*`.

## Requisitos

- Linux con soporte eBPF y un Fluent Bit que incluya el input `ebpf`.
- El agente debe ejecutarse como root (o con `CAP_BPF`/`CAP_SYS_ADMIN`).

## Notas

Experimental: los nombres de campo dependen del programa de traza y pueden cambiar.
