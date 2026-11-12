# Servidor syslog

Recibe syslog de routers, switches, firewalls y hosts, y lo indexa con la facility, la severidad y la hora de cada mensaje.

## Streams

| Stream | Señal | Por defecto | Índice | Qué recibe |
| --- | --- | --- | --- | --- |
| `udp` | logs | activo | `veloxagent-udp.syslog-server-v1` | datagramas en UDP 5140 (todas las interfaces) |
| `tcp` | logs | apagado | `veloxagent-tcp.syslog-server-v1` | mensajes en TCP 5140, delimitados por línea o con longitud (octet-counting) |
| `unix` | logs | apagado | `veloxagent-unix.syslog-server-v1` | datagramas en un socket Unix del directorio de estado del agente (Linux, macOS) |

Fluent Bit solo entrega el mensaje sin procesar; el pipeline de ingesta distingue y analiza RFC 3164 y RFC 5424. Un mensaje que no coincide con ninguno conserva su texto en `message` con `event.outcome: unparsed`.

## Campos

`@timestamp` (hora del mensaje; la de llegada si no la trae), `message`, `host.name`, `process.name`, `process.pid`, `log.level`, `log.syslog.priority`, `log.syslog.facility.code`/`.name`, `log.syslog.severity.code`/`.name`, `log.syslog.version`, `log.syslog.msgid`, `log.syslog.structured_data` (RFC 5424), `event.original` (opcional), `event.outcome`, `velox.*`.

Las horas RFC 3164 no traen año ni zona: el año es el actual y la zona es el campo `timezone` (por defecto UTC).

## Requisitos

- Abra el puerto en el firewall del host y apunte los equipos a la dirección del agente. Los puertos menores de 1024 (el clásico 514) exigen root o una capability.
- El stream unix crea `syslog-velox.syslog-server.unix.sock` en el directorio de estado del agente; apunte los emisores locales a él (por ejemplo una acción `omuxsock` de rsyslog).
- Aumente `Búfer de recepción del socket` para emisores UDP con mucho tráfico.

## Dashboard

*Servidor syslog — resumen*: eventos en el tiempo por host, principales hosts, principales programas y desglose por severidad. Lee el stream `udp`.
