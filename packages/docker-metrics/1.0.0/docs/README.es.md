# Métricas de Docker

Uso de CPU y memoria por contenedor Docker.

## Streams

| Stream | Señal | Por defecto | Destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `stats` | metrics | activa | `veloxagent-stats.docker-metrics-v1` | `id`, `name`, `cpu_used`, `mem_used`, `mem_limit` por contenedor |

## Campos

`interval` (segundos, por defecto 10), `include` y `exclude` (ids o nombres de contenedores), avanzados `path_containers` y `path_sysfs`, y `delete_after` (por defecto 14d).

Campos indexados: `@timestamp`, `id`, `name`, `cpu_used` (ns), `mem_used` (bytes), `mem_limit` (bytes), `velox.*`.

## Requisitos

- Linux con Docker. El usuario del agente debe leer `/var/lib/docker/containers` y el árbol cgroup (normalmente root o el grupo `docker`).

## Notas

`include` y `exclude` aceptan listas separadas por espacio de ids o nombres; el formulario une sus entradas con un espacio.

## Dashboard

*Docker — uso de contenedores*: CPU y memoria por contenedor en el tiempo y los contenedores más pesados.
