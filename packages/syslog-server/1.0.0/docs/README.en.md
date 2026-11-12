# Syslog server

Receives syslog from routers, switches, firewalls and hosts, and indexes it with the facility, severity and time of each message.

## Streams

| Stream | Signal | Default | Index | What it receives |
| --- | --- | --- | --- | --- |
| `udp` | logs | on | `veloxagent-udp.syslog-server-v1` | datagrams on UDP 5140 (all interfaces) |
| `tcp` | logs | off | `veloxagent-tcp.syslog-server-v1` | messages on TCP 5140, newline or octet-counting framing |
| `unix` | logs | off | `veloxagent-unix.syslog-server-v1` | datagrams on a Unix socket under the agent state directory (Linux, macOS) |

Fluent Bit only delivers the raw message; RFC 3164 and RFC 5424 are told apart and parsed by the ingest pipeline. A message that matches neither keeps its text in `message` with `event.outcome: unparsed`.

## Fields

`@timestamp` (time of the message; arrival time when it has none), `message`, `host.name`, `process.name`, `process.pid`, `log.level`, `log.syslog.priority`, `log.syslog.facility.code`/`.name`, `log.syslog.severity.code`/`.name`, `log.syslog.version`, `log.syslog.msgid`, `log.syslog.structured_data` (RFC 5424), `event.original` (optional), `event.outcome`, `velox.*`.

RFC 3164 times carry no year or zone: the year is the current one and the zone is the `timezone` field (default UTC).

## Requirements

- Open the port in the host firewall and point the devices at the agent address. Ports below 1024 (the classic 514) need root or a capability.
- The unix stream creates `syslog-velox.syslog-server.unix.sock` in the agent state directory; point local senders (for example an rsyslog `omuxsock` action) at it.
- Raise `Socket receive buffer` for busy UDP senders.

## Dashboard

*Syslog server — overview*: events over time by host, top hosts, top programs and severity breakdown. It reads the `udp` stream.
