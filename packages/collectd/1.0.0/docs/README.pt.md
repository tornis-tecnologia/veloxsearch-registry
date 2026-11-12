# collectd

Recebe métricas do protocolo de rede do collectd de daemons collectd.

## Streams

| Stream | Sinal | Padrão | Destino | O que coleta |
| --- | --- | --- | --- | --- |
| `metrics` | metrics | ligada | `veloxagent-metrics.collectd-v1` | `host`, `plugin`, `plugin_instance`, `type`, `type_instance`, `values` |

## Campos

`listen` (padrão `0.0.0.0`), `port` (UDP, padrão 25826), `typesdb` (avançado, padrão `/usr/share/collectd/types.db`; vários caminhos permitidos) e `delete_after` (padrão 14d).

Campos indexados: `@timestamp`, `host`, `plugin`, `plugin_instance`, `type`, `type_instance`, `dsnames`, `dstypes`, `values`, `interval`, `velox.*`.

## Requisitos

- Linux. Um daemon collectd com o plugin de escrita `network` apontando para o agente.
- O arquivo `types.db` deve existir no host do agente.
