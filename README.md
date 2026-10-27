# veloxsearch-registry

The integration package registry for
[VeloxSearch](https://github.com/tornis-tecnologia/veloxsearch-oss).

A VeloxSearch **integration** turns a log source into a working view: an ingest
pipeline, an index template, a set of dashboards, and a Fluent Bit
configuration. It is **data, not code** — the control plane applies it with a
fixed engine that can do exactly one set of things, and every package is
ed25519-signed and verified before a single byte reaches a cluster.

That is why contributing an integration needs no Rust.

## Layout

```
catalog.json                 what the Integrations tab lists: id, version, i18n strings, core floor
keys/
  velox-registry-2026-10.pub the public half of the signing key (also compiled into the core)
integrations/
  <id>/
    manifest.yaml            the descriptor: identity, discovery, assets, teardown, signature
    pipeline.json            OpenSearch ingest pipeline        (omitted when the source needs none)
    index-template.json      OpenSearch index template         (omitted when the source needs none)
    saved-objects.ndjson     index pattern + visualizations + dashboard
    agent.conf.tmpl          Fluent Bit configuration template
```

The format is specified in the core repository:

- [manifest.schema.json](https://github.com/tornis-tecnologia/veloxsearch-oss/blob/main/docs/integrations/manifest.schema.json) — the manifest schema
- [signing.md](https://github.com/tornis-tecnologia/veloxsearch-oss/blob/main/docs/integrations/signing.md) — what is signed, how, and the verification path
- [interpolation.md](https://github.com/tornis-tecnologia/veloxsearch-oss/blob/main/docs/integrations/interpolation.md) — the closed set of exactly eight substitution tokens

## What is here today

The twelve packages below are **byte-equivalent extractions of the recipes
compiled into the core**. The golden gates in `src/registry_golden.rs` hold them
that way: if a recipe changes in the core and this registry is not regenerated,
the core's CI goes red.

| id | source |
| --- | --- |
| `nginx` | nginx access logs |
| `traefik` | Traefik ingress access logs |
| `postgres` | PostgreSQL server logs |
| `mysql` | MySQL / MariaDB error logs |
| `mongo` | MongoDB server logs |
| `redis` | Redis server logs |
| `rabbitmq` | RabbitMQ server logs |
| `kafka` | Apache Kafka broker logs |
| `kubernetes` | All cluster and pod logs |
| `k8s-events` | Cluster events |
| `k8s-audit` | API-server audit log |
| `ssh` | Node auth / SSH logs |

## Using this registry

Nothing to configure — it is the default. To point an install at a mirror or at
a local checkout instead:

```yaml
# in the veloxsearch-env ConfigMap
VELOX_REGISTRY_URL: "https://raw.githubusercontent.com/tornis-tecnologia/veloxsearch-registry/main"
```

```sh
# air-gapped: a local checkout, verified identically
VELOX_REGISTRY_URL=file:///srv/veloxsearch-registry
```

Signature verification is the same on every route: the trusted key is compiled
into the binary, so it works with no network and cannot be redirected by a
compromised registry. A registry that cannot be reached is a **degraded state,
not a crash** — the last cached catalog is served, marked stale.

## Contributing an integration

See [CONTRIBUTING.md](CONTRIBUTING.md). Short version: open a pull request with
your package directory; a maintainer signs it at publish time.

## Licence

[GNU Affero General Public License v3.0 only](LICENSE) — the same as the core.
The assets here are generated from, and held byte-equivalent to, AGPL-licensed
code in `veloxsearch-oss`.
