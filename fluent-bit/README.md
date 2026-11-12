# Catálogo de plugins do Fluent Bit

Um arquivo YAML por plugin permitido, transcrito da página do plugin no manual
oficial (https://docs.fluentbit.io/manual/). Schema:
[`schemas/plugin.schema.json`](../schemas/plugin.schema.json). Regras: Spec 2.0 §9.

O VeloxMesh usa este catálogo para montar o formulário "adicionar
filter/processor", validar bindings de pacotes (R5, R6, R9, R12) e saber o
`event_type` que cada input emite. **Nada aqui é configuração**: é a descrição
dos parâmetros que a configuração pode ter.

## Layout

```
fluent-bit/<versão-dos-docs>/
  inputs/<name>.yaml        kind: input
  filters/<name>.yaml       kind: filter
  processors/<name>.yaml    kind: processor
  parsers/<format>.yaml     kind: parser_format   (json, regex, ltsv, logfmt)
  multiline/<name>.yaml     kind: multiline_parser (os embutidos: cri, docker, go, java, python, ruby)
```

`<versão-dos-docs>` é a versão do manual de onde a transcrição saiu (`5.2`).
Parâmetros que surgiram depois do Fluent Bit 3.2 levam `since:`; o console os
esconde para agentes mais antigos.

## Regras de autoria

1. **`name`** é o valor exato de `name:` na configuração (`tail`,
   `node_exporter_metrics`, `content_modifier`). Nome do arquivo = `name`.
2. **`docs_url`** é a página do plugin no manual. Só URLs `https://docs.fluentbit.io/`.
3. **`event_types`**: input → o que emite (`logs`, `metrics`, `traces`). Um
   input que emite registros de log com números (cpu, mem, disk, netif, proc,
   thermal, winstat) é `logs`. Só é `metrics` se a página diz que emite
   eventos de métrica (node_exporter_metrics, prometheus_scrape,
   fluentbit_metrics, …). filter/processor → o que aceita.
4. **`os`** (input): `linux`, `windows`, `darwin` conforme a página. Sem
   restrição na página = os três.
5. **`as_processor`** (filter): `true` se a página do filter ou a página
   "Filters as processors" diz que ele roda como processor anexado ao input.
6. **`requires`**: capacidades do host que a página exige (`root`, `systemd`,
   `docker_socket`, `podman_socket`, `kube_api`, `network_listen`, `gpu`, `ebpf`).
7. **`params`**: todos os parâmetros da tabela de configuração da página, com
   `key` igual ao da tabela (minúsculas, como no YAML do Fluent Bit),
   `type` (string, text, integer, number, bool, select, duration, size, regex,
   password), `default` quando a página dá um, `required`, `multi`
   (`no` | `join` | `repeat`), `options` para valores fechados, `since`,
   `advanced` para o que um operador raramente muda, `secret` para
   credenciais, `operator_settable: false` para o que só o pacote deve fixar
   (ex.: `db`, caminhos de estado).
   - `tag`, `alias`, `log_level`, `match` e as chaves `storage.*`,
     `threaded`, `processors` NÃO entram: são do compilador.
   - Para outputs nada é catalogado: o pacote nunca declara output.
8. **`description`** de plugin e de parâmetro em `en`, `es` e `pt` — uma frase.
9. **`verified: true`** só depois de conferir parâmetro a parâmetro contra a
   página. Transcrição parcial = `verified: false` e um comentário no topo
   dizendo o que falta.
10. **Allowlist.** Não entram: `exec`, `exec_wasi`, `dummy`, `random`,
    `stdin`; `lua`, `wasm`, `tensorflow`; `fluent_typed_scripting`.
    `scripts/check_catalog.py` recusa se aparecerem.

## Validar

```sh
python3 -I scripts/check_catalog.py            # todos
python3 -I scripts/check_catalog.py fluent-bit/5.2/inputs/tail.yaml
```
