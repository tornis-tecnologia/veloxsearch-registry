# Endpoint HTTP

Recibe eventos JSON enviados por POST a un endpoint HTTP del agente.

## Streams

| Stream | Señal | Por defecto | Índice | Qué recibe |
| --- | --- | --- | --- | --- |
| `json` | logs | activo | `veloxagent-json.http-endpoint-v1` | cuerpos POST con un objeto JSON o una lista de objetos, en el puerto 8888 |

## Campos

`@timestamp`, `message`, cada clave que incluya el emisor (los strings se mapean como keyword), `source.address` (con `Registrar la dirección del cliente` activo), `velox.*`.

La hora del evento sale de `time`, luego `timestamp`, luego `@timestamp` cuando es string (ISO 8601, `yyyy-MM-dd HH:mm:ss`, estilo access log, epoch en segundos o milisegundos); un valor que no se puede interpretar queda como se envió y el evento conserva la hora de llegada. El campo `timezone` aplica a horas sin desfase.

Pruebe: `curl -X POST http://localhost:8888/ -H 'Content-Type: application/json' -d '{"time":"2026-11-12T10:15:02Z","level":"info","message":"hello"}'`.

## Requisitos

- Abra el puerto en el firewall del host. El listener habla HTTP plano: póngalo detrás de un proxy TLS si da a una red no confiable, o exija un token OAuth 2.0 (JWKS) en los campos avanzados.
- El catálogo de Fluent Bit no lista claves TLS ni basic-auth para este input, por eso el paquete no las expone.
- No se ofrece la opción de etiqueta desde el registro (`tag_key`): desviaría los eventos del índice del stream.

## Dashboard

*Endpoint HTTP — resumen*: eventos en el tiempo, eventos por nivel, principales hosts y principales direcciones de cliente.
