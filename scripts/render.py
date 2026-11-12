#!/usr/bin/env python3
"""Reference compiler: package + activation + policy context -> Fluent Bit YAML.

This is the executable form of docs/mesh-integration-guide.md §7. The core's
compiler must produce equivalent output for the same inputs; CI runs
`fluent-bit --dry-run` on what this emits for every package's defaults.

Usage:
  scripts/render.py packages/<id>/<version> [--activation a.json] [--context c.json]
                    [--catalog fluent-bit/5.2] [--format yaml|json] [--backend]

No activation = every `enabled: true` stream with default values. No context
= the example context below (an internal OpenSearch endpoint, no OTLP).
--backend prints, instead of the Fluent Bit config, the OpenSearch objects the
core would install (component templates, pipeline, ISM policy, index template).
"""
from __future__ import annotations

import argparse
import copy
import fnmatch
import json
import pathlib
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import v2lib as L  # noqa: E402

DEFAULT_CONTEXT = {
    "deployment": "demo",
    "state_dir": "/var/lib/velox-agent/fluent-bit/state",
    "service": {"flush": 5, "log_level": "info", "storage_path": "/var/lib/velox-agent/fluent-bit/storage"},
    "opensearch": {"host": "10.43.207.250", "port": 9200, "tls": True, "tls_verify": False, "path": None},
    "otlp": None,  # {"host": ..., "port": 4318, "tls": True, "tls_verify": True, "path": "/v1/metrics"}
}


class RenderError(Exception):
    pass


# ---------------------------------------------------------------------------
# Values: defaults + activation, typed
# ---------------------------------------------------------------------------

def field_values(fields: list[dict], given: dict | None) -> dict:
    given = given or {}
    out = {}
    names = {f["name"] for f in fields}
    for k in given:
        if k not in names:
            raise RenderError(f"unknown field {k!r}")
    for f in fields:
        n = f["name"]
        if n in given:
            v = given[n]
        elif "default" in f:
            v = f["default"]
        else:
            if f.get("required"):
                raise RenderError(f"required field {n!r} has no value")
            continue
        if f.get("type") == "password":
            if not (isinstance(v, dict) and "$secret" in v):
                raise RenderError(f"password field {n!r} must be a {{\"$secret\": id}} reference")
            v = "${VELOX_SECRET_" + v["$secret"].upper().replace("-", "_") + "}"
        if isinstance(v, str) and L.CONTROL_RE.search(v):
            raise RenderError(f"field {n!r}: control character in value")
        out[n] = v
    return out


def visible(f: dict, values: dict) -> bool:
    s = f.get("show_if")
    if not s:
        return True
    v = values.get(s["field"])
    return v == s.get("equals") if "equals" in s else v in s.get("in", [])


def apply_bindings(fields: list[dict], values: dict, target: dict, where: str):
    """Fill plugin keys from field values (bindings of kind key/merge)."""
    for f in fields:
        n = f["name"]
        if n not in values or not visible(f, values):
            continue
        v = values[n]
        b = f["bind"]
        if "key" in b:
            if "omit_if" in b and v == b["omit_if"]:
                continue
            if isinstance(v, list):
                if b.get("prefix"):
                    v = [b["prefix"] + str(x) for x in v]
                if "join" in b:
                    v = b["join"].join(str(x) for x in v)
                elif b.get("repeat"):
                    v = list(v)
                else:
                    raise RenderError(f"{where}.{n}: list value without join/repeat")
            elif b.get("prefix"):
                v = b["prefix"] + str(v)
            if b["key"] in target:
                raise RenderError(f"{where}.{n}: key {b['key']!r} already set")
            target[b["key"]] = v
        elif "merge" in b:
            if not isinstance(v, dict):
                raise RenderError(f"{where}.{n}: merge needs an object")
            for k, val in v.items():
                if k in target:
                    raise RenderError(f"{where}.{n}: merge key {k!r} already set")
                target[k] = val


def resolve_fixed(fixed: dict, ctx: dict) -> dict:
    out = {}
    for k, v in (fixed or {}).items():
        if isinstance(v, list):
            out[k] = [L.resolve_refs(x, ctx) if isinstance(x, str) else x for x in v]
        elif isinstance(v, str):
            out[k] = L.resolve_refs(v, ctx)
        else:
            out[k] = v
    return out


def check_added_params(plugin_doc: dict, params: dict, cat: L.Catalog, where: str):
    known = cat.params(plugin_doc)
    for k, v in params.items():
        match = known.get(k) or next((p for key, p in known.items() if "*" in key and fnmatch.fnmatchcase(k, key)), None)
        if match is None:
            raise RenderError(f"{where}: {k!r} is not a parameter of {plugin_doc['name']!r}")
        if match.get("operator_settable") is False:
            raise RenderError(f"{where}: {k!r} cannot be set by the operator")
        if match.get("secret") and not (isinstance(v, str) and v.startswith("${VELOX_SECRET_")):
            raise RenderError(f"{where}: {k!r} is a secret; pass a $secret reference")
        if isinstance(v, str) and L.CONTROL_RE.search(v):
            raise RenderError(f"{where}: {k!r}: control character in value")


# ---------------------------------------------------------------------------
# Compile
# ---------------------------------------------------------------------------

def compile_policy(pkg: L.Package, activation: dict | None, ctx: dict, cat: L.Catalog) -> dict:
    act_streams = (activation or {}).get("streams") or {}
    major = L.major_of(pkg.version)
    doc = {
        "service": {
            "flush": ctx["service"]["flush"],
            "log_level": ctx["service"]["log_level"],
        },
        "parsers": [],
        "multiline_parsers": [],
        "pipeline": {"inputs": [], "filters": [], "outputs": []},
    }
    if ctx["service"].get("storage_path"):
        doc["service"]["storage.path"] = ctx["service"]["storage_path"]

    for st in pkg.streams:
        s = st.doc
        sa = act_streams.get(st.id)
        enabled = sa["enabled"] if sa is not None else s.get("enabled", True)
        if not enabled:
            continue
        tag = L.stream_tag(pkg.id, st.id)
        artifact = L.artifact_name(st.id, pkg.id, pkg.version)
        refs = {
            "stream_tag": tag, "artifact": artifact, "state_dir": ctx["state_dir"],
            "integration": pkg.id, "stream": st.id, "package_version": pkg.version,
        }
        where = f"{pkg.id}/{st.id}"
        et = s["event_type"]
        if et == "metrics" and not ctx.get("otlp"):
            raise RenderError(f"{where}: metrics stream needs an OTLP endpoint on the policy")

        # parsers
        pname = lambda n: f"{pkg.id}.{st.id}.{n}"  # noqa: E731
        for p in s.get("parsers") or []:
            entry = {"name": pname(p["name"]), **{k: v for k, v in p.items() if k not in ("name", "title")}}
            doc["parsers"].append(entry)
        for mp in s.get("multiline_parsers") or []:
            entry = {"name": pname(mp["name"]), **{k: v for k, v in mp.items() if k not in ("name", "title", "rules")}}
            if "rules" in mp:
                entry["rules"] = [{"state": r["state"], "regex": r["regex"], "next_state": r["next_state"]} for r in mp["rules"]]
            doc["multiline_parsers"].append(entry)

        # input
        inp = s["input"]
        pdoc = cat.get("input", inp["plugin"])
        if pdoc is None:
            raise RenderError(f"{where}: input plugin {inp['plugin']!r} not in catalogue")
        node = {"name": inp["plugin"], "tag": tag}
        node.update(resolve_fixed(inp.get("fixed"), refs))
        ivals = field_values(inp.get("fields") or [], (sa or {}).get("input"))
        apply_bindings(inp.get("fields") or [], ivals, node, where + ".input")
        chosen = (sa or {}).get("parser", (s.get("parser_field") or {}).get("default", "none"))
        if chosen and chosen != "none":
            if chosen not in {p["name"] for p in s.get("parsers") or []}:
                raise RenderError(f"{where}: parser {chosen!r} is not offered by the stream")
            node["parser"] = pname(chosen)

        # processors
        chain = []
        glob_filters = []
        procs = s.get("processors") or {}
        defaults = {d["id"]: d for d in procs.get("defaults") or []}
        act_chain = (sa or {}).get("processors")
        if act_chain is None:
            act_chain = [{"id": d["id"]} for d in defaults.values()]
        seen_defaults = set()
        for item in act_chain:
            if "id" in item:
                d = defaults.get(item["id"])
                if d is None:
                    raise RenderError(f"{where}: unknown processor id {item['id']!r}")
                seen_defaults.add(d["id"])
                on = item.get("enabled", d.get("enabled", True))
                if d.get("locked"):
                    on = True
                if not on:
                    continue
                plugin, body = d["plugin"], {}
                body.update(resolve_fixed(d.get("fixed"), refs))
                vals = field_values(d.get("fields") or [], item.get("fields"))
                apply_bindings(d.get("fields") or [], vals, body, f"{where}.processors.{d['id']}")
            else:
                plugin = item["plugin"]
                if plugin not in (procs.get("allow") or []):
                    raise RenderError(f"{where}: plugin {plugin!r} is not allowed on this stream")
                found = cat.chain_plugin(plugin)
                if not found:
                    raise RenderError(f"{where}: plugin {plugin!r} not in catalogue")
                body = copy.deepcopy(item.get("params") or {})
                check_added_params(found[1], body, cat, f"{where}.processors.{plugin}")
            found = cat.chain_plugin(plugin)
            kind, cdoc = found
            if kind == "processor" or cdoc.get("as_processor", False):
                chain.append({"name": plugin, **body})
            else:
                glob_filters.append({"name": plugin, "match": tag, **body})
        # locked defaults the activation left out
        for d in defaults.values():
            if d.get("locked") and d["id"] not in seen_defaults:
                body = resolve_fixed(d.get("fixed"), refs)
                vals = field_values(d.get("fields") or [], None)
                apply_bindings(d.get("fields") or [], vals, body, f"{where}.processors.{d['id']}")
                chain.append({"name": d["plugin"], **body})

        # identity metadata
        meta = {"velox.integration": pkg.id, "velox.stream": st.id, "velox.package_version": pkg.version}
        if et == "metrics":
            chain.append({"name": "labels", "insert": [f"{k.replace('.', '_')} {v}" for k, v in meta.items()]})
        else:
            for k, v in meta.items():
                chain.append({"name": "content_modifier", "action": "insert", "key": k, "value": v})
        node["processors"] = {et: chain}
        doc["pipeline"]["inputs"].append(node)
        doc["pipeline"]["filters"].extend(glob_filters)

        # output
        if et == "metrics":
            o = ctx["otlp"]
            out = {
                "name": "opentelemetry", "match": tag, "host": o["host"], "port": o["port"],
                "metrics_uri": o.get("path") or "/v1/metrics",
                "tls": "on" if o.get("tls", True) else "off",
                "tls.verify": "on" if o.get("tls_verify", True) else "off",
                "http_user": "${VELOX_OTLP_USER}", "http_passwd": "${VELOX_OTLP_PASSWORD}",
            }
        else:
            o = ctx["opensearch"]
            out = {
                "name": "opensearch", "match": tag, "host": o["host"], "port": o["port"],
                "tls": "on" if o.get("tls", True) else "off",
                "tls.verify": "on" if o.get("tls_verify", True) else "off",
                "http_user": "${VELOX_OS_USER}", "http_passwd": "${VELOX_OS_PASSWORD}",
                "index": artifact, "write_operation": "create", "suppress_type_name": "on",
                "trace_error": "on",
            }
            if o.get("path"):
                out["path"] = o["path"]
            if et == "traces":
                out["traces"] = "on"
        doc["pipeline"]["outputs"].append(out)

    for k in ("parsers", "multiline_parsers"):
        if not doc[k]:
            del doc[k]
    if not doc["pipeline"]["filters"]:
        del doc["pipeline"]["filters"]
    if not doc["pipeline"]["inputs"]:
        raise RenderError("no stream enabled")
    return doc


# ---------------------------------------------------------------------------
# Backend objects (guide §8)
# ---------------------------------------------------------------------------

def set_path(obj: dict, dotted: str, value):
    parts = dotted.split(".")
    cur = obj
    for p in parts[:-1]:
        cur = cur.setdefault(p, {})
    cur[parts[-1]] = value


def compile_backend(pkg: L.Package, activation: dict | None) -> dict:
    act_streams = (activation or {}).get("streams") or {}
    objs = {}
    major = L.major_of(pkg.version)
    for st in pkg.streams:
        s = st.doc
        sa = act_streams.get(st.id)
        if not (sa["enabled"] if sa is not None else s.get("enabled", True)):
            continue
        if s["event_type"] == "metrics":
            continue
        N = L.artifact_name(st.id, pkg.id, pkg.version)
        be = s["backend"]
        vals = field_values(be.get("fields") or [], (sa or {}).get("backend"))
        tpl = L.load_json(st.dir / be["index_template"])
        pipe = L.load_json(st.dir / be["ingest_pipeline"]) if be.get("ingest_pipeline") else None
        life = dict(be.get("lifecycle") or {})
        for f in be.get("fields") or []:
            n = f["name"]
            if n not in vals or not visible(f, vals):
                continue
            b, v = f["bind"], vals[n]
            if "template" in b:
                set_path(tpl["template"], b["template"], v)
            elif "lifecycle" in b:
                life[b["lifecycle"]] = v
            elif "pipeline_toggle" in b and pipe and v is False:
                pipe["processors"] = [p for p in pipe["processors"]
                                      if next(iter(p.values())).get("tag") != b["pipeline_toggle"]]
            elif "pipeline_param" in b and pipe:
                tag, param = b["pipeline_param"].split(".", 1)
                for p in pipe["processors"]:
                    body = next(iter(p.values()))
                    if body.get("tag") == tag:
                        set_path(body, param, v)
        objs[f"_component_template/{N}@package"] = {"template": tpl["template"]}
        if be.get("custom_hooks", True):
            objs[f"_component_template/{N}@custom (create if absent)"] = {"template": {}}
            objs[f"_ingest/pipeline/{N}@custom (create if absent)"] = {"processors": []}
        if pipe is not None:
            if be.get("custom_hooks", True):
                pipe["processors"].append({"pipeline": {"name": f"{N}@custom", "ignore_missing_pipeline": True}})
            objs[f"_ingest/pipeline/{N}"] = pipe
        if life:
            actions = []
            roll = {k[len("rollover_"):]: v for k, v in life.items() if k.startswith("rollover_")}
            if roll:
                actions.append({"rollover": {f"min_{k}": v for k, v in roll.items()}})
            states = [{"name": "hot", "actions": actions, "transitions": []}]
            if life.get("delete_after"):
                states[0]["transitions"] = [{"state_name": "delete", "conditions": {"min_index_age": life["delete_after"]}}]
                states.append({"name": "delete", "actions": [{"delete": {}}], "transitions": []})
            objs[f"_plugins/_ism/policies/{N}"] = {"policy": {
                "description": f"{pkg.id}/{st.id} v{major}", "default_state": "hot", "states": states,
                "ism_template": [{"index_patterns": [f".ds-{N}-*"], "priority": 100}],
            }}
        settings = {"index.default_pipeline": N} if pipe is not None else {}
        objs[f"_index_template/{N}"] = {
            "index_patterns": [N], "data_stream": {}, "priority": 200,
            "composed_of": [f"{N}@package"] + ([f"{N}@custom"] if be.get("custom_hooks", True) else []),
            "template": {"settings": settings} if settings else {},
        }
        objs[f"index-pattern/{N}"] = {"title": N, "timeFieldName": "@timestamp"}
    # dashboards
    prefix = f"veloxagent-{pkg.id}-v{major}-"
    stream_N = {s.id: L.artifact_name(s.id, pkg.id, pkg.version) for s in pkg.streams}
    for rel in pkg.manifest.get("dashboards") or []:
        for line in (pkg.dir / rel).read_text().splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            obj["id"] = prefix + obj["id"]
            for r in obj.get("references") or []:
                rid = str(r["id"])
                r["id"] = stream_N[rid[7:]] if rid.startswith("stream:") else prefix + rid
            objs[f"saved_object/{obj['type']}/{obj['id']}"] = obj
    return objs


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("package")
    ap.add_argument("--activation")
    ap.add_argument("--context")
    ap.add_argument("--catalog")
    ap.add_argument("--format", choices=["yaml", "json"], default="yaml")
    ap.add_argument("--backend", action="store_true")
    args = ap.parse_args()

    pkg = L.load_package(pathlib.Path(args.package))
    act = L.load_json(pathlib.Path(args.activation)) if args.activation else None
    ctx = copy.deepcopy(DEFAULT_CONTEXT)
    if args.context:
        ctx.update(L.load_json(pathlib.Path(args.context)))
    cdir = pathlib.Path(args.catalog) if args.catalog else L.latest_catalog_dir()
    if not cdir:
        sys.exit("no catalogue under fluent-bit/")
    cat = L.load_catalog(cdir)
    try:
        doc = compile_backend(pkg, act) if args.backend else compile_policy(pkg, act, ctx, cat)
    except RenderError as e:
        sys.exit(f"render: {e}")
    if args.format == "json":
        print(json.dumps(doc, indent=2, ensure_ascii=False))
    else:
        print(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120), end="")


if __name__ == "__main__":
    main()
