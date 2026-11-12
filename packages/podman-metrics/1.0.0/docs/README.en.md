# Podman metrics

CPU, memory, network and block I/O metrics of Podman containers.

## Streams

| Stream | Signal | Default | Destination | What it collects |
| --- | --- | --- | --- | --- |
| `metrics` | metrics | on | OTLP endpoint of the policy → Cortex | Container CPU, memory, network and block I/O metrics |

## Fields

`scrape_interval` (seconds, default 30) and advanced `scrape_on_start`. The Podman `path.config`, `path.sysfs` and `path.procfs` locations are fixed by the package to the standard rootful paths.

## Requirements

- Linux with Podman (rootful containers; the agent reads `containers.json`, cgroups and `/proc`).
- An OTLP endpoint on the policy (deployment with the OTel stack).

## Notes

The `podman_metrics` plugin may not be compiled into every Fluent Bit build; the agent reports it if the host's Fluent Bit lacks it.
