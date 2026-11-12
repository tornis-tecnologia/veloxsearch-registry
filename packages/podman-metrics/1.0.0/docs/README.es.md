# Métricas de Podman

Métricas de CPU, memoria, red y E/S de bloque de contenedores Podman.

## Streams

| Stream | Señal | Por defecto | Destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `metrics` | metrics | activa | Endpoint OTLP de la política → Cortex | Métricas de CPU, memoria, red y E/S de bloque por contenedor |

## Campos

`scrape_interval` (segundos, por defecto 30) y `scrape_on_start` (avanzado). Las rutas de Podman `path.config`, `path.sysfs` y `path.procfs` las fija el paquete a las rutas estándar rootful.

## Requisitos

- Linux con Podman (contenedores rootful; el agente lee `containers.json`, cgroups y `/proc`).
- Un endpoint OTLP en la política (deployment con el stack OTel).

## Notas

El plugin `podman_metrics` puede no estar compilado en todos los builds de Fluent Bit; el agente lo informa si el Fluent Bit del host no lo incluye.
