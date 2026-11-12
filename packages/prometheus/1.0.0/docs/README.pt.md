# Prometheus

Métricas em formato Prometheus de exporters, textfiles ou remote write.

## Streams

| Stream | Sinal | Padrão | Índice / destino | O que coleta |
| --- | --- | --- | --- | --- |
| `scrape` | metrics | sim | Endpoint OTLP da política | Coleta `/metrics` de um host e porta (TLS, basic auth e bearer token opcionais) |
| `textfile` | metrics | não | Endpoint OTLP da política | Lê arquivos `*.prom` do textfile collector |
| `remote_write` | metrics | não | Endpoint OTLP da política | Recebe requisições remote-write do Prometheus em uma porta |

## Campos

As métricas mantêm seus nomes e labels do Prometheus; o agente adiciona `velox_integration`, `velox_stream` e `velox_package_version`. Nada é gravado no OpenSearch.

## Requisitos

- Todos os streams exigem um endpoint OTLP na política (deployment com o stack OTel); sem ele o console não os oferece.
- `remote_write` abre uma porta de escuta no host; mantenha em uma interface confiável ou ative TLS.

## Dashboard

Nenhum. Dashboards de métricas precisam da datasource Prometheus do deployment; construa-os sobre os labels `velox_integration` e `velox_stream`.
