# SSH

Eventos de autenticación de sshd de auth.log / secure.

## Streams

| Stream | Señal | Por defecto | Índice / destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `auth` | logs | activo | `veloxagent-auth.ssh-v1` | `/var/log/auth.log`, `/var/log/secure`; sshd separado, las demás líneas como syslog |

## Campos

`@timestamp`, `host.name`, `process.name`, `process.pid`, `message` y, para sshd, `event.category` (`authentication`), `event.action` (`login`, `invalid_user`, `max_auth_attempts`, `connection_closed`, `disconnect`), `event.outcome` (`success`, `failure`, `unknown`; `unparsed` en líneas sin forma syslog), `user.name`, `source.ip`, `source.port`, `ssh.method`. Los nombres coinciden con el stream `auth` del paquete `system`. Se reconocen `sshd` y `sshd-session` (OpenSSH 9.8+). La retención por defecto es de 90 días.

Cambian los nombres de 1.x: `auth_result`/`auth_method`/`auth_user`/`src_ip`/`src_port` ahora son `event.outcome`/`ssh.method`/`user.name`/`source.ip`/`source.port`.

## Requisitos

- Linux. El usuario del agente debe leer `/var/log/auth.log` o `/var/log/secure` (normalmente grupo `adm`).
- No lo active junto con el stream `auth` del paquete `system` sobre los mismos archivos: ambos indexarían cada línea.

## Dashboard

*SSH — authentication overview*: eventos de autenticación, IPs de origen únicas, logins fallidos en el tiempo, aceptados vs fallidos en el tiempo, resultados, IPs de origen, usuarios y métodos más frecuentes.
