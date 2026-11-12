# Eventos de Kubernetes

Eventos de la API de Kubernetes (scheduling, descarga de imágenes, back-offs, condiciones de nodo) como logs consultables.

## Streams

| Stream | Señal | Por defecto | Destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `events` | logs | activa | `veloxagent-events.kubernetes-events-v1` | `kubernetes.event.reason`, `.type`, `.message`, `.count`, `.involved_object.*` |

## Campos

`kube_url`, `kube_namespace` (vacío = todos), `tls_verify`, y avanzados `kube_token_file`, `kube_ca_file`, `kube_retention_time`, `interval_sec` e `interval_nsec`. La base de checkpoints está fija bajo el directorio de estado del agente. `delete_after` (por defecto 14d).

Campos indexados: `@timestamp` (de `lastTimestamp`), `message`, `kubernetes.event.reason`, `.type` (Normal/Warning), `.message`, `.count`, `.action`, `.first_timestamp`, `.involved_object.kind|name|namespace|uid`, `.source.component|host`, `velox.*`. Un registro sin motivo recibe `event.outcome: unparsed`.

## Requisitos

- Acceso al servidor de API de Kubernetes (`kube_api`), normalmente desde dentro del clúster con un token de service account.
- RBAC: `get`, `list` y `watch` sobre `events`. Ejecute un agente por clúster; de lo contrario los eventos se duplican.

## Dashboard

*Kubernetes — eventos*: eventos en el tiempo por tipo, motivos principales, namespaces principales y objetos con más advertencias.
