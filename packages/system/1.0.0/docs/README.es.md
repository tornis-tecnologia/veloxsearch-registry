# Sistema

Logs y métricas del propio host Linux, recolectados por Velox Agent.

## Streams

| Stream | Señal | Por defecto | Índice / destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `syslog` | logs | activo | `veloxagent-syslog.system-v1` | `/var/log/syslog`, `/var/log/messages` separados en host, proceso, pid y mensaje |
| `auth` | logs | activo | `veloxagent-auth.system-v1` | `/var/log/auth.log`, `/var/log/secure`; logins SSH y `sudo` analizados (usuario, IP de origen, resultado) |
| `journal` | logs | inactivo | `veloxagent-journal.system-v1` | entradas de journald, opcionalmente solo ciertas units |
| `kernel` | logs | inactivo | `veloxagent-kernel.system-v1` | `/dev/kmsg` con nombre de nivel |
| `cpu` | métricas | inactivo | `veloxagent-cpu.system-v1` | muestras de uso de CPU como documentos (sin stack OTel) |
| `mem` | métricas | inactivo | `veloxagent-mem.system-v1` | muestras de memoria y swap como documentos |
| `host_metrics` | métricas | inactivo | endpoint OTLP de la política → Cortex | métricas compatibles con node-exporter (requiere el stack OTel) |

## Campos (logs)

`@timestamp`, `message`, `host.name`, `process.name`, `process.pid`,
`event.outcome` (`success`/`failure` para SSH, `unparsed` cuando la línea no tiene forma syslog),
`event.category`, `user.name`, `source.ip`, `source.port`, `ssh.method`,
`process.command_line` (sudo), `systemd.unit`, `log.level`, `log.syslog.priority`, `velox.*`.

## Requisitos

- Linux. El usuario del agente debe poder leer los archivos de log (normalmente grupo `adm`), `/dev/kmsg` para `kernel` y el journal (grupo `systemd-journal`) para `journal`.
- `host_metrics` necesita un endpoint OTLP en la política (deployment con el stack OTel).

## Panel

*System — overview*: volumen de syslog por host, procesos principales, SSH éxito vs fallo, logins fallidos por IP de origen, niveles del kernel, CPU y memoria.
