# System

Logs and metrics of the Linux host itself, collected by Velox Agent.

## Streams

| Stream | Signal | Default | Index / destination | What it collects |
| --- | --- | --- | --- | --- |
| `syslog` | logs | on | `veloxagent-syslog.system-v1` | `/var/log/syslog`, `/var/log/messages` parsed into host, process, pid, message |
| `auth` | logs | on | `veloxagent-auth.system-v1` | `/var/log/auth.log`, `/var/log/secure`; SSH logins and `sudo` parsed (user, source IP, outcome) |
| `journal` | logs | off | `veloxagent-journal.system-v1` | journald entries, optionally only chosen units |
| `kernel` | logs | off | `veloxagent-kernel.system-v1` | `/dev/kmsg` with a level name |
| `cpu` | metrics | off | `veloxagent-cpu.system-v1` | CPU usage samples as documents (no OTel stack needed) |
| `mem` | metrics | off | `veloxagent-mem.system-v1` | memory and swap samples as documents |
| `host_metrics` | metrics | off | OTLP endpoint of the policy → Cortex | node-exporter compatible metrics (needs the OTel stack) |

## Fields (logs)

`@timestamp`, `message`, `host.name`, `process.name`, `process.pid`,
`event.outcome` (`success`/`failure` for SSH, `unparsed` when a line has no
syslog shape), `event.category`, `user.name`, `source.ip`, `source.port`,
`ssh.method`, `process.command_line` (sudo), `systemd.unit`, `log.level`,
`log.syslog.priority`, `velox.*`.

## Requirements

- Linux. The agent user must read the log files (usually group `adm`), `/dev/kmsg` for `kernel`, and the journal (group `systemd-journal`) for `journal`.
- `host_metrics` needs an OTLP endpoint on the policy (deployment with the OTel stack).

## Dashboard

*System — overview*: syslog volume by host, top processes, SSH success vs failure, failed logins by source IP, kernel levels, CPU and memory.
