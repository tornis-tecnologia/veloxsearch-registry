# Contributing an integration

An integration is **data**. No Rust, no build step, no plugin API. You
describe what to collect and how it can be configured, how OpenSearch stores
it, and what the dashboards show; the engine does the rest.

By participating you agree to the
[Code of Conduct](https://github.com/tornis-tecnologia/veloxsearch-oss/blob/main/CODE_OF_CONDUCT.md)
of the main project.

## Which format

- **Spec 2.0 (`packages/`)** — for Velox Mesh / Velox Agent on hosts. This is
  where new integrations go. Read [`docs/PACKAGING.md`](docs/PACKAGING.md)
  (how) and [`docs/spec/README.md`](docs/spec/README.md) (what is allowed).
- **Spec 1.x (`integrations/`)** — the in-cluster DaemonSet path. These
  packages are generated from the core's recipes and held byte-equivalent by
  its golden gates; **do not edit them by hand**. Change the recipe in the
  core, then regenerate (see "Packages extracted from core recipes" below).

## Before you start

Open an issue describing the source: what it is, what its log format looks
like (a few real, redacted lines), how the logs reach the host, and the three
or four things an operator wants on the dashboard. That conversation is much
cheaper than a finished package that indexes the wrong fields.

## A Spec 2.0 package, in short

```
packages/<id>/<version>/
  manifest.yaml            identity, compatibility, streams, dashboards, files (sha256), signature
  changelog.yaml
  docs/README.{en,es,pt}.md
  img/icon.svg
  streams/<stream>/        stream.yaml + index-template.json + ingest-pipeline.json
                           + sample-event.json + test/
  dashboards/*.ndjson
```

Copy [`packages/system/1.0.0`](packages/system/1.0.0) as a starting point.

Rules that will fail review:

1. **Only catalogued plugins and keys.** Every Fluent Bit plugin and every
   key a field binds must exist in `fluent-bit/<version>/`. Plugins that
   execute code (`exec`, `lua`, `wasm`, ...) are not in the catalogue and
   never will be.
2. **No output, endpoint, TLS of the output or collector credential in a
   package.** Those belong to the Mesh policy.
3. **Only the closed set of context references** (`{stream_tag}`,
   `{artifact}`, `{state_dir}`, `{integration}`, `{stream}`,
   `{package_version}`) in `fixed:` values. No `${...}`.
4. **A published version is immutable.** Any change is a new version; within
   a major, mappings only grow.
5. **Pipelines are tested.** Every stream with an ingest pipeline ships
   `test/` cases and their expected output.
6. **en, es and pt** on every title and description.

Run the checklist at the end of `docs/PACKAGING.md` before opening the pull
request; CI runs the same checks (plus `fluent-bit --dry-run` on 3.2 and the
current release, and the pipeline tests against OpenSearch).

## Signing

**You do not sign your package**, and you should not try.

Submit it with the placeholder signature (copy the block from any existing
manifest). A maintainer signs it on their own machine at publish time. The
private half of the key is never in this repository, never in the container
image, and **never in CI** — which is why this step is a person and not a
workflow. CI refuses to merge a package that still carries the placeholder.

### For maintainers: signing a pull request

```sh
gh pr checkout <number>
velox sign packages/<id>/<version> --key ~/path/to/velox-registry-2026-10.priv.pem   # Spec 2.0
velox sign integrations/<id> --key ~/path/to/velox-registry-2026-10.priv.pem         # Spec 1.x
git commit -am "sign: <id> <version>" && git push
```

`velox sign` verifies the signature it just produced **before** writing, so a
package that would not check out never reaches the disk. Then regenerate the
catalogue: `scripts/build_index.py` (2.0; the manifest's sha256 changed).

## Packages extracted from core recipes (Spec 1.x)

The twelve packages under `integrations/` are **generated** from the recipes
compiled into the core and are held byte-equivalent by its golden gates.
Editing their assets by hand will fail CI in `veloxsearch-oss`. Change the
recipe in the core, then regenerate:

```sh
VELOX_REGISTRY_PATH=/path/to/veloxsearch-registry \
  VELOX_UPDATE_REGISTRY=1 cargo test regenerate_registry_assets
```

Manifests are hand-authored and are never rewritten by that command. A recipe
change on the core's `main` opens a regeneration pull request here
automatically (`registry-sync.yml` in `veloxsearch-oss`). CI runs the core's
gates against its `develop`, unless the pull request's head branch also
exists in `veloxsearch-oss`: then it uses that branch, so open both changes
on the same branch name and merge them back to back.

## Checklist

- [ ] `packages/<id>/<version>/` with manifest, streams, dashboards, docs
- [ ] `scripts/validate_v2.py packages/<id>/<version>` passes
- [ ] `scripts/pipeline_test.py` passes and `test/*.expected.json` were reviewed
- [ ] `scripts/dryrun.sh packages/<id>/<version>` passes on 3.2 and latest
- [ ] `tests/activations/<id>/*.json` fixture with every stream on
- [ ] `changelog.yaml` has this version's entry
- [ ] Signature left as the placeholder
- [ ] Commits signed off (`git commit -s`)
