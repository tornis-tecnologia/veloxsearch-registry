# Serial port

Read lines from a serial device such as a sensor or an embedded board.

## Streams

| Stream | Signal | Default | Destination | What it collects |
| --- | --- | --- | --- | --- |
| `lines` | logs | on | `veloxagent-lines.serial-v1` | Every serial line as `message` |

## Fields

`file` (required, default `/dev/ttyUSB0`), `bitrate` (required integer, default 9600), `separator`, and advanced `format` (`none` or `json`) and `min_bytes`. `delete_after` (default 30d).

Indexed fields: `@timestamp`, `message` (trimmed), `velox.*`.

## Requirements

- Linux. The agent user needs access to the device (usually group `dialout`).
