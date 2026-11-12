#!/usr/bin/env python3
"""Validate Spec 2.0 packages: JSON Schemas plus the cross-file rules R1..R23
of docs/spec/README.md §14 (R16 lives in check_catalog.py; R24 in CI with an
OpenSearch container, scripts/pipeline_test.py).

Usage:
  scripts/validate_v2.py                       # every packages/<id>/<version>
  scripts/validate_v2.py packages/nginx/1.0.0  # one version
  scripts/validate_v2.py --examples            # also docs/spec/examples
  --catalog fluent-bit/5.2                     # catalogue to check against (default: newest)
  --expect-signed                              # refuse the placeholder signature
  --base-ref main                              # R19/R21: compare with versions on that git ref
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

try:
    import yaml
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
except ImportError:
    sys.exit("requires: pip install pyyaml jsonschema referencing")

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import v2lib as L  # noqa: E402

errors: list[str] = []


def err(msg):
    errors.append(msg)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

schemas = {p.name: json.loads(p.read_text()) for p in L.SCHEMAS.glob("*.schema.json")}
registry = Registry().with_resources((s["$id"], Resource.from_contents(s)) for s in schemas.values())


def schema_check(name, doc, label) -> bool:
    v = Draft202012Validator(schemas[name], registry=registry)
    errs = sorted(v.iter_errors(doc), key=lambda e: list(e.path))
    for e in errs:
        err(f"{label}: {'/'.join(map(str, e.path)) or '(root)'}: {e.message}")
    return not errs


# ---------------------------------------------------------------------------
# Type compatibility field -> catalogue param (R6)
# ---------------------------------------------------------------------------

COMPAT = {
    "string": {"string", "text", "regex", "duration", "size", "select"},
    "text": {"text", "string"},
    "integer": {"integer", "number"},
    "number": {"number"},
    "bool": {"bool"},
    "select": {"select", "string", "integer"},
    "duration": {"duration", "string", "integer"},
    "size": {"size", "string"},
    "regex": {"regex", "string"},
    "password": {"password", "string"},
}


def default_matches(field: dict) -> bool:
    t, d = field.get("type"), field.get("default")
    if d is None:
        return True
    vals = d if isinstance(d, list) else [d]
    if isinstance(d, list) and not field.get("multi"):
        return False
    for v in vals:
        if t in ("string", "text", "regex", "password"):
            if not isinstance(v, str):
                return False
        elif t == "integer":
            if not isinstance(v, int) or isinstance(v, bool):
                return False
        elif t == "number":
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                return False
        elif t == "bool":
            if not isinstance(v, bool):
                return False
        elif t == "duration":
            if not re.fullmatch(r"[0-9]+(ms|s|m|h|d)", str(v)):
                return False
        elif t == "size":
            if not re.fullmatch(r"[0-9]+([kKmMgGtT][bB]?|[bB])?", str(v)):
                return False
        elif t == "select":
            opts = [o["value"] if isinstance(o, dict) else o for o in field.get("options") or []]
            if field.get("options") and v not in opts:
                return False
        elif t == "yaml":
            if not isinstance(v, dict):
                return False
    return True


# ---------------------------------------------------------------------------
# Per-package checks
# ---------------------------------------------------------------------------

I18N_KEYS = ("title", "summary", "description")


def check_i18n(obj, where):
    if isinstance(obj, dict) and "en" in obj:
        for loc in ("en", "es", "pt"):
            if not obj.get(loc):
                err(f"{where}: missing {loc!r} locale (R17)")


def walk_i18n(doc, where):
    if isinstance(doc, dict):
        for k, v in doc.items():
            if k in I18N_KEYS and isinstance(v, dict):
                check_i18n(v, f"{where}.{k}")
            elif k == "options" and isinstance(v, list):
                for i, o in enumerate(v):
                    if isinstance(o, dict) and isinstance(o.get("title"), dict):
                        check_i18n(o["title"], f"{where}.options[{i}].title")
            else:
                walk_i18n(v, f"{where}.{k}")
    elif isinstance(doc, list):
        for i, v in enumerate(doc):
            walk_i18n(v, f"{where}[{i}]")


def check_fixed_refs(fixed: dict, where):
    for k, v in (fixed or {}).items():
        vals = v if isinstance(v, list) else [v]
        for val in vals:
            if isinstance(val, str):
                if L.ENV_RE.search(val):
                    err(f"{where}.fixed.{k}: `${{...}}` is not allowed in a package (R7)")
                for m in L.REF_RE.finditer(val):
                    if m.group(1) not in L.CONTEXT_REFS:
                        err(f"{where}.fixed.{k}: unknown context reference {{{m.group(1)}}} (R7)")


def check_fields_against_plugin(fields, fixed, plugin_doc, cat: L.Catalog, where):
    params = cat.params(plugin_doc) if plugin_doc else {}
    names = set()
    for f in fields:
        n = f.get("name")
        if n in names:
            err(f"{where}: duplicate field {n!r}")
        names.add(n)
        if not default_matches(f):
            err(f"{where}.{n}: default does not match type/options (R8)")
        b = f.get("bind") or {}
        if "key" in b:
            k = b["key"]
            if k in (fixed or {}):
                err(f"{where}.{n}: binds key {k!r} that `fixed` already sets (R6)")
            if plugin_doc is None:
                continue
            p = params.get(k)
            if p is None:
                err(f"{where}.{n}: key {k!r} is not a parameter of plugin {plugin_doc['name']!r} (R6)")
                continue
            if p.get("operator_settable") is False:
                err(f"{where}.{n}: {k!r} is not operator-settable; use `fixed` (R6)")
            if p.get("secret") and f.get("type") != "password":
                err(f"{where}.{n}: {k!r} is a secret; the field must be `password` (R6)")
            if p.get("type") not in COMPAT.get(f.get("type"), set()) and f.get("type") != "yaml":
                err(f"{where}.{n}: field type {f.get('type')!r} is not compatible with {k!r} ({p.get('type')!r}) (R6)")
            if f.get("multi"):
                pm = p.get("multi", "no")
                if pm == "no":
                    err(f"{where}.{n}: {k!r} does not take several values (R6)")
                elif pm == "join" and "join" not in b:
                    err(f"{where}.{n}: {k!r} takes a joined string; bind needs `join` (R6)")
                elif pm == "repeat" and not b.get("repeat"):
                    err(f"{where}.{n}: {k!r} is a repeated key; bind needs `repeat: true` (R6)")
        elif "merge" in b:
            if f.get("type") != "yaml":
                err(f"{where}.{n}: `merge` binding only for `yaml` fields (R6)")
    # show_if targets
    for f in fields:
        s = f.get("show_if")
        if s and s.get("field") not in names:
            err(f"{where}.{f.get('name')}: show_if references unknown field {s.get('field')!r} (R8)")
    return names


def check_stream(pkg: L.Package, st: L.Stream, cat: L.Catalog | None):
    where = f"{pkg.id}/{pkg.version}/streams/{st.id}"
    if not st.doc:
        err(f"{where}: stream.yaml missing (R3)")
        return
    if not schema_check("stream.schema.json", st.doc, where):
        return
    if st.doc.get("id") != st.id:
        err(f"{where}: stream id {st.doc.get('id')!r} != directory (R3)")
    walk_i18n(st.doc, where)
    pkg_os = set((pkg.manifest.get("compatibility") or {}).get("os") or [])
    st_os = set(st.doc.get("os") or pkg_os)
    if not st_os <= pkg_os:
        err(f"{where}: os {sorted(st_os - pkg_os)} not in compatibility.os (R4)")

    name = L.artifact_name(st.id, pkg.id, pkg.version)
    if len(name) > 200 or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", name):
        err(f"{where}: artifact name {name!r} invalid (R22)")

    inp = st.doc["input"]
    plugin = inp["plugin"]
    pdoc = cat.get("input", plugin) if cat else None
    if cat and pdoc is None:
        err(f"{where}: input plugin {plugin!r} is not in the catalogue (R5)")
    if pdoc:
        if not st_os <= set(pdoc.get("os") or []):
            err(f"{where}: plugin {plugin!r} does not support os {sorted(st_os - set(pdoc.get('os') or []))} (R5)")
        if st.doc["event_type"] not in (pdoc.get("event_types") or []):
            err(f"{where}: plugin {plugin!r} does not emit {st.doc['event_type']!r} (R9)")
        for k in (inp.get("fixed") or {}):
            if k not in cat.params(pdoc):
                err(f"{where}: fixed key {k!r} is not a parameter of {plugin!r} (R6)")
    check_fixed_refs(inp.get("fixed"), where + ".input")
    check_fields_against_plugin(inp.get("fields") or [], inp.get("fixed"), pdoc, cat, where + ".input")

    # parsers (R14)
    pnames = set()
    for p in st.doc.get("parsers") or []:
        if p["name"] in pnames:
            err(f"{where}: duplicate parser {p['name']!r} (R14)")
        pnames.add(p["name"])
        if p["format"] == "regex":
            try:
                re.compile(p["regex"])
            except re.error as e:
                err(f"{where}: parser {p['name']!r}: regex does not compile: {e} (R14)")
    for mp in st.doc.get("multiline_parsers") or []:
        if mp["name"] in pnames:
            err(f"{where}: multiline parser {mp['name']!r} clashes with a parser name (R14)")
        if mp["type"] == "regex" and mp["rules"][0].get("state") != "start_state":
            err(f"{where}: multiline parser {mp['name']!r}: first rule must be start_state (R14)")
    pf = st.doc.get("parser_field") or {}
    if pf.get("default") not in (None, "none") and pf.get("default") not in pnames:
        err(f"{where}: parser_field.default {pf.get('default')!r} is not a parser of the stream (R14)")

    # processors (R12, R13)
    procs = st.doc.get("processors") or {}
    ids = set()
    for item in procs.get("defaults") or []:
        pid = item["id"]
        if pid in ids:
            err(f"{where}: duplicate processor id {pid!r} (R13)")
        ids.add(pid)
        pl = item["plugin"]
        found = cat.chain_plugin(pl) if cat else None
        if cat and not found:
            err(f"{where}: processor {pid!r}: plugin {pl!r} is not a filter/processor of the catalogue (R12)")
        cdoc = found[1] if found else None
        if cdoc and st.doc["event_type"] not in (cdoc.get("event_types") or []):
            err(f"{where}: processor {pid!r}: {pl!r} does not accept {st.doc['event_type']!r} (R12)")
        check_fixed_refs(item.get("fixed"), f"{where}.processors.{pid}")
        if cdoc:
            for k in (item.get("fixed") or {}):
                if k not in cat.params(cdoc):
                    err(f"{where}.processors.{pid}: fixed key {k!r} is not a parameter of {pl!r} (R6)")
        check_fields_against_plugin(item.get("fields") or [], item.get("fixed"), cdoc, cat, f"{where}.processors.{pid}")
    for pl in procs.get("allow") or []:
        found = cat.chain_plugin(pl) if cat else None
        if cat and not found:
            err(f"{where}: allow: {pl!r} is not a filter/processor of the catalogue (R12)")
        elif found and st.doc["event_type"] not in (found[1].get("event_types") or []):
            err(f"{where}: allow: {pl!r} does not accept {st.doc['event_type']!r} (R12)")

    # backend (R10, R11, R15)
    be = st.doc.get("backend") or {}
    et = st.doc["event_type"]
    if et == "metrics":
        for k in ("index_template", "ingest_pipeline", "lifecycle", "fields"):
            if k in be:
                err(f"{where}: metrics stream must not declare backend.{k} (R10)")
        return
    tpl_file = st.dir / be.get("index_template", "")
    if not be.get("index_template") or not tpl_file.is_file():
        err(f"{where}: backend.index_template missing or file absent (R11)")
        tpl = {}
    else:
        tpl = L.load_json(tpl_file)
        t = tpl.get("template") or {}
        if not isinstance(t, dict) or not t.get("mappings"):
            err(f"{where}: index-template.json must be {{\"template\": {{\"settings\", \"mappings\"}}}} (R11)")
        for k in ("index_patterns", "data_stream", "composed_of", "priority"):
            if k in tpl:
                err(f"{where}: index template must not declare {k!r}; the core sets it (R11)")
        if "default_pipeline" in json.dumps(t.get("settings") or {}):
            err(f"{where}: index template must not fix default_pipeline (R11)")
    tags = set()
    if be.get("ingest_pipeline"):
        pfile = st.dir / be["ingest_pipeline"]
        if not pfile.is_file():
            err(f"{where}: ingest_pipeline file {be['ingest_pipeline']!r} absent (R15)")
        else:
            pipe = L.load_json(pfile)
            for proc in pipe.get("processors") or []:
                for _ptype, body in proc.items():
                    if isinstance(body, dict) and body.get("tag"):
                        tags.add(body["tag"])
    for f in be.get("fields") or []:
        b = f.get("bind") or {}
        n = f.get("name")
        if "pipeline_toggle" in b:
            if b["pipeline_toggle"] not in tags:
                err(f"{where}.backend.{n}: pipeline_toggle {b['pipeline_toggle']!r} is not a tag of the pipeline (R15)")
            if f.get("type") != "bool":
                err(f"{where}.backend.{n}: pipeline_toggle needs a bool field (R15)")
        elif "pipeline_param" in b:
            tag = b["pipeline_param"].split(".", 1)[0]
            if tag not in tags:
                err(f"{where}.backend.{n}: pipeline_param tag {tag!r} is not a tag of the pipeline (R15)")
        elif "lifecycle" in b and not be.get("lifecycle"):
            err(f"{where}.backend.{n}: lifecycle binding but backend.lifecycle is absent (R15)")
        elif "template" in b and not be.get("index_template"):
            err(f"{where}.backend.{n}: template binding but no index_template (R15)")
        elif "key" in b or "merge" in b:
            err(f"{where}.backend.{n}: backend fields cannot bind plugin keys (R15)")
    sample = st.dir / "sample-event.json"
    if not sample.is_file():
        err(f"{where}: sample-event.json missing")


def check_dashboards(pkg: L.Package):
    where = f"{pkg.id}/{pkg.version}"
    ids = {}
    refs = []
    for rel in pkg.manifest.get("dashboards") or []:
        f = pkg.dir / rel
        if not f.is_file():
            err(f"{where}: dashboards file {rel!r} absent (R18)")
            continue
        for ln, line in enumerate(f.read_text().splitlines(), 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                err(f"{where}/{rel}:{ln}: not JSON: {e}")
                continue
            if obj.get("type") == "index-pattern":
                err(f"{where}/{rel}:{ln}: packages must not ship index patterns (R18)")
            oid = obj.get("id")
            if not oid or not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", str(oid)):
                err(f"{where}/{rel}:{ln}: saved object id {oid!r} must be a local slug (R18)")
            if oid in ids:
                err(f"{where}/{rel}:{ln}: duplicate saved object id {oid!r} (R18)")
            ids[oid] = obj.get("type")
            for r in obj.get("references") or []:
                refs.append((rel, ln, r))
    stream_ids = {s.id: s.doc.get("event_type") for s in pkg.streams}
    for rel, ln, r in refs:
        rid = str(r.get("id", ""))
        if r.get("type") == "index-pattern":
            if not rid.startswith("stream:"):
                err(f"{where}/{rel}:{ln}: index-pattern reference must be `stream:<id>` (R18)")
            elif stream_ids.get(rid[7:]) not in ("logs", "traces"):
                err(f"{where}/{rel}:{ln}: `{rid}` is not a logs/traces stream of the package (R18)")
        elif rid not in ids:
            err(f"{where}/{rel}:{ln}: reference {rid!r} points outside the package (R18)")


def check_package(vdir: pathlib.Path, cat: L.Catalog | None, expect_signed: bool):
    label = vdir.relative_to(L.ROOT).as_posix()
    try:
        pkg = L.load_package(vdir)
    except Exception as e:  # noqa: BLE001
        err(f"{label}: cannot load: {e}")
        return None
    m = pkg.manifest
    if not schema_check("manifest.schema.json", m, label + "/manifest.yaml"):
        return pkg
    if m["id"] != vdir.parent.name or m["version"] != vdir.name:
        err(f"{label}: id/version differ from the directories (R1)")
    walk_i18n({k: v for k, v in m.items() if k in I18N_KEYS}, label)

    # R2 inventory
    disk = dict(L.inventory(vdir))
    listed = {f["path"]: f["sha256"] for f in m["files"]}
    for p in sorted(set(disk) - set(listed)):
        err(f"{label}: {p!r} on disk but not in files: (R2)")
    for p in sorted(set(listed) - set(disk)):
        err(f"{label}: files: lists {p!r} which is absent (R2)")
    for p in sorted(set(listed) & set(disk)):
        if listed[p] != disk[p]:
            err(f"{label}: sha256 of {p!r} differs from files: (R2)")
    for rel in [m.get("icon"), m.get("changelog"), *((m.get("docs") or {}).values())]:
        if rel and rel not in listed:
            err(f"{label}: manifest names {rel!r} which is not in files: (R2)")

    # R3 streams == dirs
    sdirs = {d.name for d in (vdir / "streams").iterdir() if d.is_dir()} if (vdir / "streams").is_dir() else set()
    for extra in sorted(sdirs - set(m["streams"])):
        err(f"{label}: streams/{extra} exists but is not in manifest.streams (R3)")

    # R4
    comp = m["compatibility"]
    if L.semver_key(comp["min_fluent_bit_version"]) < L.semver_key("3.2.0"):
        err(f"{label}: min_fluent_bit_version must be >= 3.2.0 (R4)")

    for st in pkg.streams:
        check_stream(pkg, st, cat)
    check_dashboards(pkg)

    # R23 changelog
    if m.get("changelog"):
        cl = L.load_yaml(vdir / m["changelog"])
        if schema_check("changelog.schema.json", cl, label + "/" + m["changelog"]):
            if not any(e["version"] == m["version"] for e in cl):
                err(f"{label}: changelog has no entry for {m['version']} (R23)")
            walk_i18n(cl, label + "/changelog")

    sig = m["signature"]["value"]
    if expect_signed and sig.startswith(L.PLACEHOLDER_SIG_PREFIX):
        err(f"{label}: still carries the placeholder signature; sign before merging")
    return pkg


# ---------------------------------------------------------------------------
# Cross-version rules (R19, R20, R21) against a git ref
# ---------------------------------------------------------------------------

def git_versions(base_ref: str, pkg_id: str) -> dict[str, str]:
    """version -> manifest text on base_ref."""
    out = {}
    r = subprocess.run(["git", "ls-tree", "--name-only", base_ref, f"packages/{pkg_id}/"],
                       capture_output=True, text=True, cwd=L.ROOT)
    for line in r.stdout.split():
        ver = line.rstrip("/").rsplit("/", 1)[-1]
        show = subprocess.run(["git", "show", f"{base_ref}:packages/{pkg_id}/{ver}/manifest.yaml"],
                              capture_output=True, text=True, cwd=L.ROOT)
        if show.returncode == 0:
            out[ver] = show.stdout
    return out


def mapping_fields(tpl: dict, prefix="") -> dict[str, str]:
    out = {}
    for name, body in ((tpl.get("properties") or {}).items()):
        full = f"{prefix}{name}"
        if "type" in body:
            out[full] = body["type"]
        if "properties" in body:
            out.update(mapping_fields(body, full + "."))
    return out


def check_history(pkg: L.Package, base_ref: str):
    label = f"{pkg.id}/{pkg.version}"
    published = git_versions(base_ref, pkg.id)
    if pkg.version in published:
        if published[pkg.version] != (pkg.dir / "manifest.yaml").read_text():
            err(f"{label}: version already published on {base_ref}; a change needs a new version (R19)")
        return
    newer = [v for v in published if L.semver_key(v) >= L.semver_key(pkg.version)]
    if newer:
        err(f"{label}: {base_ref} already has {sorted(newer)}; new version must be greater (R21)")
    same_major = [v for v in published if L.major_of(v) == L.major_of(pkg.version)]
    if same_major:
        prev = max(same_major, key=L.semver_key)
        for st in pkg.streams:
            r = subprocess.run(["git", "show", f"{base_ref}:packages/{pkg.id}/{prev}/streams/{st.id}/index-template.json"],
                               capture_output=True, text=True, cwd=L.ROOT)
            if r.returncode or not (st.doc.get("backend") or {}).get("index_template"):
                continue
            old = mapping_fields((json.loads(r.stdout).get("template") or {}).get("mappings") or {})
            new = mapping_fields((L.load_json(st.dir / st.doc["backend"]["index_template"]).get("template") or {}).get("mappings") or {})
            for f, t in old.items():
                if f not in new:
                    err(f"{label}/streams/{st.id}: mapping field {f!r} removed within major {L.major_of(pkg.version)} (R20)")
                elif new[f] != t:
                    err(f"{label}/streams/{st.id}: mapping field {f!r} changed type {t}->{new[f]} within a major (R20)")


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*", help="package version dirs (default: every packages/<id>/<version>)")
    ap.add_argument("--catalog", help="fluent-bit/<version> dir (default: newest)")
    ap.add_argument("--no-catalog", action="store_true", help="skip catalogue-dependent rules")
    ap.add_argument("--examples", action="store_true", help="also validate docs/spec/examples packages")
    ap.add_argument("--expect-signed", action="store_true")
    ap.add_argument("--base-ref", help="git ref to check R19/R20/R21 against (e.g. origin/main)")
    args = ap.parse_args()

    cat = None
    if not args.no_catalog:
        cdir = pathlib.Path(args.catalog) if args.catalog else L.latest_catalog_dir()
        if cdir and cdir.is_dir():
            cat = L.load_catalog(cdir)
        else:
            print("warning: no catalogue found; catalogue rules skipped", file=sys.stderr)

    dirs = [pathlib.Path(p).resolve() for p in args.paths] or list(L.iter_package_dirs(L.PACKAGES))
    if args.examples:
        dirs += list(L.iter_package_dirs(L.ROOT / "docs" / "spec" / "examples"))
    if not dirs:
        print("no packages to validate")
        return

    seen = set()
    for d in dirs:
        pkg = check_package(d, cat, args.expect_signed)
        if pkg:
            key = (pkg.id, pkg.version)
            if key in seen and d.is_relative_to(L.PACKAGES):
                err(f"{d}: duplicate package version")
            seen.add(key)
            if args.base_ref and d.is_relative_to(L.PACKAGES):
                check_history(pkg, args.base_ref)

    if errors:
        print(f"{len(errors)} problem(s):", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        sys.exit(1)
    print(f"{len(dirs)} package version(s) valid" + (f" against catalogue {cat.version}" if cat else "") + ".")


if __name__ == "__main__":
    main()
