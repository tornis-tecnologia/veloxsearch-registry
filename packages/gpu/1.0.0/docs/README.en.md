# GPU

GPU utilization, power and temperature for NVIDIA and sysfs-exposed cards.

## Streams

| Stream | Signal | Default | Destination | What it collects |
| --- | --- | --- | --- | --- |
| `metrics` | metrics | on | OTLP endpoint of the policy → Cortex | GPU utilization, memory, power and temperature |

## Fields

`scrape_interval` (seconds, default 5), `cards_include` (default `*`), `cards_exclude`, `enable_nvml`, `enable_power`, `enable_temperature` and advanced `path_sysfs`.

## Requirements

- Linux with a GPU and its driver (NVML for NVIDIA).
- An OTLP endpoint on the policy (deployment with the OTel stack): without it the stream cannot be activated.
- A Fluent Bit build that includes the `gpu_metrics` input.
