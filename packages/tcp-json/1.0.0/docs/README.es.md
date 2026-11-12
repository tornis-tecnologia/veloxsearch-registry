# TCP JSON

Abre un listener TCP para aplicaciones y scripts que envían eventos. Elija objetos JSON (un evento cada uno, con la hora tomada del objeto) o líneas de texto plano.

## Streams

| Stream | Señal | Por defecto | Índice | Qué recibe |
| --- | --- | --- | --- | --- |
| `json` | logs | activo | `veloxagent-json.tcp-json-v1` | objetos JSON en TCP 5170 (todas las interfaces) |
| `raw` | logs | apagado | `veloxagent-raw.tcp-json-v1` | líneas de texto plano en TCP 5171 |

## Campos

`@timestamp`, `message` y cada clave que incluya el emisor (los strings se mapean como keyword, así que `level`, `host`, `service` se pueden agregar), `velox.*`.

`json` toma la hora del evento de `time`, luego `timestamp`, luego `@timestamp` cuando es string (ISO 8601, `yyyy-MM-dd HH:mm:ss`, estilo access log, epoch en segundos o milisegundos); la clave de origen se elimina al interpretarla. Un valor que no se puede interpretar queda como se envió y el evento conserva la hora de llegada. El campo `timezone` aplica a horas sin desfase.

`raw` guarda cada línea en `message`; la hora es la de llegada.

Pruebe: `echo '{"time":"2026-11-12T10:15:02Z","level":"info","message":"hello"}' | nc localhost 5170`; raw: `echo "a plain line" | nc localhost 5171`.

## Requisitos

- Abra el puerto en el firewall del host; los streams `json` y `raw` usan puertos distintos para poder funcionar juntos.
- `json` necesita un objeto JSON completo por mensaje; un flujo de objetos concatenados sirve por TCP.

## Dashboard

*TCP JSON — resumen*: eventos en el tiempo, eventos por nivel y principales hosts (lee el stream `json`).
