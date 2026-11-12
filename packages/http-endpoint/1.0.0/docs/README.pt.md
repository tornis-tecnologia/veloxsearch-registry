# Endpoint HTTP

Recebe eventos JSON enviados por POST a um endpoint HTTP do agente.

## Streams

| Stream | Sinal | Padrão | Índice | O que recebe |
| --- | --- | --- | --- | --- |
| `json` | logs | ligado | `veloxagent-json.http-endpoint-v1` | corpos POST com um objeto JSON ou uma lista de objetos, na porta 8888 |

## Campos

`@timestamp`, `message`, cada chave que o emissor incluir (strings são mapeadas como keyword), `source.address` (com `Registrar o endereço do cliente` ligado), `velox.*`.

O horário do evento vem de `time`, depois `timestamp`, depois `@timestamp` quando é string (ISO 8601, `yyyy-MM-dd HH:mm:ss`, estilo access log, epoch em segundos ou milissegundos); um valor que não pode ser interpretado permanece como enviado e o evento mantém o horário de chegada. O campo `timezone` vale para horários sem deslocamento.

Teste: `curl -X POST http://localhost:8888/ -H 'Content-Type: application/json' -d '{"time":"2026-11-12T10:15:02Z","level":"info","message":"hello"}'`.

## Requisitos

- Abra a porta no firewall do host. O listener fala HTTP puro: coloque-o atrás de um proxy TLS se ele atende uma rede não confiável, ou exija um token OAuth 2.0 (JWKS) nos campos avançados.
- O catálogo do Fluent Bit não lista chaves de TLS nem de basic-auth para este input, por isso o pacote não as expõe.
- A opção de tag a partir do registro (`tag_key`) não é oferecida: desviaria os eventos do índice do stream.

## Dashboard

*Endpoint HTTP — visão geral*: eventos no tempo, eventos por nível, principais hosts e principais endereços de cliente.
