# Guia: como o VeloxMesh lê e aplica integrações do registry (Spec 2.0)

**Para:** quem desenvolve o VeloxMesh (console + core + serviço Mesh) e o
VeloxAgent.
**Status:** rascunho v1, 2026-11-12. A Spec 2.0 formal está em `docs/spec/README.md`
e `schemas/`; onde este guia e a spec divergirem, vale a spec.
**Base:** documento "Velox Mesh, Velox Agent e integrações"
(https://claude.ai/artifact/6xXfT5pPYUxdjLsGHKwyEU) e ADRs 039, 068–073 do
veloxsearch-oss.

O registry deixa de entregar "um template fixo por integração" e passa a
entregar **o que pode ser configurado** em cada integração, com tipos, padrões
e textos. O VeloxMesh lê esse catálogo, gera o formulário (como o Fleet do
Elastic), guarda o que o operador escolheu na revisão da política, instala o
backend no OpenSearch e compila o YAML do Fluent Bit que o agente aplica.

---

## 1. Quem faz o quê

| Peça | Responsabilidade |
| --- | --- |
| **Registry** | Publica pacotes versionados e assinados: streams, campos configuráveis, parsers, filters/processors padrão e permitidos, assets de backend, dashboards. Publica o catálogo de plugins do Fluent Bit (allowlist com parâmetros tipados). Não compila nada. |
| **Core** | Baixa o catálogo e os pacotes, **verifica assinatura**, serve o formulário ao console, valida valores, instala o backend com conta admin, **compila** a configuração do Fluent Bit, entrega a revisão ao serviço Mesh. Mesmo papel que tem hoje (só o core lê pacotes e fala com OpenSearch como admin). |
| **Console** | Tela de escolha da integração (catálogo), formulário gerado, tela de upgrade, edição da ativação. |
| **Serviço Mesh** | Guarda revisões e segredos, serve no check-in. Não compila, não fala com OpenSearch, não lê o registry. |
| **VeloxAgent** | Aplica o YAML compilado com dry-run e rollback; exporta segredos como variáveis de ambiente para o Fluent Bit; reporta versão do Fluent Bit e SO. |

A fronteira de segurança continua a mesma: o core só compila sobre pacote
verificado, e nada vindo do registry é código executável no host.

---

## 2. Descobrir integrações: o catálogo

O core lê `packages/index.json` a partir de `VELOX_REGISTRY_URL` (HTTP ou
`file://`, mesma regra do catálogo 1.x: registry inalcançável = catálogo em
cache marcado `stale`, nunca erro fatal).

```json
{
  "spec_version": "2.0",
  "generated_at": "2026-11-12T00:00:00Z",
  "packages": [
    {
      "id": "custom-logs",
      "title":   {"en": "Custom logs", "es": "Logs personalizados", "pt": "Logs personalizados"},
      "summary": {"en": "...", "es": "...", "pt": "..."},
      "categories": ["custom", "logs"],
      "icon": "custom-logs/1.0.0/img/icon.svg",
      "latest": "1.0.0",
      "versions": [
        {
          "version": "1.0.0",
          "release": "ga",
          "path": "custom-logs/1.0.0/",
          "manifest_sha256": "…",
          "min_mesh_version": "0.15.0",
          "min_agent_version": "0.2.0",
          "min_fluent_bit_version": "3.2.0",
          "os": ["linux", "windows", "darwin"],
          "event_types": ["logs"]
        }
      ]
    }
  ]
}
```

**Escolha de versão:** maior `version` cujos `min_*` são satisfeitos pelo core
e pelos agentes da política. `release` ∈ `ga | beta | experimental`; o console
esconde não-GA por padrão. `os` e `event_types` servem de filtro na tela.

O `index.json` é só uma vitrine. A verdade de cada versão é o `manifest.yaml`
dela, que é assinado. Conferir `manifest_sha256` do índice contra o manifesto
baixado.

---

## 3. Baixar e verificar um pacote

```
packages/<id>/<versão>/
  manifest.yaml              identidade, compatibilidade, lista de streams,
                             inventário de arquivos (sha256), assinatura
  changelog.yaml
  docs/README.{en,es,pt}.md
  img/icon.svg
  streams/<stream>/stream.yaml
  streams/<stream>/index-template.json
  streams/<stream>/ingest-pipeline.json
  streams/<stream>/sample-event.json
  dashboards/*.ndjson
```

Ordem obrigatória:

1. Baixar `manifest.yaml`.
2. Verificar a assinatura ed25519 sobre o manifesto canônico, com a chave
   compilada no binário (`key_id` desconhecido, sem assinatura e adulterado =
   três recusas distintas, como hoje).
3. Baixar cada arquivo do `files:` do manifesto e conferir o sha256. Arquivo
   fora do inventário é ignorado; arquivo do inventário ausente ou divergente
   recusa o pacote inteiro.
4. Validar contra os JSON Schemas da Spec 2.0 (`schemas/`).
5. Só então ler qualquer texto para mostrar ao operador.

Versão publicada é imutável: o core pode guardar em cache por
`(id, versão, manifest_sha256)` para sempre.

---

## 4. O que um pacote declara

### 4.1 Stream

Uma stream é a unidade que o operador liga ou desliga (≈ data stream do
Elastic). Cada uma tem um input do Fluent Bit, parsers, cadeia de
processamento e backend próprios.

```yaml
# packages/custom-logs/1.0.0/streams/log/stream.yaml
id: log
title:       {en: Log files, es: Archivos de log, pt: Arquivos de log}
description: {en: "...", es: "...", pt: "..."}
signal: logs                    # logs | metrics | traces — o que a stream É (nome, tela, dashboards)
event_type: logs                # logs | metrics | traces — o que o plugin EMITE (decide o output, §9)
enabled: true                   # pré-selecionada no formulário
os: [linux, windows, darwin]

input:
  plugin: tail                  # tem de existir no catálogo fluent-bit/
  fixed:                        # chaves que o operador não muda
    db: "{state_dir}/tail-{stream_tag}.db"
    mem_buf_limit: 5MB
  fields:
    - name: paths
      type: string
      multi: true
      required: true
      default: [/var/log/*.log]
      bind: {key: path, join: ","}
      title: {en: Paths, es: Rutas, pt: Caminhos}
    - name: exclude_paths
      type: string
      multi: true
      group: advanced
      bind: {key: exclude_path, join: ","}
    - name: multiline
      type: select
      options: [none, docker, cri, go, java, python, ruby]
      default: none
      bind: {key: multiline.parser, omit_if: none}
    - name: read_from_head
      type: bool
      default: false
      group: advanced
      bind: {key: read_from_head}

parsers:                        # definidos pelo pacote, oferecidos num select
  - name: json
    format: json
    time_key: time
    time_format: "%Y-%m-%dT%H:%M:%S.%L%z"
parser_field: {default: none}  # select gerado: none + `parsers`; vira `parser:` do input

processors:
  defaults:                     # cadeia padrão, cada item liga/desliga
    - id: exclude
      plugin: grep
      enabled: false
      title: {en: Exclusion rules, es: Reglas de exclusión, pt: Regras de exclusão}
      fields:
        - name: rules
          type: string
          multi: true
          placeholder: "log ^DEBUG"
          bind: {key: exclude, repeat: true}
  allow: [grep, modify, record_modifier, nest, parser, content_modifier, sql, throttle]

backend:                        # dashboards ficam no manifesto (`dashboards:`), não na stream
  index_template: index-template.json
  ingest_pipeline: ingest-pipeline.json
  custom_hooks: true            # cria <nome>@custom (pipeline e component template)
  lifecycle:                    # padrões da política ISM
    rollover_max_size: 10gb
    rollover_max_age: 1d
    delete_after: 30d
  fields:
    - name: replicas
      type: integer
      default: 1
      min: 0
      bind: {template: settings.index.number_of_replicas}
    - name: keep_original
      type: bool
      default: true
      bind: {pipeline_toggle: remove_original}   # `tag` de um processor do pipeline
```

Pacote completo e válido: `docs/spec/examples/custom-logs/1.0.0/` no registry. A
definição normativa de cada chave está em `docs/spec/README.md` e nos JSON
Schemas de `schemas/`.

### 4.2 Tipos de campo

| `type` | Widget | Valor | Observação |
| --- | --- | --- | --- |
| `string` | texto | string de uma linha | `pattern` opcional |
| `text` | área de texto | multilinha | só para campos que o binding aceita multilinha (ex.: mappings extras) |
| `integer`, `number` | número | i64 / f64 | `min`, `max` |
| `bool` | toggle | bool | |
| `select` | lista | um de `options` | `options_from: parsers` permitido |
| `duration` | texto com validação | `30s`, `5m`, `1d` | |
| `size` | texto com validação | `5MB`, `10gb` | |
| `regex` | texto | regex válida | o core compila para validar |
| `password` | texto oculto | segredo | nunca entra na revisão (ver §6) |
| `yaml` | editor | objeto | só em `group: advanced`, validado contra o catálogo do plugin |

Atributos comuns: `name`, `title`, `description`, `placeholder`, `required`,
`default`, `multi`, `group` (`general` / `advanced`), `since` (versão mínima do
Fluent Bit), `show_if: {field: x, equals: y}`.

### 4.3 Bindings: para onde vai cada valor

| Binding | Destino |
| --- | --- |
| `{key: k}` | chave `k` do plugin no YAML do Fluent Bit |
| `{key: k, join: ","}` | lista unida numa string |
| `{key: k, repeat: true}` | lista YAML de valores (chave multi-valor do plugin) |
| `{key: k, omit_if: v}` | omite a chave quando o valor é `v` |
| `{template: caminho.pontilhado}` | settings/mappings do component template do pacote |
| `{pipeline_toggle: tag}` | remove o processor com esse `tag` quando `false` |
| `{pipeline_param: tag.campo}` | parâmetro de um processor do ingest pipeline |
| `{lifecycle: campo}` | política ISM |

O core nunca concatena texto para montar configuração. Ele monta um objeto e
serializa com biblioteca YAML/JSON. Valores escalares com caractere de controle
ou quebra de linha são recusados (mesma regra do 1.1).

### 4.4 Referências de contexto (conjunto fechado)

Só estas aparecem em `fixed:`. Qualquer outra `{…}` é erro fatal, como no
conjunto fechado de 8 tokens do 1.x.

| Referência | Valor |
| --- | --- |
| `{stream_tag}` | `velox.<integração>.<stream>` |
| `{artifact}` | nome do artefato da stream, `veloxagent-<stream>.<integração>-v<major>` (§8) |
| `{state_dir}` | diretório de estado do Fluent Bit no agente |
| `{integration}`, `{stream}`, `{package_version}` | identidade |

### 4.5 Catálogo de plugins do Fluent Bit

`fluent-bit/<versão>/{inputs,parsers,filters,processors}/<nome>.yaml` descreve
cada plugin permitido: parâmetros com tipo, padrão, i18n e `since`; o
`event_type` que o input emite; se o filter pode rodar como processor. É com
ele que o console monta o formulário de "adicionar filter/processor" (os
`allow:` da stream) sem código específico por plugin.

Plugins que executam código **não estão no catálogo** e o core recusa uma
stream que os referencie: inputs `exec` e `exec_wasi`; filters `lua` e `wasm`;
processor `fluent_typed_scripting`.

---

## 5. Formulário e validação

1. **Tela de escolha:** lista o catálogo, filtrando por `os` e `event_types`
   compatíveis com os agentes da política.
2. **Formulário:** um bloco por stream (toggle `enabled`). Dentro dele, os
   campos do input, o select de parser e a cadeia de processors (cada padrão
   com seu toggle e seus campos, mais "Adicionar filter/processor" limitado a
   `allow:`). Um bloco "Backend" traz os campos de template, pipeline e ciclo
   de vida. Os campos ficam em `general` e `advanced` (colapsado), como o
   "Advanced options" do Fleet.
3. **Campos com `since`** acima da versão do Fluent Bit do agente mais antigo
   da política: esconder ou marcar como indisponível.
4. **Validação no core**, nunca só no navegador: tipo, `required`, `min`/`max`,
   `pattern`, regex compila, plugin no catálogo, `allow:` respeitado, chaves do
   `yaml` avançado existem no plugin.

---

## 6. O que fica na revisão da política

A ativação cresce do `{package_id, package_version, inputs}` do schema 1.2 para:

```json
{
  "package_id": "custom-logs",
  "package_version": "1.0.0",
  "spec_version": "2.0",
  "streams": {
    "log": {
      "enabled": true,
      "input":  {"paths": ["/srv/app/*.log"], "multiline": "java"},
      "parser": "json",
      "processors": [
        {"id": "exclude", "enabled": true, "fields": {"rules": ["log ^DEBUG"]}},
        {"plugin": "modify", "params": {"add": ["env prod"]}}
      ],
      "backend": {"replicas": 1, "delete_after": "14d"}
    }
  }
}
```

**Segredos (`type: password`):** o valor vai para o armazenamento de segredos
da política no serviço Mesh, fora da revisão, como a credencial do coletor
(`mesh_policy_credentials`). A revisão guarda só `{"$secret": "<id>"}`. O
compilador escreve `${VELOX_SECRET_<ID>}` no YAML. O agente recebe o segredo
autenticado no check-in e o exporta como variável de ambiente, sem gravar em
disco nem em log. A credencial do coletor (`${VELOX_OS_USER}` /
`${VELOX_OS_PASSWORD}`) segue igual.

---

## 7. Compilar o YAML do Fluent Bit

Formato **YAML** (Fluent Bit ≥ 3.2), porque processors só existem em YAML e o
YAML aceita `parsers:` e `multiline_parsers:` inline.

Algoritmo, por política:

1. `service:` do agente (flush, log_level, storage). O pacote nunca declara.
2. Para cada ativação → cada stream habilitada:
   1. **Parsers** do pacote em `parsers:` / `multiline_parsers:` com nome
      prefixado `<integração>.<stream>.<parser>`, para nunca colidir entre
      integrações.
   2. **Input:** `name: <plugin>`, `tag: {stream_tag}`, chaves `fixed` com as
      referências resolvidas, chaves dos campos pelo binding, `parser:` se
      escolhido.
   3. **Processors do input:** cadeia padrão habilitada, depois os adicionados
      pelo operador, na ordem. Filters entram **como processor** sempre que o
      catálogo diz que o plugin aceita essa posição. Isso evita o `Match`
      global de uma integração pegar registros de outra. Filter que não roda
      como processor vira filter global com `match: {stream_tag}`.
   4. **Metadados** (processor `content_modifier` no fim da cadeia):
      `velox.integration`, `velox.stream`, `velox.package_version`. Com eles o
      painel "dados recebidos por integração" volta a ser possível.
3. **Outputs:** gerados pelo core a partir dos endpoints da política, escolhidos
   pelo `event_type` da stream (§9). Para logs e traces: um `opensearch` por
   stream (`match: {stream_tag}`, `index` = `{artifact}`). Para métricas: um
   `opentelemetry` para o endpoint OTLP da política. TLS, `tls.verify`, CA e
   credencial vêm só das configurações do endpoint no Mesh (decisão do
   operador), nunca do pacote.
4. Calcular o hash e entregar ao serviço Mesh como hoje (`put_policy`).

Exemplo de saída para a ativação do §6:

```yaml
service:
  flush: 5
  log_level: info
  storage.path: /var/lib/velox-agent/fluent-bit/storage

parsers:
  - name: custom-logs.log.json
    format: json
    time_key: time
    time_format: "%Y-%m-%dT%H:%M:%S.%L%z"

pipeline:
  inputs:
    - name: tail
      tag: velox.custom-logs.log
      path: /srv/app/*.log
      multiline.parser: java
      parser: custom-logs.log.json
      db: /var/lib/velox-agent/fluent-bit/state/tail-velox.custom-logs.log.db
      mem_buf_limit: 5MB
      processors:
        logs:
          - name: grep
            exclude: log ^DEBUG
          - name: modify
            add: env prod
          - name: content_modifier
            action: insert
            key: velox.integration
            value: custom-logs
          # … velox.stream, velox.package_version

  outputs:
    - name: opensearch
      match: velox.custom-logs.log
      host: os.exemplo.com
      port: 443
      tls: on
      tls.verify: on                      # configuração do endpoint no Mesh
      http_user: ${VELOX_OS_USER}
      http_passwd: ${VELOX_OS_PASSWORD}
      index: veloxagent-log.custom-logs-v1
      write_operation: create             # data stream (§8; confirmar no FB mínimo)
      suppress_type_name: on
```

Exemplo de stream de métricas nativas (`system`, stream `cpu`, plugin
`node_exporter_metrics`) na mesma política:

```yaml
pipeline:
  inputs:
    - name: node_exporter_metrics
      tag: velox.system.cpu
      metrics: cpu,loadavg
      scrape_interval: 30
      processors:
        metrics:
          - name: labels
            insert:
              - velox_integration system
              - velox_stream cpu
              - velox_package_version 1.0.0
  outputs:
    - name: opentelemetry
      match: velox.system.cpu
      host: otlp.exemplo.com              # endpoint OTLP da política
      port: 4318
      metrics_uri: /v1/metrics
      tls: on
      tls.verify: on
      http_user: ${VELOX_OTLP_USER}
      http_passwd: ${VELOX_OTLP_PASSWORD}
```

O compilador de referência deste repositório (`scripts/render.py`) gera
exatamente isso a partir de um pacote e de uma ativação. É a especificação
executável: o compilador do core deve produzir saída equivalente para os
mesmos casos de teste. O CI do registry roda `fluent-bit --dry-run` (3.2 e a
versão atual) sobre a saída de todo pacote com seus padrões e com os fixtures
de `tests/activations/`; a saída foi aceita também pelo 4.0.

**Processamento condicional (reservado).** O Fluent Bit ≥ 4.0 aceita uma chave
`condition` por processor (`op: and|or`, regras `field/op/value` com
`eq, neq, gt, lt, gte, lte, regex, not_regex, in, not_in`, acessor `$field`),
só em YAML e **não** quando um filter roda como processor. A Spec 2.0 não a
expõe; `fluent-bit/5.2/processors/CONDITIONAL.md` guarda a sintaxe para uma
revisão 2.1.

---

## 8. Instalar o backend no OpenSearch

Vale para streams com `event_type` `logs` ou `traces`. Streams de eventos de
métrica não criam nada no OpenSearch (§9).

**Nome base `N` por stream: `veloxagent-<stream>.<integração>-v<major>`.**
Exemplos: `veloxagent-access.nginx-v1`, `veloxagent-error.nginx-v1`,
`veloxagent-auth.system-v1`, `veloxagent-log.custom-logs-v1`.

- O mesmo `N` nomeia data stream, index template, ingest pipeline, política
  ISM e index pattern (o core cria o index pattern; o pacote não traz).
- Saved objects do pacote têm ids locais (`overview`) e são instalados como
  `veloxagent-<integração>-v<major>-<id>`, porque um dashboard pode cruzar
  várias streams. Eles referenciam o index pattern de uma stream como
  `stream:<id>`, e o core troca por `N`.
- O `id` da stream é único no pacote e descritivo (`access`, `error`, `auth`,
  `cpu`), porque é a primeira coisa que o operador lê na lista de índices.
- `-v<major>` é a major da **versão do pacote**. Mudança incompatível de
  mapping = nova major = novo `N`.
- O prefixo `veloxagent-` mantém a permissão única do coletor (ADR-070:
  `veloxagent-role` sobre `veloxagent-*`); integração nova não pede permissão nova.
- Substitui, para pacotes 2.0, o formato `veloxagent-<integração>-<sinal>-v<major>`
  do ADR-071, que dá um nome por sinal e colide quando uma integração tem
  várias streams do mesmo sinal. Pacotes 1.x continuam com o formato antigo.
  Registrar numa ADR do core.
- Leitores (retenção, detectores, "dados chegando") usam a família sem versão
  `veloxagent-<stream>.<integração>-v*`.

Ordem, **antes** de gravar a revisão (o agente não pode escrever antes de o
template existir):

1. Component template `N@package`: mappings e settings do
   `index-template.json` com os bindings `template` aplicados.
2. Component template `N@custom`: criar vazio **se não existir**; nunca
   sobrescrever. É do operador.
3. Ingest pipeline `N@custom`: idem, vazio se não existir, nunca sobrescrito.
4. Ingest pipeline `N`: o do pacote, com `pipeline_toggle` e `pipeline_param`
   aplicados, terminando num processor `pipeline` que chama `N@custom`.
5. Política ISM `N`: rollover e exclusão a partir de `lifecycle`, com
   `ism_template` apontando para os índices de `N`.
6. Index template `N`: `composed_of: [N@package, N@custom]`,
   `index.default_pipeline: N`, `data_stream: {}` (pendente, §13).
7. Index pattern `N` (id e título `N`, `timeFieldName: @timestamp`).
8. Saved objects do `dashboards:` do manifesto: ids locais viram
   `veloxagent-<integração>-v<major>-<id>`, `stream:<id>` vira o `N` da stream,
   em todas as referências, incluindo `searchSourceJSON` (transformação por JSON
   parseado, como no ADR-071).

`scripts/render.py <pacote> --backend` imprime exatamente esses objetos
(component templates, pipeline com o processor `pipeline` para `N@custom`
— sem `ignore_missing_pipeline`, que é do Elasticsearch e o OpenSearch recusa;
`N@custom` é criado antes —, política ISM com `ism_template` para
`.ds-N-*`, index template com `data_stream: {}`, index pattern e saved
objects renomeados). Detalhe prático: os pipelines dos pacotes copiam campos com `script`
(`ctx.event.original = ctx.log`): o OpenSearch não tem `copy_from`, e `set`
com `{{campo}}` escapa aspas.

**Compartilhamento:** os artefatos de `N` são do deployment, não da política.
Duas políticas na mesma major compartilham `N`. Instale sempre o backend da
**maior versão ativa** daquela major. Por isso uma versão minor só pode
**acrescentar** mapping, nunca mudar um tipo; o validador do registry verifica
isso. Mudança incompatível = nova major = novo `N`.

**Remoção:** o backend sai quando nenhuma ativação do deployment usa mais
aquela major (contagem por uso, ADR-073 item 4). `@custom` e dados ficam, a
menos que o operador peça explicitamente.

---

## 9. Métricas e roteamento por tipo de evento

Uma stream tem dois atributos distintos:

- **`signal`**: o que a stream representa para o operador (`logs`, `metrics`,
  `traces`). Decide categoria na tela, filtros do catálogo e dashboards.
- **`event_type`**: o que o plugin do Fluent Bit emite de fato. O autor declara
  e o validador do registry confere contra o catálogo de plugins (regra R9),
  então o core pode confiar no valor. **Decide o output.**

O output `opensearch` do Fluent Bit aceita só `logs` e `traces`, e não existe
processor que converta métrica em log. Por isso o roteamento é por
`event_type`:

| `event_type` | Output do Fluent Bit | Destino | Backend instalado |
| --- | --- | --- | --- |
| `logs` | `opensearch` | data stream `N` no OpenSearch | §8 completo |
| `traces` | `opensearch` | data stream `N` no OpenSearch | §8 completo |
| `metrics` | `opentelemetry` (OTLP/HTTP, `/v1/metrics`) | OTel Collector do deployment → Cortex | nenhum no OpenSearch; só dashboards |

### 9.1 Rota de métricas (eventos de métrica)

O core já implanta, por deployment, o stack OTel (ADR-049): um OTel Collector
com receptor OTLP (gRPC 4317, HTTP 4318, autenticação basic `basicauth/otlp`)
cuja pipeline `metrics` exporta por `prometheusremotewrite` para o Cortex. O
Dashboards consulta o Cortex por uma datasource Prometheus. A rota do agente
reaproveita esse caminho:

```
Fluent Bit (opentelemetry output) ──OTLP/HTTP 4318, basic auth──▶ OTel Collector do deployment
                                                                  └─prometheusremotewrite─▶ Cortex ◀─ Dashboards (datasource Prometheus)
```

O que o Mesh/core precisa ter:

1. **Terceiro tipo de endpoint na política: OTLP.** Ao lado dos endpoints
   OpenSearch e Velox Mesh, com o mesmo parser de host / host:porta / URL e o
   mesmo bind do output (Host, Port, tls, Path → `metrics_uri`). O endereço
   interno do Collector é oferecido com um clique, nunca assumido.
2. **Credencial OTLP do coletor**, criada pelo core como a do OpenSearch
   (ADR-070), guardada fora da revisão e entregue no check-in como
   `VELOX_OTLP_USER` / `VELOX_OTLP_PASSWORD`. O Collector hoje autentica com
   `basicauth/otlp`; o core precisa provisionar um usuário para agentes ali.
3. **Exposição do receptor OTLP para fora do cluster** quando a política tiver
   agentes externos (Ingress/LoadBalancer com TLS). Hoje ele é um Service
   interno.
4. **Política sem endpoint OTLP ou deployment sem stack OTel:** o console não
   oferece streams com `event_type: metrics` e o compilador recusa a ativação
   com mensagem clara. Nunca descartar em silêncio.
5. **Rótulos de identidade:** o compilador adiciona, pelo processor `labels`,
   `velox_integration`, `velox_stream`, `velox_package_version` (e o Collector
   já acrescenta os atributos do recurso). É o equivalente do `N` para
   métricas: dashboards e alertas filtram por esses rótulos.
6. **Retenção:** é a do Cortex (hoje 360h), não ISM. Os campos `lifecycle` não
   se aplicam a streams de eventos de métrica e o validador do registry os
   recusa ali.
7. **Dashboards de métricas:** saved objects que consultam a datasource
   Prometheus (PromQL), entregues pelo pacote em `dashboards/` e instalados com
   a mesma renomeação de ids.

### 9.2 Inputs "de métrica" que emitem registros de log

Alguns inputs medem coisas mas, pelo que a documentação indica, emitem
**registros de log** (`cpu`, `mem`, `disk`, `netif`, `proc`, `thermal`,
`winstat` e possivelmente `docker`, `statsd`, `collectd`). Decisão: são
streams **`signal: metrics`** (aparecem como métricas para o operador) com
`event_type: logs` (vão para o OpenSearch como documentos, num data stream
`N` com mapping numérico, ISM normal e dashboards por index pattern). O
`event_type` real de cada plugin é confirmado plugin a plugin no catálogo
(fase F2); se a documentação de um plugin disser que ele emite métricas, ele
segue a rota 9.1.

Para métricas de host em Linux, os pacotes preferem o input nativo
`node_exporter_metrics` (cpu, meminfo, diskstats, netdev, filesystem,
loadavg, thermal_zone) e `process_exporter_metrics`, que emitem métricas de
verdade. Os inputs que emitem log (`cpu`, `mem`...) ficam como alternativa
para quem não tem o stack OTel.

---

## 10. Upgrade de versão

Mesmo fluxo do "Upgrade integration" do Fleet:

1. O core encontra uma versão compatível mais nova e o console mostra "Pronto
   para atualizar X → Y" com o changelog.
2. Diff dos campos, por stream:
   - campo com o mesmo nome e tipo → valor mantido;
   - campo novo `required` sem `default` → o operador preenche antes de salvar;
   - campo removido → descartado, e o console mostra qual;
   - stream nova → entra com o `enabled` padrão;
   - stream removida → sai.
3. Ao salvar: backend da nova versão primeiro (§8), depois a nova revisão. Os
   agentes pegam a mudança no próximo check-in.
4. Mudança de major cria `N` novo; o antigo fica para a retenção.

---

## 11. Invariantes que não mudam

- Só o core lê pacotes, verifica, compila e fala com OpenSearch como admin.
  O serviço Mesh só guarda e serve.
- Compilação só sobre pacote verificado; sem bypass.
- Nada vindo do registry executa código no host (allowlist, §4.5).
- O pacote nunca declara output, endpoint, TLS do output ou credencial do
  coletor.
- Segredos fora da revisão; só para agente autenticado naquela política.
- Configuração montada como objeto e serializada, nunca por concatenação.
- O conjunto de referências de contexto é fechado.
- O agente valida (`--dry-run`) e faz rollback; status derivado, nunca gravado.

---

## 12. Mudanças necessárias por componente

**Core**
- [ ] Ler `packages/index.json` e pacotes 2.0 (o catálogo e os pacotes 1.x continuam para o caminho de cluster).
- [ ] Verificação 2.0: manifesto assinado + inventário sha256. `velox sign` / `velox verify` com suporte 2.0.
- [ ] Validação de valores (§5) e ativação 2.0 na revisão (§6).
- [ ] Compilador YAML (§7), equivalente ao `scripts/render.py`.
- [ ] Backend 2.0 (§8): component templates, `@custom`, ISM, data streams, contagem por uso.
- [ ] Segredos de integração no fluxo de credenciais.
- [ ] Roteamento de output por `event_type` (§9).
- [ ] Rota de métricas (§9.1): endpoint OTLP na política, credencial OTLP do coletor provisionada no Collector, exposição externa do receptor, recusa clara sem stack OTel.
- [ ] ADR: nome por stream `veloxagent-<stream>.<integração>-v<major>` para pacotes 2.0, data streams, rota de métricas pelo stack OTel.

**Console**
- [ ] Tela de catálogo com filtros (categoria, SO, tipo de evento, release).
- [ ] Formulário gerado (§4.2, §5), incluindo "adicionar filter/processor" a partir do catálogo de plugins.
- [ ] Tela de upgrade com diff (§10).

**Serviço Mesh**
- [ ] Guardar segredos de integração por política (como `mesh_policy_credentials`) e entregá-los no check-in.
- [ ] Endpoint do tipo OTLP nas configurações (`veloxsearch.ai/mesh-settings`) e credencial OTLP por política.

**VeloxAgent**
- [ ] Aplicar configuração YAML (`fluent-bit -c config.yaml`, `--dry-run` em YAML).
- [ ] Exportar `VELOX_SECRET_*` e `VELOX_OTLP_USER` / `VELOX_OTLP_PASSWORD` para o Fluent Bit sem registrar valores.
- [ ] Reportar `velox.fluent_bit.version` nos atributos (o console usa para `since`).
- [ ] Criar e expor `{state_dir}` do Fluent Bit.

---

## 13. Pontos em aberto

| Tema | Pergunta | Onde decide |
| --- | --- | --- |
| Data streams | `write_operation: create` no output `opensearch` desde o Fluent Bit 3.2? | F2 + core |
| Métricas | Exposição externa do receptor OTLP do Collector (Ingress, TLS, auth) | core |
| `event_type` real | Confirmar plugin a plugin (`cpu`, `mem`, `docker`, `statsd`...) | F2 |
| Assinatura 2.0 | Formato canônico do manifesto | F1 + core |
| Cluster | Quando o DaemonSet passa a ler `packages/` em vez de `integrations/` | F6 |
