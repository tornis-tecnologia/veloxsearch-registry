# Puerto serie

Lee líneas de un dispositivo serie como un sensor o una placa embebida.

## Streams

| Stream | Señal | Por defecto | Destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `lines` | logs | activa | `veloxagent-lines.serial-v1` | Cada línea serial como `message` |

## Campos

`file` (obligatorio, por defecto `/dev/ttyUSB0`), `bitrate` (entero obligatorio, por defecto 9600), `separator`, y avanzados `format` (`none` o `json`) y `min_bytes`. `delete_after` (por defecto 30d).

Campos indexados: `@timestamp`, `message` (sin espacios sobrantes), `velox.*`.

## Requisitos

- Linux. El usuario del agente necesita acceso al dispositivo (normalmente el grupo `dialout`).
