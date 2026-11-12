# CLAUDE.md — veloxsearch-registry

Contexto, decisões e plano de trabalho deste repositório. Leia antes de mudar
qualquer coisa. Atualize este arquivo quando uma decisão mudar.

## Visão

O registry é a **fonte de integrações** do VeloxSearch. Ele não compila, não
aplica e não fala com cluster nenhum. Ele publica, assinado e versionado,
**o que pode ser configurado** em cada integração e com quais padrões:

- **Coleta (Fluent Bit):** input, parsers, filters e processors, cada um com
  parâmetros tipados e amigáveis (path de logs, regras de exclusão, multiline,
  portas, intervalo de scrape...).
- **Backend (OpenSearch):** index template / mappings, ingest pipeline,
  ciclo de vida (rollover, retenção), pontos de extensão `@custom`.
- **Visualização:** dashboards e index patterns prontos.

O **VeloxMesh** lê o registry, mostra o catálogo na tela de escolha de
integração de uma policy, gera o formulário a partir do pacote (como o Fleet do
Elastic faz), valida o que o operador preencheu, instala o lado backend no
OpenSearch e compila a configuração do Fluent Bit que o **VeloxAgent** aplica.

Referência de experiência: Elastic Integrations / Fleet
(https://www.elastic.co/docs/reference/integrations/all_integrations).
Referência de opções de coleta: manual do Fluent Bit
(https://docs.fluentbit.io/manual/data-pipeline/inputs, `/parsers`,
`/processors`, `/filters`).

## Documentos do repositório

| Documento | Para quem | Status |
| --- | --- | --- |
| `docs/mesh-integration-guide.md` | Quem desenvolve VeloxMesh / VeloxAgent / core | rascunho v1 |
| Cópia compartilhada do guia (Claude Docs): https://claude.ai/artifact/9pKW45BX5xBxMpSJUirHNz | time do Mesh | manter igual ao arquivo; o arquivo é a fonte |
| `docs/spec/README.md` (Spec 2.0, regras R1–R24) | Autores de pacote e Mesh | rascunho F1 |
| `schemas/*.schema.json` (common, manifest, stream, index, plugin, activation, changelog) | validador e Mesh | F1 |
| `docs/spec/examples/` (pacote custom-logs, ativação, entrada de catálogo) | fixture de conformidade | F1 |
| `scripts/check_spec.py`, `scripts/inventory.py` | CI (job `spec`) | F1 |
| `README.md`, `CONTRIBUTING.md` | contribuidores | descrevem só o formato 1.x — atualizar em F5 |

Documento de arquitetura do Mesh (fornecido pelo usuário, em Claude Docs):
https://claude.ai/artifact/6xXfT5pPYUxdjLsGHKwyEU — descreve Mesh, Agent,
políticas, check-in OpAMP, invariantes de segurança. É a fonte de verdade do
lado Mesh; este repo tem de ser compatível com ela.

## Decisões tomadas (2026-11-12)

1. **O registry só fornece parâmetros e artefatos; o Mesh aplica.** Nenhum
   código executável no registry chega a um host.
2. **Coleta configurável por stream, no estilo Elastic.** Cada integração tem
   streams (≈ data streams do Elastic). Cada stream declara: input do Fluent
   Bit + parâmetros expostos, parsers, filters/processors padrão e quais o
   operador pode acrescentar, e o backend (template, pipeline, dashboards).
3. **Backend também é configurável** (pedido explícito): settings de template
   (shards, réplicas, refresh), mappings extras, liga/desliga processors do
   ingest pipeline, ciclo de vida, e hooks `<nome>@custom` (pipeline e
   component template) que o operador edita sem tocar no pacote.
4. **Segurança do output é do Mesh.** Pacote nunca declara `[OUTPUT]`,
   endpoint, TLS do output nem credencial do coletor. Pacote declara TLS e
   credenciais **do input** quando o input conecta num serviço (scrape HTTPS,
   Kafka SASL...), como campo `password`/`secret`, guardado pelo Mesh.
5. **Versão por integração, desacoplada do Mesh.** Cada integração publica
   várias versões imutáveis; cada versão declara `min_mesh_version`,
   `min_agent_version`, `min_fluent_bit_version`. O Mesh escolhe a maior
   compatível e oferece upgrade (tela "Upgrade integration" do Fleet).
6. **Configuração gerada em YAML do Fluent Bit (≥ 3.2).** Processors só
   existem no formato YAML ("Only YAML configuration files support
   processors"); YAML aceita `parsers:` e `multiline_parsers:` inline.
7. **Filters viram processors anexados ao input** sempre que o plugin aceita
   essa posição — evita que o `Match` global de uma integração pegue registros
   de outra. Filter global com `Match` no tag da stream só quando o plugin não
   roda como processor.
8. **Allowlist de plugins.** Fora do catálogo: tudo que executa código no host
   — inputs `exec`, `exec_wasi`; filters `lua`, `wasm`; processor
   `fluent_typed_scripting` (Lua); `tensorflow` até avaliação. Invariante do
   Mesh: "um Mesh comprometido oferece configuração, nunca executa nada no
   host". Também fora: `dummy`, `random`, `stdin` (teste).
9. **Nada de interpolação de texto em configuração.** Spec 2.0 é estruturada:
   valores tipados, serializados pelo Mesh com biblioteca YAML/JSON. Strings
   de valor não podem conter controle/quebra de linha. Conjunto fechado de
   referências de contexto (ex. `{state_dir}`, `{stream_tag}`) definido na spec.
10. **Árvore nova `packages/` para a Spec 2.0; `integrations/` + `catalog.json`
    (1.x) ficam intactos.** Motivo: os testes golden do core
    (`src/registry_golden.rs` em veloxsearch-oss) prendem `integrations/<id>/`
    byte a byte às receitas do DaemonSet e exigem que a lista de pastas seja
    igual a `RECIPES`. O caminho de cluster migra depois, num PR casado com o
    core. (Recomendação adotada; usuário pode reverter.)
11. **F4 cobre todos os inputs padrão do Fluent Bit** (exceto os excluídos no
    item 8), mais a migração das 12 integrações de aplicação existentes.
12. **Nome do artefato por stream: `veloxagent-<stream>.<integração>-v<major>`**
    (ex. `veloxagent-access.nginx-v1`). Mesmo nome para data stream, index
    template, ingest pipeline, ISM e index pattern; saved objects `N-<sufixo>`.
    Substitui o formato do ADR-071 só para pacotes 2.0. `id` de stream único e
    descritivo. (2026-11-12, usuário)
13. **`signal` ≠ `event_type`.** `signal` = o que a stream é para o operador;
    `event_type` = o que o plugin emite (vem do catálogo de plugins) e decide
    o output. Inputs que medem mas emitem log (`cpu`, `mem`, `disk`, `netif`,
    `proc`, `thermal`, ...) são `signal: metrics` + `event_type: logs` →
    OpenSearch. `event_type` confirmado plugin a plugin em F2. (2026-11-12, usuário)
14. **Métricas entram na Spec 2.0.** Eventos de métrica vão por output
    `opentelemetry` (OTLP/HTTP) para o OTel Collector do deployment (ADR-049),
    que exporta para o Cortex; dashboards de métricas consultam a datasource
    Prometheus. Sem ISM nem template para essas streams. Detalhes no guia §9.
15. **Dashboards no manifesto, não na stream.** Pacote não traz index pattern
    (o core cria um por stream logs/traces, id `N`); saved objects referenciam
    `stream:<id>` e têm ids locais instalados como
    `veloxagent-<integração>-v<major>-<id>`.
16. **`event_type` é declarado pelo autor e conferido contra o catálogo (R9).**
17. **Assinatura 2.0 = algoritmo do signing.md 1.x** (JCS do manifesto sem
    `signature` + sha256 de cada arquivo, lista ordenada, ed25519), com os
    arquivos enumerados pelo inventário `files:`.

## Pendências (precisam de decisão fora deste repo)

- **Data streams do OpenSearch** em vez de índice simples (exige
  `Write_Operation create` no output e ISM com `ism_template`). Proposto como
  padrão da Spec 2.0; confirmar suporte do output `opensearch` no FB mínimo.
- **Rota de métricas no core/Mesh:** endpoint OTLP na política, credencial
  OTLP do coletor no Collector, exposição externa do receptor OTLP. Guia §9.1.
- **ADR no core** para o nome por stream (decisão 12) e a rota de métricas.
- **Assinatura 2.0.** Proposta: manifesto lista todo arquivo com sha256;
  ed25519 sobre o manifesto canônico; mesma chave `velox-registry-2026-10`.
  `velox sign`/`verify` do core precisam suportar.
- **Schema 1.2 do core só existe no branch local `feat/ee-velox-mesh-plan`**
  de veloxsearch-oss (não está em `origin/develop` nem `origin/main`).

## Plano

| Fase | Entrega | Depende de |
| --- | --- | --- |
| F0 ✅ | Este CLAUDE.md; `docs/mesh-integration-guide.md`; cópia compartilhada | — |
| F1 ✅ | Spec 2.0 em `docs/spec/` + JSON Schemas em `schemas/` + exemplo + `check_spec.py` no CI | — |
| F2 ✅ | Catálogo `fluent-bit/5.2/` — 84 plugins (49 inputs, 19 filters, 9 processors, 4 formatos de parser, 8 multiline). Descrições parafraseadas do manual; chaves/padrões transcritos. `CONDITIONAL.md` guarda a sintaxe condicional para uma Spec 2.1 | F1 |
| F3 ✅ | `validate_v2.py` (R1–R23), `build_index.py`, `render.py` (+ `--backend`), `dryrun.sh`, `pipeline_test.py` (R24), `check_catalog.py`; CI jobs `spec`, `packages`, `pipelines` | F1, F2 |
| F4 🔄 | `custom-logs`, `system` prontos e verificados (dry-run 3.2/4.0/5.x, pipelines no OpenSearch). Demais pacotes em andamento por agentes (ver ondas) | F1–F3 |
| F5 ✅ | README, CONTRIBUTING, `docs/PACKAGING.md` | — |
| F6 | PR casado no core: ADR de nomes por stream, signing 2.0, leitura do catálogo v2 pelo Mesh, rota de métricas, migração do caminho de cluster | core |

Tudo no branch `feat/packages-spec-2.0` (não enviado ao remoto; nada assinado).
Ambiente local de teste usado: OpenSearch em `docker` (`velox-os-test`, porta
19200, sem segurança) e imagens `fluent/fluent-bit:{3.2,4.0,latest}`.

### F4 — pacotes por input padrão do Fluent Bit

Tipo de evento marcado "?" = confirmar na página do plugin em F2.

**Onda 1 — logs, sem dependência externa**

| Pacote | Inputs (plugin) | Evento | SO |
| --- | --- | --- | --- |
| `custom-logs` | `tail` (paths, exclude, multiline, parser) | logs | todos |
| `file-head` | `head` | logs | todos |
| `system` | `tail` (syslog, auth, kern), `systemd`, `kmsg`, `cpu`, `mem`, `disk`, `netif`, `proc`, `thermal` | logs (cpu/mem/... ?) | Linux |
| `journald` | `systemd` (filtros por unit, campos) | logs | Linux |
| `kernel-logs` | `kmsg` | logs | Linux |
| `syslog` | `syslog` (servidor tcp/udp/unix_tcp/unix_udp) | logs | todos |
| `tcp` | `tcp` | logs | todos |
| `udp` | `udp` | logs | todos |
| `http-endpoint` | `http` | logs | todos |
| `fluent-forward` | `forward` | logs | todos |
| `mqtt` | `mqtt` | logs | todos |
| `kafka-consumer` | `kafka` | logs | todos |
| `splunk-hec` | `splunk` | logs | todos |
| `elasticsearch-bulk` | `elasticsearch` | logs | todos |
| `docker-events` | `docker_events` | logs | Linux |
| `agent-self` | `fluentbit_logs`, `health`, `fluentbit_metrics` | logs / metrics | todos |

**Onda 2 — Windows**

| Pacote | Inputs | Evento |
| --- | --- | --- |
| `windows` | `winevtlog`, `winlog`, `winstat`, `windows_exporter_metrics`, Event Tracing for Windows | logs / metrics |

**Onda 3 — eventos de métrica e traces (rota OTLP do guia §9.1; Mesh precisa implementar para funcionar)**

| Pacote | Inputs |
| --- | --- |
| `host-metrics` | `node_exporter_metrics`, `process_exporter_metrics`, `gpu_metrics` (?) |
| `prometheus` | `prometheus_scrape`, `prometheus_textfile` (?) |
| `prometheus-remote-write` | `prometheus_remote_write` (receptor) |
| `opentelemetry` | `opentelemetry` (receptor OTLP logs/metrics/traces) |
| `statsd` | `statsd` |
| `collectd` | `collectd` |
| `docker-metrics` | `docker` |
| `podman-metrics` | `podman_metrics` |

**Onda 4 — especiais**

| Pacote | Inputs | Nota |
| --- | --- | --- |
| `kubernetes-events` | `kubernetes_events` | precisa de API do cluster |
| `ebpf` | `ebpf` | privilegiado; `release: experimental` |
| `blob` | `blob` | avaliar caso de uso |
| `serial` | `serial` | sob demanda |

**Onda 5 — integrações de aplicação (migração das 12 de `integrations/`)**

nginx (access, error, `nginx_exporter_metrics`), postgres, mysql, mongo,
redis, rabbitmq, kafka (logs do broker), traefik, ssh (auth). Cada uma usa
`tail` + parsers + pipeline próprio, com paths padrão por distro como campos.
kubernetes, k8s-events, k8s-audit continuam no caminho de cluster (1.x) até F6.

**Excluídos:** `exec`, `exec_wasi` (executam comando), `dummy`, `random`,
`stdin` (teste).

## Estrutura alvo

```
catalog.json                 1.x — caminho de cluster (DaemonSet), golden do core
integrations/<id>/           1.x — idem; NÃO editar à mão (gerado pelo core)
packages/                    Spec 2.0 — lido pelo VeloxMesh
  index.json                 gerado por scripts/build_index.py
  <id>/<versão>/             imutável depois de publicado
    manifest.yaml            identidade, compatibilidade, streams, inventário + assinatura
    changelog.yaml
    docs/README.{en,es,pt}.md
    img/icon.svg
    streams/<stream>/
      stream.yaml            input, parsers, filters, processors, campos
      index-template.json    mappings + settings (com bindings)
      ingest-pipeline.json   processors com `tag` (para liga/desliga)
      sample-event.json
      test/*.log + *.expected.json
    dashboards/*.ndjson
fluent-bit/<versão-fb>/{inputs,parsers,filters,processors}/<nome>.yaml
schemas/                     JSON Schemas da Spec 2.0
docs/spec/                   Spec 2.0
docs/mesh-integration-guide.md
scripts/                     validate.py (1.x), validate_v2.py, build_index.py, render.py
```

## Regras que valem sempre

- **Não editar `integrations/*` à mão.** São extrações byte a byte das
  receitas do core; mudar quebra o CI do veloxsearch-oss. Manifestos 1.x são
  escritos à mão, assets são regenerados pelo core.
- **Versão publicada é imutável.** Mudança = nova versão.
- **Nunca assinar no CI nem guardar chave privada aqui.** Pacote entra com
  assinatura placeholder; mantenedor assina com `velox sign`.
- **Nada que execute código no host** (decisão 8).
- **Pacote não declara output** (decisão 4).
- **i18n:** todo texto de UI em `en`, `es`, `pt`.
- **Fluent Bit mínimo 3.2** (requisito do VeloxAgent). Parâmetro mais novo
  declara `since:` e o Mesh esconde para agente com FB antigo.
- Commits com sign-off (`git commit -s`). Branch por fase.
