# Spec 2.0 — pacotes de integração do veloxsearch-registry

**Status:** rascunho para revisão, 2026-11-12 · **Schemas:** [`schemas/`](../../schemas/) ·
**Exemplo de conformidade:** [`examples/custom-logs/1.0.0/`](examples/custom-logs/1.0.0/) ·
**Guia para o VeloxMesh:** [`../mesh-integration-guide.md`](../mesh-integration-guide.md)

Esta spec define o formato que o registry publica e o VeloxMesh lê. Um pacote
2.0 descreve **o que pode ser configurado** numa integração: streams de coleta
do Fluent Bit (input, parsers, filters, processors), backend no OpenSearch
(template, ingest pipeline, ciclo de vida) e dashboards. O registry não compila
nada; o core do VeloxSearch verifica, valida, instala o backend e compila o YAML
do Fluent Bit que o VeloxAgent aplica.

"DEVE", "NÃO DEVE" e "PODE" têm o sentido da RFC 2119. Cada regra que um JSON
Schema não consegue expressar tem um número `Rn` (§14), implementado por
`scripts/validate_v2.py`.

---

## 1. Relação com o formato 1.x

| | 1.x (`integrations/`, `catalog.json`) | 2.0 (`packages/`) |
| --- | --- | --- |
| Consumidor | DaemonSet do cluster (receitas do core) | VeloxMesh / VeloxAgent |
| Configuração | template de texto + 8 tokens + `${var}` escalares | estrutura tipada, serializada pelo core |
| Formato Fluent Bit | clássico | YAML (≥ 3.2) |
| Versões | uma por id | várias, imutáveis |
| Nome dos artefatos | `veloxagent-<integração>-<sinal>-v<major>` (ADR-071) | `veloxagent-<stream>.<integração>-v<major>` |

As duas árvores coexistem. `integrations/` continua presa às receitas do core
pelos testes golden e não é editada à mão. Nada nesta spec muda o formato 1.x.

---

## 2. Layout

```
packages/
  index.json                         gerado (§10)
  <id>/<versão>/                     uma versão de um pacote; imutável depois de publicada
    manifest.yaml                    §4
    changelog.yaml                   schemas/changelog.schema.json
    docs/README.<en|es|pt>.md
    img/icon.svg
    streams/<stream>/
      stream.yaml                    §5
      index-template.json            §8.2
      ingest-pipeline.json           §8.3
      sample-event.json              documento como chega ao OpenSearch
      test/<caso>.log                entrada de teste do pipeline (F3)
      test/<caso>.expected.json      saída esperada do _simulate (F3)
    dashboards/<nome>.ndjson         §8.5
fluent-bit/<versão-fb>/
  inputs/<nome>.yaml                 catálogo de plugins (§9)
  filters/<nome>.yaml
  processors/<nome>.yaml
  parsers/<formato>.yaml
  multiline/<nome>.yaml
```

- **R1** `manifest.id` é igual ao diretório `<id>` e `manifest.version` ao diretório `<versão>`.
- **R2** Todo arquivo da versão, exceto `manifest.yaml`, está em `files:` com o sha256 correto, e nada além deles existe no diretório. Sem arquivos ocultos. `scripts/inventory.py` gera a lista.

---

## 3. Conceitos

- **Integração (pacote):** uma fonte com sentido para o operador (`nginx`, `system`, `custom-logs`).
- **Stream:** a unidade que o operador liga e desliga (≈ data stream do Elastic). Um input do Fluent Bit, seus campos, parsers, cadeia de processamento e backend.
- **Campo:** um parâmetro configurável, mostrado como controle de formulário e ligado (**bind**) a um destino: chave do plugin, template, pipeline ou ciclo de vida.
- **`signal`:** o que a stream é para o operador (`logs`, `metrics`, `traces`). Categoria, filtros e dashboards.
- **`event_type`:** o que o plugin emite de fato. **Decide o output**: `logs`/`traces` → `opensearch`; `metrics` → `opentelemetry` para o OTel Collector do deployment (guia §9).
- **Ativação:** o que uma política guarda para um pacote (§13).

---

## 4. Manifesto (`manifest.yaml`)

Schema: [`manifest.schema.json`](../../schemas/manifest.schema.json). Exemplo: [`examples/custom-logs/1.0.0/manifest.yaml`](examples/custom-logs/1.0.0/manifest.yaml).

| Campo | Obrigatório | Notas |
| --- | --- | --- |
| `spec_version` | sim | `"2.0"` |
| `id` | sim | `^[a-z0-9]([a-z0-9-]*[a-z0-9])?$`, até 48 |
| `version` | sim | semver; regras de mudança em §11 |
| `release` | sim | `ga`, `beta`, `experimental` |
| `title`, `summary` | sim | i18n |
| `description` | não | i18n |
| `categories` | sim | lista fechada (schema) |
| `icon`, `owner`, `license`, `docs`, `changelog` | não | caminhos relativos à versão |
| `compatibility` | sim | `min_mesh_version`, `min_agent_version`, `min_fluent_bit_version` (≥ 3.2.0), `os` |
| `streams` | sim | ids, na ordem de exibição; cada um em `streams/<id>/` |
| `dashboards` | não | ndjson de saved objects (§8.5) |
| `files` | sim | inventário (R2) |
| `signature` | sim | §12 |

O manifesto NÃO DEVE declarar output, endpoint, TLS do output, credencial do
coletor nem `[SERVICE]`: isso é do VeloxMesh (o schema recusa chaves desconhecidas).

- **R3** Cada id em `streams` tem `streams/<id>/stream.yaml` com o mesmo `id`; nenhum diretório de stream fica fora da lista.
- **R4** `compatibility.min_fluent_bit_version` ≥ `3.2.0`. `compatibility.os` contém o `os` de toda stream.

---

## 5. Stream (`streams/<id>/stream.yaml`)

Schema: [`stream.schema.json`](../../schemas/stream.schema.json). Exemplo: [`examples/custom-logs/1.0.0/streams/log/stream.yaml`](examples/custom-logs/1.0.0/streams/log/stream.yaml).

```yaml
id: log                      # ^[a-z][a-z0-9_-]{0,31}$, sem ponto
title: {en, es, pt}
signal: logs
event_type: logs
enabled: true                # pré-selecionada
os: [linux, windows, darwin]
input:    {plugin, fixed, fields}
parsers:  [...]              # §5.3
multiline_parsers: [...]
parser_field: {default, title, group}
processors: {defaults: [...], allow: [...]}
backend:  {index_template, ingest_pipeline, custom_hooks, lifecycle, fields}
```

### 5.1 Input

- `plugin`: nome do plugin do Fluent Bit, presente no catálogo (§9).
- `fixed`: chaves que o pacote fixa e o operador não muda. Valores escalares ou listas; strings PODEM usar as referências de contexto (§7).
- `fields`: campos configuráveis (§6).

O compilador acrescenta `tag: {stream_tag}` e `parser:` (§5.3). O pacote NÃO DEVE declarar `tag`.

- **R5** `input.plugin` existe no catálogo de plugins para `compatibility.min_fluent_bit_version`, é `kind: input`, e o `os` da stream está contido no `os` do plugin.
- **R9** `event_type` da stream está em `event_types` do plugin. Plugins que emitem mais de um tipo (`opentelemetry`) exigem uma stream por tipo.

### 5.2 Processors

`processors.defaults` é a cadeia padrão, em ordem. Cada item tem `id`, `plugin`
(filter ou processor do catálogo), `title`, `enabled` (padrão `true`), `locked`
(não pode ser desligado), `fixed` e `fields`. `processors.allow` lista os plugins
que o operador pode acrescentar depois dos padrões.

O compilador anexa filters como processors do input sempre que o catálogo marca
`as_processor: true` (evita que o `Match` de uma integração pegue registros de
outra); caso contrário, gera filter global com `match: {stream_tag}`.

- **R12** Todo plugin em `defaults` e `allow` existe no catálogo, é `filter` ou `processor`, aceita o `event_type` da stream e não executa código (§9).
- **R13** Ids de processors são únicos na stream.

### 5.3 Parsers

`parsers` e `multiline_parsers` usam as chaves do manual do Fluent Bit. O
compilador emite cada um em `parsers:` / `multiline_parsers:` com nome
`<integração>.<stream>.<nome>`. `parser_field` gera o select de parser do input
com as opções `none` + `parsers`; o valor escolhido vira `parser:` do input.

- **R14** Nomes de parser são únicos na stream; `parser_field.default` é `none` ou um nome de `parsers`; `multiline_parsers` com `type: regex` têm regras que começam em `start_state`.

### 5.4 Backend

Obrigatório para `event_type` `logs`/`traces`; proibido (exceto omitido) para `metrics`, que não cria nada no OpenSearch. Detalhes em §8.

---

## 6. Campos e bindings

Schema: `common.schema.json#/$defs/field`.

### 6.1 Tipos

| `type` | Valor | Validação no core |
| --- | --- | --- |
| `string` | string de uma linha | `pattern` opcional |
| `text` | multilinha | só para binding que aceita multilinha |
| `integer` / `number` | i64 / f64 | `min`, `max` |
| `bool` | `true`/`false` | |
| `select` | um de `options` (ou `options_from`) | |
| `duration` | `^[0-9]+(ms\|s\|m\|h\|d)$` | |
| `size` | `^[0-9]+([kKmMgGtT][bB]?\|[bB])?$` | |
| `regex` | regex | compila |
| `password` | segredo | sem `default`; nunca na revisão |
| `yaml` | objeto | só `group: advanced`, `bind: {merge: true}` |

Atributos: `name` (único no escopo: input, cada processor, backend), `title`,
`description`, `placeholder`, `required`, `multi`, `default`, `group`, `since`,
`show_if`, `options`, `options_from`, `min`, `max`, `pattern`, `bind`.

Nenhum valor escalar PODE conter caractere de controle ou quebra de linha
(exceto `text`), porque vira chave de configuração.

### 6.2 Bindings

| Binding | Efeito no core |
| --- | --- |
| `{key: k}` | define a chave `k` do plugin |
| `{key: k, join: ","}` | lista → uma string unida |
| `{key: k, repeat: true}` | lista → lista YAML (chave multivalor) |
| `{key: k, omit_if: v}` | omite a chave quando o valor é `v` |
| `{key: k, prefix: "p "}` | prefixa cada valor |
| `{merge: true}` | (`yaml`) funde o objeto nas chaves do plugin |
| `{template: settings.a.b}` / `{template: mappings.a.b}` | define o caminho no component template `N@package` |
| `{pipeline_toggle: tag}` | `false` remove do pipeline o processor com esse `tag` |
| `{pipeline_param: tag.campo}` | define `campo` do processor com esse `tag` |
| `{lifecycle: delete_after}` | sobrepõe o padrão de `backend.lifecycle` |

- **R6** Binding `key` aponta para um parâmetro do plugin no catálogo, com tipo compatível; `operator_settable: false` só aceita `fixed`; parâmetro `secret` só aceita campo `password`; `multi: true` exige `join` ou `repeat` coerente com o `multi` do parâmetro; a chave não está também em `fixed`. `merge` só aceita chaves do catálogo fora de `fixed`.
- **R8** `default` tem o tipo do campo; default de `select` está nas opções; `show_if` aponta para um campo do mesmo escopo.
- **R15** `pipeline_toggle`/`pipeline_param` apontam para um `tag` existente em `ingest-pipeline.json`; `pipeline_toggle` só em campo `bool`. `template` só em stream com `index_template`. `lifecycle` só em stream com `backend.lifecycle`.

---

## 7. Referências de contexto (conjunto fechado)

Só em strings de `fixed`. Resolvidas pelo core na compilação.

| Referência | Valor |
| --- | --- |
| `{stream_tag}` | `velox.<integração>.<stream>` |
| `{artifact}` | `veloxagent-<stream>.<integração>-v<major>` |
| `{state_dir}` | diretório de estado do Fluent Bit no agente |
| `{integration}`, `{stream}`, `{package_version}` | identidade |

- **R7** Qualquer outra `{...}` em `fixed` é erro. `${...}` é proibido em pacotes (variáveis de ambiente são do core: credenciais e segredos).

---

## 8. Backend e nomes

### 8.1 Nome do artefato

`N = veloxagent-<stream>.<integração>-v<major>`, onde `<major>` é a major da
versão do pacote. O mesmo `N` nomeia data stream, component template
`N@package`, index template, ingest pipeline, política ISM e index pattern. O
prefixo `veloxagent-` é o que a conta do coletor pode escrever (ADR-070).

- **R22** `len(N) ≤ 200` e `N` é um nome de índice válido do OpenSearch.

### 8.2 `index-template.json`

Corpo de um component template do OpenSearch: `{"template": {"settings": {...}, "mappings": {...}}}`.
O core o instala como `N@package`, com os bindings `template` aplicados, e cria o
index template `N` com `composed_of: [N@package, N@custom]`, `index_patterns: [N]`,
`data_stream: {}` e `index.default_pipeline: N`. O pacote NÃO DEVE declarar
`index_patterns`, `data_stream`, `composed_of` nem `default_pipeline`.

### 8.3 `ingest-pipeline.json`

Corpo de um ingest pipeline. Processors que campos ligam, desligam ou ajustam
DEVEM ter `tag`. O core acrescenta, no fim, um processor `pipeline` que chama
`N@custom`.

### 8.4 Ciclo de vida e hooks

`backend.lifecycle` (`rollover_max_size`, `rollover_max_age`,
`rollover_max_docs`, `delete_after`) vira a política ISM `N`. Com
`custom_hooks: true` (padrão) o core cria `N@custom` (component template e
pipeline vazios) se não existirem e nunca os sobrescreve: são do operador.

### 8.5 Dashboards (saved objects)

- O pacote NÃO DEVE incluir index patterns. O core cria um por stream `logs`/`traces`, com id e título `N`.
- Saved objects referenciam o index pattern de uma stream pelo id `stream:<stream>`.
- Ids de saved objects são locais ao pacote (`overview`, `events-over-time`). O core instala como `veloxagent-<integração>-v<major>-<id>` e reescreve todas as referências, incluindo `searchSourceJSON`.
- Dashboards de streams `metrics` consultam a datasource Prometheus do deployment e filtram pelos rótulos `velox_integration` e `velox_stream`.

- **R18** Toda referência `stream:<id>` aponta para uma stream `logs`/`traces` do pacote; ids locais são únicos no pacote; nenhuma referência aponta para fora do pacote.
- **R10** Stream `metrics` não tem `index_template`, `ingest_pipeline`, `lifecycle`, `custom_hooks` nem campos de backend (também no schema).
- **R11** Stream `logs`/`traces` tem `index_template` (também no schema); se o pipeline existir, o template não fixa `default_pipeline`.

---

## 9. Catálogo de plugins do Fluent Bit

Schema: [`plugin.schema.json`](../../schemas/plugin.schema.json). Um arquivo por
plugin em `fluent-bit/<versão-fb>/`, transcrito da página do plugin no manual
(`docs_url`), com `verified: true` depois de conferido parâmetro a parâmetro.

- `kind`: `input`, `filter`, `processor`, `parser_format`, `multiline_parser`.
- `event_types`: o que o input emite, ou o que o filter/processor aceita. É a fonte do `event_type` das streams.
- `as_processor`: se o filter roda anexado ao input.
- `requires`: capacidades do host (`root`, `systemd`, `docker_socket`, `kube_api`...).
- `params`: chave, tipo, `multi` (`no`/`join`/`repeat`), padrão, `since`, `secret`, `operator_settable`.

**Allowlist.** Nada que execute código no host entra no catálogo, e o core recusa
stream que o referencie:

| Excluído | Motivo |
| --- | --- |
| inputs `exec`, `exec_wasi` | executam comando / WASM |
| filters `lua`, `wasm` | executam script |
| processor `fluent_typed_scripting` | executa Lua |
| filter `tensorflow` | executa modelo; reavaliar |
| inputs `dummy`, `random`, `stdin` | só para teste |

- **R16** O catálogo não contém plugin excluído; cada `docs_url` é do manual oficial.

---

## 10. Catálogo de pacotes (`packages/index.json`)

Schema: [`index.schema.json`](../../schemas/index.schema.json). Gerado por
`scripts/build_index.py` a partir dos manifestos; nunca editado à mão. Para cada
versão: `release`, `path`, `manifest_sha256`, mínimos de compatibilidade, `os`,
`signals`, `event_types`. `latest` é a maior versão `ga` (ou a maior, se nenhuma
for `ga`).

O consumidor escolhe a maior versão cujos mínimos ele e os agentes da política
satisfazem, e confere `manifest_sha256` contra o manifesto baixado.

---

## 11. Versionamento e compatibilidade

Uma versão publicada é **imutável** (R19). Mudança = nova versão.

| Mudança | Versão mínima |
| --- | --- |
| Textos, dashboards, padrões de campo, novo campo opcional, nova stream, novo processor opcional | patch / minor |
| Campo novo `required` sem `default` | minor (o upgrade pede o valor) |
| Novo campo de mapping, novo processor de pipeline | minor |
| Remover ou mudar o tipo de um campo de mapping; mudar o `id` de uma stream | **major** (novo `N`) |
| Remover campo de formulário ou stream | minor, com entrada `breaking-change` no changelog |

- **R19** Versão já publicada em `main` não muda (CI compara com `main`).
- **R20** Dentro de uma major, o mapping de cada stream é aditivo em relação à versão anterior: nenhum campo removido, nenhum tipo alterado.
- **R21** `version` é maior que todas as versões existentes do mesmo pacote.

Regras do upgrade do lado do Mesh: guia §10.

---

## 12. Assinatura 2.0

Mesmo algoritmo do 1.x ([signing.md do core](https://github.com/tornis-tecnologia/veloxsearch-oss/blob/main/docs/integrations/signing.md)), com a enumeração de arquivos vinda do inventário:

1. `manifest.yaml`: parse, remover `signature`, serializar com JCS (RFC 8785), `sha256`.
2. Para cada `files[].path`: `sha256` dos bytes brutos (o mesmo valor do inventário).
3. Lista `[[relpath, "sha256:<hex>"], ...]` com o manifesto como `manifest.yaml`, ordenada por `relpath` em bytes, serializada com JCS; `digest = SHA-256(lista)`.
4. `signature.value = base64(ed25519_sign(chave, digest))`, chave `velox-registry-2026-10`.

Verificação no core: manifesto válido, `key_id` conhecido, cada arquivo do
inventário presente e com o hash certo, digest recalculado, assinatura confere.
Qualquer falha recusa o pacote inteiro. `velox sign` / `velox verify` precisam
ganhar suporte a 2.0 (core).

---

## 13. Ativação

Schema: [`activation.schema.json`](../../schemas/activation.schema.json). Exemplo: [`examples/activations/custom-logs.json`](examples/activations/custom-logs.json).

O core guarda na revisão da política, por pacote: `package_id`,
`package_version`, `spec_version` e, por stream, `enabled`, valores do input,
`parser`, a cadeia de processors (padrões por `id`, acrescentados por `plugin`)
e valores de backend. Campo `password` guarda só `{"$secret": "<id>"}`. Stream
ausente = desligada; ativação vazia = streams com `enabled: true` e valores
padrão.

---

## 14. Regras de validação

Além dos schemas, `scripts/validate_v2.py` (F3) aplica:

| Regra | Resumo | Seção |
| --- | --- | --- |
| R1 | id/versão iguais aos diretórios | §2 |
| R2 | inventário completo e correto | §2 |
| R3 | streams listadas = diretórios, ids iguais | §4 |
| R4 | FB mínimo ≥ 3.2.0; `os` coerente | §4 |
| R5 | plugin do input no catálogo e no SO | §5.1 |
| R6 | bindings `key`/`merge` válidos contra o catálogo | §6.2 |
| R7 | só referências de contexto do conjunto fechado; sem `${...}` | §7 |
| R8 | defaults com o tipo certo; `show_if` válido | §6.1 |
| R9 | `event_type` emitido pelo plugin | §5.1 |
| R10 | stream `metrics` sem backend no OpenSearch | §8.5 |
| R11 | stream `logs`/`traces` com template | §8.5 |
| R12 | processors no catálogo, compatíveis, sem executar código | §5.2 |
| R13 | ids de processor únicos | §5.2 |
| R14 | parsers coerentes | §5.3 |
| R15 | bindings de backend apontam para tags/paths existentes | §6.2 |
| R16 | catálogo sem plugin excluído | §9 |
| R17 | todo texto de UI em `en`, `es` e `pt` | — |
| R18 | referências de saved objects internas e válidas | §8.5 |
| R19 | versão publicada imutável | §11 |
| R20 | mapping aditivo dentro da major | §11 |
| R21 | versão nova maior que as existentes | §11 |
| R22 | nome `N` válido e ≤ 200 | §8.1 |
| R23 | changelog tem a entrada da própria versão | — |
| R24 | todo `ingest-pipeline.json` passa nos casos de `test/` via `_simulate` | §2 |

---

## 15. Conformidade

| Ferramenta | Fase | O que garante |
| --- | --- | --- |
| `scripts/check_spec.py` | F1 | schemas válidos, exemplo conforme, variantes inválidas recusadas |
| `scripts/inventory.py` | F1 | gera e confere `files:` |
| `scripts/validate_v2.py` | F3 | R1–R24 |
| `scripts/build_index.py` | F3 | `packages/index.json` |
| `scripts/render.py` | F3 | compilador de referência: pacote + ativação → YAML do Fluent Bit; CI roda `fluent-bit --dry-run` |
