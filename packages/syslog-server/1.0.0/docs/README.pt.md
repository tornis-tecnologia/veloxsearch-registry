# Servidor syslog

Recebe syslog de roteadores, switches, firewalls e hosts, e o indexa com a facility, a severidade e o horário de cada mensagem.

## Streams

| Stream | Sinal | Padrão | Índice | O que recebe |
| --- | --- | --- | --- | --- |
| `udp` | logs | ligado | `veloxagent-udp.syslog-server-v1` | datagramas em UDP 5140 (todas as interfaces) |
| `tcp` | logs | desligado | `veloxagent-tcp.syslog-server-v1` | mensagens em TCP 5140, delimitadas por linha ou com tamanho (octet-counting) |
| `unix` | logs | desligado | `veloxagent-unix.syslog-server-v1` | datagramas em um socket Unix no diretório de estado do agente (Linux, macOS) |

O Fluent Bit entrega apenas a mensagem bruta; o pipeline de ingestão distingue e interpreta RFC 3164 e RFC 5424. Uma mensagem que não casa com nenhum mantém o texto em `message` com `event.outcome: unparsed`.

## Campos

`@timestamp` (horário da mensagem; o de chegada se não houver), `message`, `host.name`, `process.name`, `process.pid`, `log.level`, `log.syslog.priority`, `log.syslog.facility.code`/`.name`, `log.syslog.severity.code`/`.name`, `log.syslog.version`, `log.syslog.msgid`, `log.syslog.structured_data` (RFC 5424), `event.original` (opcional), `event.outcome`, `velox.*`.

Horários RFC 3164 não trazem ano nem fuso: o ano é o atual e o fuso é o campo `timezone` (padrão UTC).

## Requisitos

- Abra a porta no firewall do host e aponte os equipamentos para o endereço do agente. Portas abaixo de 1024 (a clássica 514) exigem root ou uma capability.
- O stream unix cria `syslog-velox.syslog-server.unix.sock` no diretório de estado do agente; aponte os emissores locais para ele (por exemplo uma ação `omuxsock` do rsyslog).
- Aumente o `Buffer de recepção do socket` para emissores UDP com muito tráfego.

## Dashboard

*Servidor syslog — visão geral*: eventos no tempo por host, principais hosts, principais programas e distribuição por severidade. Lê o stream `udp`.
