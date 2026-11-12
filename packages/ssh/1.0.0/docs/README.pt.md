# SSH

Eventos de autenticação do sshd de auth.log / secure.

## Streams

| Stream | Sinal | Padrão | Índice / destino | O que coleta |
| --- | --- | --- | --- | --- |
| `auth` | logs | ligado | `veloxagent-auth.ssh-v1` | `/var/log/auth.log`, `/var/log/secure`; sshd separado, demais linhas como syslog |

## Campos

`@timestamp`, `host.name`, `process.name`, `process.pid`, `message` e, para o sshd, `event.category` (`authentication`), `event.action` (`login`, `invalid_user`, `max_auth_attempts`, `connection_closed`, `disconnect`), `event.outcome` (`success`, `failure`, `unknown`; `unparsed` em linhas sem formato syslog), `user.name`, `source.ip`, `source.port`, `ssh.method`. Os nomes coincidem com o stream `auth` do pacote `system`. `sshd` e `sshd-session` (OpenSSH 9.8+) são reconhecidos. A retenção padrão é de 90 dias.

Os nomes do 1.x mudaram: `auth_result`/`auth_method`/`auth_user`/`src_ip`/`src_port` agora são `event.outcome`/`ssh.method`/`user.name`/`source.ip`/`source.port`.

## Requisitos

- Linux. O usuário do agente deve ler `/var/log/auth.log` ou `/var/log/secure` (normalmente grupo `adm`).
- Não ative junto com o stream `auth` do pacote `system` nos mesmos arquivos: ambos indexariam cada linha.

## Dashboard

*SSH — authentication overview*: eventos de autenticação, IPs de origem únicos, logins falhos ao longo do tempo, aceitos vs falhos ao longo do tempo, resultados, IPs de origem, usuários e métodos mais frequentes.
