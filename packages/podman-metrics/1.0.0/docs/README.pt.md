# Métricas do Podman

Métricas de CPU, memória, rede e E/S de bloco de contêineres Podman.

## Streams

| Stream | Sinal | Padrão | Destino | O que coleta |
| --- | --- | --- | --- | --- |
| `metrics` | metrics | ligada | Endpoint OTLP da política → Cortex | Métricas de CPU, memória, rede e E/S de bloco por contêiner |

## Campos

`scrape_interval` (segundos, padrão 30) e `scrape_on_start` (avançado). Os caminhos do Podman `path.config`, `path.sysfs` e `path.procfs` são fixados pelo pacote nos caminhos padrão rootful.

## Requisitos

- Linux com Podman (contêineres rootful; o agente lê `containers.json`, cgroups e `/proc`).
- Um endpoint OTLP na política (deployment com o stack OTel).

## Notas

O plugin `podman_metrics` pode não estar compilado em todos os builds do Fluent Bit; o agente informa se o Fluent Bit do host não o tiver.
