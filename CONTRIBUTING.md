# Contributing an integration

An integration is **data**. No Rust, no build step, no plugin API — you are
writing an ingest pipeline, an index template, some dashboards and a Fluent Bit
config, plus a manifest that names them.

By participating you agree to the
[Code of Conduct](https://github.com/tornis-tecnologia/veloxsearch-oss/blob/main/CODE_OF_CONDUCT.md)
of the main project.

## Before you start

Open an issue describing the source: what it is, what its log format looks like
(a few real, redacted lines), how the logs reach the cluster, and the three or
four things an operator actually wants on the dashboard. That conversation is
much cheaper than a finished package that indexes the wrong fields.

## The package

Create `integrations/<id>/` with:

| File | Required | What it is |
| --- | --- | --- |
| `manifest.yaml` | yes | Identity, discovery predicate, asset names, teardown set, signature |
| `saved-objects.ndjson` | yes | Index pattern, visualizations, and the dashboard — one compact JSON document per line, dashboard last |
| `agent.conf.tmpl` | yes | Fluent Bit configuration, interpolated at install time |
| `pipeline.json` | no | OpenSearch ingest pipeline; omit if the source needs no parsing |
| `index-template.json` | no | OpenSearch index template; omit together with `pipeline.json` |

`<id>` is lowercase, and matches `manifest.yaml`'s `id`.

Validate the manifest against
[manifest.schema.json](https://github.com/tornis-tecnologia/veloxsearch-oss/blob/main/docs/integrations/manifest.schema.json).
Copy `integrations/nginx/` as a starting point — it exercises every field.

## Three rules that will fail review

**1. Interpolation is a closed set.** Exactly eight tokens are substituted into
your assets. Anything else stays literal — it is not an escape hatch, it is a
typo that ships. See
[interpolation.md](https://github.com/tornis-tecnologia/veloxsearch-oss/blob/main/docs/integrations/interpolation.md).

**2. `teardown` must list everything install creates — no more, no less.** The
core asserts this: the set your package creates and the set your teardown
removes are compared, and a mismatch fails. An integration that leaves orphans
behind after uninstall is a bug, and so is one that deletes something it did not
create.

**3. `discovery` is a predicate, not a program.** It is an image-substring test
that yields a display kind. Omit it entirely if your source is the cluster or
the nodes themselves rather than a discoverable container image.

## Signing

**You do not sign your package**, and you should not try.

Submit it with the placeholder signature (copy the block from any existing
manifest). A maintainer computes the canonical digest and signs it with the
private key at publish time. The private half is never in this repository, never
in the container image, and never in CI.

If you *want* to check your package will verify, run the core's gates against
your checkout:

```sh
git clone https://github.com/tornis-tecnologia/veloxsearch-oss.git
cd veloxsearch-oss
VELOX_REGISTRY_PATH=/path/to/veloxsearch-registry cargo test
```

## The catalog

Add a row to `catalog.json` matching your manifest: same `id`, same `version`,
same `title` and `summary` strings, same `min_core_version`. The catalog is what
the Integrations tab lists; a package with no catalog row is invisible, and a
catalog row with no package is an error the core reports.

Titles and summaries need `en`, `es` and `pt`. If you cannot write all three,
say so in the pull request and a maintainer will fill the gap.

## Packages extracted from core recipes

The twelve packages here today are **generated** from the recipes compiled into
the core and are held byte-equivalent by its golden gates. Editing their assets
by hand will fail CI in `veloxsearch-oss`. Change the recipe in the core, then
regenerate:

```sh
VELOX_REGISTRY_PATH=/path/to/veloxsearch-registry \
  VELOX_UPDATE_REGISTRY=1 cargo test regenerate_registry_assets
```

Manifests are hand-authored and are never rewritten by that command.

## Checklist

- [ ] `integrations/<id>/` with a manifest and its assets
- [ ] Manifest validates against the schema
- [ ] `teardown` lists exactly what install creates
- [ ] Only the eight interpolation tokens are used
- [ ] A `catalog.json` row with matching strings, in `en`, `es` and `pt`
- [ ] Signature left as the placeholder
- [ ] Commits signed off (`git commit -s`)
