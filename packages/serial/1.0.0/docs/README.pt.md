# Porta serial

Lê linhas de um dispositivo serial como um sensor ou uma placa embarcada.

## Streams

| Stream | Sinal | Padrão | Destino | O que coleta |
| --- | --- | --- | --- | --- |
| `lines` | logs | ligada | `veloxagent-lines.serial-v1` | Cada linha serial como `message` |

## Campos

`file` (obrigatório, padrão `/dev/ttyUSB0`), `bitrate` (inteiro obrigatório, padrão 9600), `separator`, e avançados `format` (`none` ou `json`) e `min_bytes`. `delete_after` (padrão 30d).

Campos indexados: `@timestamp`, `message` (sem espaços nas pontas), `velox.*`.

## Requisitos

- Linux. O usuário do agente precisa de acesso ao dispositivo (normalmente o grupo `dialout`).
