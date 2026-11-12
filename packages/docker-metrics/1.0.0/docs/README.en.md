# Docker metrics

CPU and memory usage per Docker container.

## Streams

| Stream | Signal | Default | Destination | What it collects |
| --- | --- | --- | --- | --- |
| `stats` | metrics | on | `veloxagent-stats.docker-metrics-v1` | `id`, `name`, `cpu_used`, `mem_used`, `mem_limit` per container |

## Fields

`interval` (seconds, default 10), `include` and `exclude` (container ids or names), advanced `path_containers` and `path_sysfs`, and `delete_after` (default 14d).

Indexed fields: `@timestamp`, `id`, `name`, `cpu_used` (ns), `mem_used` (bytes), `mem_limit` (bytes), `velox.*`.

## Requirements

- Linux with Docker. The agent user must read `/var/lib/docker/containers` and the cgroup tree (usually root or the `docker` group).

## Notes

`include` and `exclude` take space-separated lists of ids or names; the form joins your entries with a space.

## Dashboard

*Docker — container usage*: CPU and memory per container over time, and the heaviest containers.
