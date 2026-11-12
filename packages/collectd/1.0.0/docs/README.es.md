# collectd

Recibe métricas del protocolo de red de collectd desde demonios collectd.

## Streams

| Stream | Señal | Por defecto | Destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `metrics` | metrics | activa | `veloxagent-metrics.collectd-v1` | `host`, `plugin`, `plugin_instance`, `type`, `type_instance`, `values` |

## Campos

`listen` (por defecto `0.0.0.0`), `port` (UDP, por defecto 25826), `typesdb` (avanzado, por defecto `/usr/share/collectd/types.db`; se permiten varias rutas) y `delete_after` (por defecto 14d).

Campos indexados: `@timestamp`, `host`, `plugin`, `plugin_instance`, `type`, `type_instance`, `dsnames`, `dstypes`, `values`, `interval`, `velox.*`.

## Requisitos

- Linux. Un demonio collectd con el plugin de escritura `network` apuntando al agente.
- El archivo `types.db` debe existir en el host del agente.
