#!/usr/bin/env python3
"""Structural validation of the registry: schema, catalog consistency, layout.

This is the CHEAP half of the gate and needs no Rust. The authoritative half —
that every asset is byte-equivalent to what the core generates, and that every
signature verifies — runs in veloxsearch-oss CI, which clones this repository.

Usage: scripts/validate.py [--schema path/to/manifest.schema.json]
"""
import argparse, json, pathlib, sys, urllib.request

SCHEMA_URL = ("https://raw.githubusercontent.com/tornis-tecnologia/"
              "veloxsearch-oss/main/docs/integrations/manifest.schema.json")
ROOT = pathlib.Path(__file__).resolve().parent.parent
LOCALES = ("en", "es", "pt")
# catalog.rs::PLACEHOLDER_SIG_PREFIX
PLACEHOLDER_PREFIX = "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8"

errors = []
def err(msg): errors.append(msg)


def load_schema(path):
    if path:
        return json.loads(pathlib.Path(path).read_text())
    with urllib.request.urlopen(SCHEMA_URL, timeout=30) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", help="local manifest.schema.json (default: fetch from the core repo)")
    ap.add_argument("--expect-signed", action="store_true",
                    help="refuse the documented placeholder signature. Off by default so a "
                         "work-in-progress package still validates; ON in the CI job that "
                         "gates merges, because a placeholder in main is a package the "
                         "control plane will reject as UNSIGNED.")
    args = ap.parse_args()

    try:
        import yaml
    except ImportError:
        sys.exit("pyyaml is required: pip install pyyaml jsonschema")
    try:
        import jsonschema
    except ImportError:
        sys.exit("jsonschema is required: pip install pyyaml jsonschema")

    schema = load_schema(args.schema)
    catalog = json.loads((ROOT / "catalog.json").read_text())

    if catalog.get("schema_version") != "1.0":
        err(f'catalog.json: schema_version is {catalog.get("schema_version")!r}, expected "1.0"')

    rows = {e["id"]: e for e in catalog["integrations"]}
    dirs = {p.name for p in (ROOT / "integrations").iterdir() if p.is_dir()}

    for missing in sorted(dirs - rows.keys()):
        err(f"integrations/{missing}: package with no catalog.json row")
    for missing in sorted(rows.keys() - dirs):
        err(f"catalog.json: row {missing!r} has no package directory")

    for pid in sorted(dirs & rows.keys()):
        pkg = ROOT / "integrations" / pid
        try:
            m = yaml.safe_load((pkg / "manifest.yaml").read_text())
        except Exception as e:
            err(f"{pid}/manifest.yaml: {e}")
            continue

        try:
            jsonschema.validate(m, schema)
        except jsonschema.ValidationError as e:
            err(f"{pid}/manifest.yaml: {'/'.join(str(x) for x in e.path)}: {e.message}")

        if m.get("id") != pid:
            err(f"{pid}/manifest.yaml: id is {m.get('id')!r}, must match the directory name")

        row = rows[pid]
        for field in ("version", "title", "summary", "min_core_version"):
            if m.get(field) != row.get(field):
                err(f"{pid}: manifest {field} differs from its catalog.json row")

        for loc in LOCALES:
            for field in ("title", "summary"):
                if not row.get(field, {}).get(loc):
                    err(f"catalog.json: {pid}.{field} is missing the {loc!r} locale")

        # Every asset the manifest names exists; nothing else is in the directory.
        named = set(m.get("assets", {}).values())
        on_disk = {p.name for p in pkg.iterdir() if p.name != "manifest.yaml"}
        for f in sorted(named - on_disk):
            err(f"{pid}: manifest names {f!r} but the file is not there")
        for f in sorted(on_disk - named):
            err(f"{pid}: {f!r} is in the package but no manifest field names it")

        # pipeline and index_template travel together or not at all.
        a = m.get("assets", {})
        if ("pipeline" in a) != ("index_template" in a):
            err(f"{pid}: assets.pipeline and assets.index_template must both be present or both absent")

        # Teardown must cover the dashboard the manifest advertises.
        td = m.get("teardown", {})
        if m.get("dashboard") not in td.get("saved_objects", []):
            err(f"{pid}: teardown.saved_objects does not include the dashboard {m.get('dashboard')!r}")
        if ("pipeline" in a) and not td.get("ingest_pipeline"):
            err(f"{pid}: ships a pipeline but teardown.ingest_pipeline is unset")
        if ("index_template" in a) and not td.get("index_template"):
            err(f"{pid}: ships an index template but teardown.index_template is unset")

        sig = m.get("signature", {})
        if sig.get("algorithm") != "ed25519":
            err(f"{pid}: signature.algorithm is {sig.get('algorithm')!r}, only ed25519 is supported")
        # The staging placeholder, spelled the same way catalog.rs spells it.
        # Keep the two in step: this is the string the core reports as UNSIGNED.
        if args.expect_signed and str(sig.get("value", "")).startswith(PLACEHOLDER_PREFIX):
            err(f"{pid}: still carries the placeholder signature — sign it with "
                f"`velox sign integrations/{pid} --key <key>` before merging")

        for line_no, line in enumerate((pkg / "saved-objects.ndjson").read_text().splitlines(), 1):
            if not line.strip():
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                err(f"{pid}/saved-objects.ndjson:{line_no}: not valid JSON: {e}")

    if errors:
        print(f"{len(errors)} problem(s):", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        sys.exit(1)
    signed = " and signed" if args.expect_signed else ""
    print(f"{len(dirs)} packages validated: schema, catalog consistency, layout, teardown{signed}.")


if __name__ == "__main__":
    main()
