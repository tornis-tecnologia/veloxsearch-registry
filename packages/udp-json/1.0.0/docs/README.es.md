# UDP JSON

Abre un listener UDP para emisores que envían sin esperar respuesta. Elija objetos JSON (un evento cada uno, con la hora tomada del objeto) o líneas de texto plano.

## Streams

| Stream | Señal | Por defecto | Índice | Qué recibe |
| --- | --- | --- | --- | --- |
| `json` | logs | activo | `veloxagent-json.udp-json-v1` | objetos JSON en UDP 5170 (todas las interfaces) |
| `raw` | logs | apagado | `veloxagent-raw.udp-json-v1` | líneas de texto plano en UDP 5171 |

## Campos

`@timestamp`, `message` y cada clave que incluya el emisor (los strings se mapean como keyword, así que `level`, `host`, `service` se pueden agregar), `velox.*`.

`json` toma la hora del evento de `time`, luego `timestamp`, luego `@timestamp` cuando es string (ISO 8601, `yyyy-MM-dd HH:mm:ss`, estilo access log, epoch en segundos o milisegundos); la clave de origen se elimina al interpretarla. Un valor que no se puede interpretar queda como se envió y el evento conserva la hora de llegada. El campo `timezone` aplica a horas sin desfase.

`raw` guarda cada línea en `message`; la hora es la de llegada.

Pruebe: `echo '{"time":"2026-11-12T10:15:02Z","level":"info","message":"hello"}' | nc -u -w1 localhost 5170`; raw: `echo "a plain line" | nc -u -w1 localhost 5171`.

## Requisitos

- Abra el puerto en el firewall del host; los streams `json` y `raw` usan puertos distintos para poder funcionar juntos.
- `json` necesita un objeto JSON completo por mensaje; un flujo de objetos concatenados sirve por TCP.
- UDP no garantiza la entrega y cada datagrama debe caber en el búfer: suba `Tamaño máximo del búfer` para objetos grandes.

## Dashboard

*UDP JSON — resumen*: eventos en el tiempo, eventos por nivel y principales hosts (lee el stream `json`).
