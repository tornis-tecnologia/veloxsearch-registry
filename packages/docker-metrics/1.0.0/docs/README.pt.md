# Métricas do Docker

Uso de CPU e memória por contêiner Docker.

## Streams

| Stream | Sinal | Padrão | Destino | O que coleta |
| --- | --- | --- | --- | --- |
| `stats` | metrics | ligada | `veloxagent-stats.docker-metrics-v1` | `id`, `name`, `cpu_used`, `mem_used`, `mem_limit` por contêiner |

## Campos

`interval` (segundos, padrão 10), `include` e `exclude` (ids ou nomes de contêineres), avançados `path_containers` e `path_sysfs`, e `delete_after` (padrão 14d).

Campos indexados: `@timestamp`, `id`, `name`, `cpu_used` (ns), `mem_used` (bytes), `mem_limit` (bytes), `velox.*`.

## Requisitos

- Linux com Docker. O usuário do agente deve ler `/var/lib/docker/containers` e a árvore cgroup (normalmente root ou o grupo `docker`).

## Notas

`include` e `exclude` aceitam listas separadas por espaço de ids ou nomes; o formulário une suas entradas com um espaço.

## Dashboard

*Docker — uso de contêineres*: CPU e memória por contêiner ao longo do tempo e os contêineres mais pesados.
