# Fluent Forward

Un receptor Forward: instancias de Fluent Bit y Fluentd envían sus eventos a este agente, que los indexa en OpenSearch.

## Streams

| Stream | Señal | Por defecto | Índice / destino | Qué recolecta |
| --- | --- | --- | --- | --- |
| `logs` | logs | activado | `veloxagent-logs.fluent-forward-v1` | Eventos del protocolo Forward en el TCP 24224 (clave compartida opcional) |

## Campos

`@timestamp` (de `time`, `timestamp` o `ts`, ISO-8601 o epoch en segundos/milisegundos; hora de ingesta si no hay), `host.name` (de un `host` string o `hostname`), `event.outcome`, `velox.*`. Las demás claves se conservan tal cual.

## Requisitos

- El puerto (24224 por defecto) debe ser alcanzable por los emisores; el agente necesita permiso para escuchar.
- Con `shared_key`, los emisores deben usar Secure Forward con la misma clave.

## Dashboard

*Fluent Forward — overview*: eventos en el tiempo por host, hosts principales y registros por resultado.
