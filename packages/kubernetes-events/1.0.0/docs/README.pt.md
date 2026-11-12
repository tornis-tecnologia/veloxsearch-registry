# Eventos do Kubernetes

Eventos da API do Kubernetes (scheduling, pull de imagens, back-offs, condições de nó) como logs pesquisáveis.

## Streams

| Stream | Sinal | Padrão | Destino | O que coleta |
| --- | --- | --- | --- | --- |
| `events` | logs | ligada | `veloxagent-events.kubernetes-events-v1` | `kubernetes.event.reason`, `.type`, `.message`, `.count`, `.involved_object.*` |

## Campos

`kube_url`, `kube_namespace` (vazio = todos), `tls_verify`, e avançados `kube_token_file`, `kube_ca_file`, `kube_retention_time`, `interval_sec` e `interval_nsec`. O banco de checkpoints é fixo no diretório de estado do agente. `delete_after` (padrão 14d).

Campos indexados: `@timestamp` (de `lastTimestamp`), `message`, `kubernetes.event.reason`, `.type` (Normal/Warning), `.message`, `.count`, `.action`, `.first_timestamp`, `.involved_object.kind|name|namespace|uid`, `.source.component|host`, `velox.*`. Um registro sem motivo recebe `event.outcome: unparsed`.

## Requisitos

- Acesso ao servidor de API do Kubernetes (`kube_api`), normalmente de dentro do cluster com um token de service account.
- RBAC: `get`, `list` e `watch` em `events`. Execute um agente por cluster; caso contrário os eventos são duplicados.

## Dashboard

*Kubernetes — eventos*: eventos ao longo do tempo por tipo, principais motivos, principais namespaces e objetos com mais avisos.
