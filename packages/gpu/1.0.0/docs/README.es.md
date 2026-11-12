# GPU

Utilización, consumo y temperatura de GPU para tarjetas NVIDIA y expuestas por sysfs.

## Streams

| Stream | Señal | Por defecto | Destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `metrics` | metrics | activa | Endpoint OTLP de la política → Cortex | Utilización, memoria, consumo y temperatura de GPU |

## Campos

`scrape_interval` (segundos, por defecto 5), `cards_include` (por defecto `*`), `cards_exclude`, `enable_nvml`, `enable_power`, `enable_temperature` y `path_sysfs` (avanzado).

## Requisitos

- Linux con una GPU y su controlador (NVML para NVIDIA).
- Un endpoint OTLP en la política (deployment con el stack OTel): sin él el stream no se puede activar.
- Un Fluent Bit que incluya el input `gpu_metrics`.
