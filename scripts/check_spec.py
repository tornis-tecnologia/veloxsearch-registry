#!/usr/bin/env python3
"""Conformance check of the Spec 2.0 schemas against the examples in docs/spec/examples.

1. Every schema in schemas/ is a valid draft 2020-12 schema.
2. Every example validates against its schema.
3. A set of known-bad variants is REJECTED (so a schema loosened by mistake fails CI).
4. The example package's `files:` inventory is current (scripts/inventory.py --check).

This checks shapes only. The cross-file rules R1..R24 of docs/spec/README.md
are enforced by scripts/validate_v2.py (phase F3).

Usage: scripts/check_spec.py
"""
import copy, json, pathlib, subprocess, sys

try:
    import yaml
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
except ImportError:
    sys.exit("requires: pip install pyyaml jsonschema referencing")

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas"
EX = ROOT / "docs" / "spec" / "examples"
PKG = EX / "custom-logs" / "1.0.0"

failures = []


def load(p: pathlib.Path):
    text = p.read_text()
    return json.loads(text) if p.suffix == ".json" else yaml.safe_load(text)


schemas = {p.name: json.loads(p.read_text()) for p in sorted(SCHEMAS.glob("*.schema.json"))}
registry = Registry().with_resources(
    (s["$id"], Resource.from_contents(s)) for s in schemas.values()
)


def validator(name):
    return Draft202012Validator(schemas[name], registry=registry)


for name, s in schemas.items():
    try:
        Draft202012Validator.check_schema(s)
    except Exception as e:  # noqa: BLE001 - report and keep going
        failures.append(f"schemas/{name}: not a valid schema: {e}")


def expect_valid(schema, doc, label):
    errs = sorted(validator(schema).iter_errors(doc), key=lambda e: list(e.path))
    for e in errs:
        failures.append(f"{label}: {'/'.join(map(str, e.path)) or '(root)'}: {e.message}")


def expect_invalid(schema, doc, label):
    if not list(validator(schema).iter_errors(doc)):
        failures.append(f"known-bad variant ACCEPTED: {label}")


manifest = load(PKG / "manifest.yaml")
stream = load(PKG / "streams" / "log" / "stream.yaml")
expect_valid("manifest.schema.json", manifest, "custom-logs/manifest.yaml")
expect_valid("stream.schema.json", stream, "custom-logs/streams/log/stream.yaml")
expect_valid("changelog.schema.json", load(PKG / "changelog.yaml"), "custom-logs/changelog.yaml")
expect_valid("activation.schema.json", load(EX / "activations" / "custom-logs.json"), "activations/custom-logs.json")
expect_valid("plugin.schema.json", load(EX / "fluent-bit" / "tail.yaml"), "fluent-bit/tail.yaml")
expect_valid("index.schema.json", {
    "spec_version": "2.0",
    "generated_at": "2026-11-12T00:00:00Z",
    "packages": [{
        "id": "custom-logs", "title": manifest["title"], "summary": manifest["summary"],
        "categories": manifest["categories"], "latest": "1.0.0",
        "versions": [{
            "version": "1.0.0", "release": "ga", "path": "custom-logs/1.0.0/",
            "manifest_sha256": "0" * 64, "min_mesh_version": "0.15.0",
            "min_agent_version": "0.2.0", "min_fluent_bit_version": "3.2.0",
            "os": ["linux"], "signals": ["logs"], "event_types": ["logs"],
        }],
    }],
}, "index (synthetic)")


def variant(doc, mutate):
    d = copy.deepcopy(doc)
    mutate(d)
    return d


bad_streams = {
    "stream id with a dot (breaks veloxagent-<stream>.<integração>)":
        lambda s: s.update(id="app.log"),
    "password field with a default":
        lambda s: s["input"]["fields"].append({
            "name": "token", "type": "password", "title": {"en": "Token"},
            "default": "x", "bind": {"key": "http_passwd"}}),
    "bind with both join and repeat":
        lambda s: s["input"]["fields"][0]["bind"].update(repeat=True),
    "select without options":
        lambda s: s["input"]["fields"].append({
            "name": "mode", "type": "select", "title": {"en": "Mode"}, "bind": {"key": "mode"}}),
    "yaml field outside the advanced group":
        lambda s: s["input"]["fields"].append({
            "name": "extra", "type": "yaml", "title": {"en": "Extra"}, "bind": {"merge": True}}),
    "metrics event_type with an index template":
        lambda s: s.update(event_type="metrics"),
    "logs event_type without backend":
        lambda s: s.pop("backend"),
    "regex parser without regex":
        lambda s: s["parsers"].append({"name": "r", "format": "regex"}),
    "unknown top-level key":
        lambda s: s.update(output={"name": "opensearch"}),
    "control character in a fixed value":
        lambda s: s["input"]["fixed"].update(db="a\nb"),
    "missing event_type":
        lambda s: s.pop("event_type"),
}
for label, mutate in bad_streams.items():
    expect_invalid("stream.schema.json", variant(stream, mutate), f"stream: {label}")

bad_manifests = {
    "spec_version 1.2": lambda m: m.update(spec_version="1.2"),
    "path traversal in files": lambda m: m["files"].append({"path": "../x", "sha256": "0" * 64}),
    "absolute icon path": lambda m: m.update(icon="/etc/passwd"),
    "unknown category": lambda m: m.update(categories=["misc"]),
    "no streams": lambda m: m.update(streams=[]),
    "output declared by the package": lambda m: m.update(outputs=[{"name": "opensearch"}]),
}
for label, mutate in bad_manifests.items():
    expect_invalid("manifest.schema.json", variant(manifest, mutate), f"manifest: {label}")

r = subprocess.run([sys.executable, str(ROOT / "scripts" / "inventory.py"), str(PKG), "--check"],
                   capture_output=True, text=True)
if r.returncode:
    failures.append((r.stderr or r.stdout).strip())

if failures:
    print(f"{len(failures)} problem(s):", file=sys.stderr)
    for f in failures:
        print(f"  {f}", file=sys.stderr)
    sys.exit(1)
print(f"spec 2.0: {len(schemas)} schemas valid; examples conform; "
      f"{len(bad_streams) + len(bad_manifests)} known-bad variants rejected; inventory current.")
