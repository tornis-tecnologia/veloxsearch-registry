# Sistema

Logs e métricas do próprio host Linux, coletados pelo Velox Agent.

## Streams

| Stream | Sinal | Padrão | Índice / destino | O que coleta |
| --- | --- | --- | --- | --- |
| `syslog` | logs | ligado | `veloxagent-syslog.system-v1` | `/var/log/syslog`, `/var/log/messages` separados em host, processo, pid e mensagem |
| `auth` | logs | ligado | `veloxagent-auth.system-v1` | `/var/log/auth.log`, `/var/log/secure`; logins SSH e `sudo` analisados (usuário, IP de origem, resultado) |
| `journal` | logs | desligado | `veloxagent-journal.system-v1` | entradas do journald, opcionalmente só certas units |
| `kernel` | logs | desligado | `veloxagent-kernel.system-v1` | `/dev/kmsg` com nome de nível |
| `cpu` | métricas | desligado | `veloxagent-cpu.system-v1` | amostras de uso de CPU como documentos (sem stack OTel) |
| `mem` | métricas | desligado | `veloxagent-mem.system-v1` | amostras de memória e swap como documentos |
| `host_metrics` | métricas | desligado | endpoint OTLP da política → Cortex | métricas compatíveis com node-exporter (exige o stack OTel) |

## Campos (logs)

`@timestamp`, `message`, `host.name`, `process.name`, `process.pid`,
`event.outcome` (`success`/`failure` para SSH, `unparsed` quando a linha não tem forma de syslog),
`event.category`, `user.name`, `source.ip`, `source.port`, `ssh.method`,
`process.command_line` (sudo), `systemd.unit`, `log.level`, `log.syslog.priority`, `velox.*`.

## Requisitos

- Linux. O usuário do agente precisa ler os arquivos de log (normalmente grupo `adm`), `/dev/kmsg` para `kernel` e o journal (grupo `systemd-journal`) para `journal`.
- `host_metrics` precisa de um endpoint OTLP na política (deployment com o stack OTel).

## Dashboard

*System — overview*: volume de syslog por host, processos principais, SSH sucesso vs falha, logins falhos por IP de origem, níveis do kernel, CPU e memória.
