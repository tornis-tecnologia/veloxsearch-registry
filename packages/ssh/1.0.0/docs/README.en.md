# SSH

sshd authentication events from auth.log / secure.

## Streams

| Stream | Signal | Default | Index / destination | What it collects |
| --- | --- | --- | --- | --- |
| `auth` | logs | on | `veloxagent-auth.ssh-v1` | `/var/log/auth.log`, `/var/log/secure`; sshd parsed, other lines kept as syslog |

## Fields

`@timestamp`, `host.name`, `process.name`, `process.pid`, `message`, and for sshd `event.category` (`authentication`), `event.action` (`login`, `invalid_user`, `max_auth_attempts`, `connection_closed`, `disconnect`), `event.outcome` (`success`, `failure`, `unknown`; `unparsed` for lines without syslog shape), `user.name`, `source.ip`, `source.port`, `ssh.method`. Names match the `auth` stream of the `system` package. Both `sshd` and `sshd-session` (OpenSSH 9.8+) are recognised. Retention defaults to 90 days.

1.x names changed: `auth_result`/`auth_method`/`auth_user`/`src_ip`/`src_port` are now `event.outcome`/`ssh.method`/`user.name`/`source.ip`/`source.port`.

## Requirements

- Linux. The agent user must read `/var/log/auth.log` or `/var/log/secure` (usually group `adm`).
- Do not enable this together with the `auth` stream of the `system` package on the same files: both would index each line.

## Dashboard

*SSH — authentication overview*: auth events, unique source IPs, failed logins over time, accepted vs failed over time, outcomes, top source IPs, top users and authentication methods.
