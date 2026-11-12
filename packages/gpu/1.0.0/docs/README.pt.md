# GPU

Utilização, consumo e temperatura de GPU para placas NVIDIA e expostas via sysfs.

## Streams

| Stream | Sinal | Padrão | Destino | O que coleta |
| --- | --- | --- | --- | --- |
| `metrics` | metrics | ligada | Endpoint OTLP da política → Cortex | Utilização, memória, consumo e temperatura de GPU |

## Campos

`scrape_interval` (segundos, padrão 5), `cards_include` (padrão `*`), `cards_exclude`, `enable_nvml`, `enable_power`, `enable_temperature` e `path_sysfs` (avançado).

## Requisitos

- Linux com uma GPU e seu driver (NVML para NVIDIA).
- Um endpoint OTLP na política (deployment com o stack OTel): sem ele o stream não pode ser ativado.
- Um Fluent Bit que inclua o input `gpu_metrics`.
