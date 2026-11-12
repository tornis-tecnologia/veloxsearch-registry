# Archivos binarios (blob)

Ingiere archivos binarios de un directorio y registra lo procesado.

## Streams

| Stream | Señal | Por defecto | Destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `files` | logs | activa | `veloxagent-files.blob-v1` | Un registro por archivo: `file.path`, `file.name`, `file.size` |

## Campos

`path` (obligatorio, por defecto `/var/spool/velox/blobs/*`), `exclude` (patrones), `scan_refresh_interval` (por defecto 10s) y avanzados `upload_success_action` / `upload_failure_action` (`delete`, `add_suffix`, `emit_log`) con sus sufijos. La base de seguimiento está fija bajo el directorio de estado del agente. `delete_after` (por defecto 30d).

## Requisitos

- El usuario del agente debe leer el directorio (y escribir si elige `delete` o `add_suffix`).

## Notas

Beta. `delete` elimina los archivos del disco tras una carga correcta.
