#!/usr/bin/env python3
"""Validate the Fluent Bit plugin catalogue (fluent-bit/<docs-version>/**.yaml).

- each file validates against schemas/plugin.schema.json
- file name == `name`, directory == kind
- no excluded plugin (Spec 2.0 §9 allowlist; rule R16)
- docs_url is on docs.fluentbit.io
- param keys unique; `secret` params are `password`; select params have options
- i18n: every description/title carries en, es and pt (R17)

Usage: scripts/check_catalog.py [file ...]   (default: every file)
"""
import json, pathlib, sys

try:
    import yaml
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
except ImportError:
    sys.exit("requires: pip install pyyaml jsonschema referencing")

ROOT = pathlib.Path(__file__).resolve().parent.parent
CAT = ROOT / "fluent-bit"
SCHEMAS = ROOT / "schemas"

EXCLUDED = {
    "input": {"exec", "exec_wasi", "dummy", "random", "stdin"},
    "filter": {"lua", "wasm", "tensorflow"},
    "processor": {"fluent_typed_scripting"},
}
KIND_DIR = {
    "input": "inputs", "filter": "filters", "processor": "processors",
    "parser_format": "parsers", "multiline_parser": "multiline",
}
LOCALES = ("en", "es", "pt")

schemas = {p.name: json.loads(p.read_text()) for p in SCHEMAS.glob("*.schema.json")}
registry = Registry().with_resources((s["$id"], Resource.from_contents(s)) for s in schemas.values())
validator = Draft202012Validator(schemas["plugin.schema.json"], registry=registry)

errors = []


def check(path: pathlib.Path):
    rel = path.relative_to(ROOT)
    try:
        doc = yaml.safe_load(path.read_text())
    except Exception as e:  # noqa: BLE001
        errors.append(f"{rel}: YAML: {e}")
        return
    for e in sorted(validator.iter_errors(doc), key=lambda e: list(e.path)):
        errors.append(f"{rel}: {'/'.join(map(str, e.path)) or '(root)'}: {e.message}")
    if not isinstance(doc, dict):
        return
    kind, name = doc.get("kind"), doc.get("name")
    if name and path.stem != name:
        errors.append(f"{rel}: file name must equal name ({name!r})")
    if kind in KIND_DIR and path.parent.name != KIND_DIR[kind]:
        errors.append(f"{rel}: kind {kind!r} belongs under {KIND_DIR[kind]}/")
    if name in EXCLUDED.get(kind, ()):
        errors.append(f"{rel}: {name!r} executes code or is a test plugin; it is not allow-listed (R16)")

    def i18n(obj, where):
        if isinstance(obj, dict):
            for loc in LOCALES:
                if not obj.get(loc):
                    errors.append(f"{rel}: {where} is missing the {loc!r} locale (R17)")

    i18n(doc.get("title"), "title")
    i18n(doc.get("description"), "description")
    seen = set()
    for p in doc.get("params") or []:
        if not isinstance(p, dict):
            continue
        k = p.get("key")
        if k in seen:
            errors.append(f"{rel}: duplicate param {k!r}")
        seen.add(k)
        i18n(p.get("description"), f"params.{k}.description")
        if p.get("secret") and p.get("type") != "password":
            errors.append(f"{rel}: params.{k}: secret params must be type password")
        if p.get("type") == "select" and not p.get("options"):
            errors.append(f"{rel}: params.{k}: select without options")
        if p.get("multi") == "join" and not p.get("join"):
            errors.append(f"{rel}: params.{k}: multi join needs a `join` separator")
        if k in {"tag", "alias", "log_level", "match", "processors", "threaded"} or str(k).startswith("storage."):
            errors.append(f"{rel}: params.{k}: belongs to the compiler, not the catalogue")


files = [pathlib.Path(a).resolve() for a in sys.argv[1:]] or sorted(CAT.rglob("*.yaml"))
for f in files:
    check(f)

if errors:
    print(f"{len(errors)} problem(s):", file=sys.stderr)
    for e in errors:
        print(f"  {e}", file=sys.stderr)
    sys.exit(1)
print(f"catalogue: {len(files)} plugin file(s) valid.")
