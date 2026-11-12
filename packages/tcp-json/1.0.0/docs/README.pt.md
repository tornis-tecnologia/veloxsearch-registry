# TCP JSON

Abre um listener TCP para aplicações e scripts que enviam eventos. Escolha objetos JSON (um evento cada, com o horário tomado do objeto) ou linhas de texto puro.

## Streams

| Stream | Sinal | Padrão | Índice | O que recebe |
| --- | --- | --- | --- | --- |
| `json` | logs | ligado | `veloxagent-json.tcp-json-v1` | objetos JSON em TCP 5170 (todas as interfaces) |
| `raw` | logs | desligado | `veloxagent-raw.tcp-json-v1` | linhas de texto puro em TCP 5171 |

## Campos

`@timestamp`, `message` e cada chave que o emissor incluir (strings são mapeadas como keyword, então `level`, `host`, `service` podem ser agregados), `velox.*`.

`json` toma o horário do evento de `time`, depois `timestamp`, depois `@timestamp` quando é string (ISO 8601, `yyyy-MM-dd HH:mm:ss`, estilo access log, epoch em segundos ou milissegundos); a chave de origem é removida após a interpretação. Um valor que não pode ser interpretado permanece como enviado e o evento mantém o horário de chegada. O campo `timezone` vale para horários sem deslocamento.

`raw` guarda cada linha em `message`; o horário é o de chegada.

Teste: `echo '{"time":"2026-11-12T10:15:02Z","level":"info","message":"hello"}' | nc localhost 5170`; raw: `echo "a plain line" | nc localhost 5171`.

## Requisitos

- Abra a porta no firewall do host; os streams `json` e `raw` usam portas diferentes para poderem rodar juntos.
- `json` precisa de um objeto JSON completo por mensagem; um fluxo de objetos concatenados serve por TCP.

## Dashboard

*TCP JSON — visão geral*: eventos no tempo, eventos por nível e principais hosts (lê o stream `json`).
