#!/usr/bin/env python3
"""R24: every stream's ingest pipeline reproduces its expected documents.

For each packages/<id>/<version>/streams/<stream>/test/<case>.log the
pipeline (as the core would install it: the package's processors; the
@custom hook is dropped) is run through OpenSearch `_ingest/pipeline/_simulate`
with one document per line `{"log": <line>, "@timestamp": "<fixed>"}`, and
the result is compared with <case>.expected.json (a list of documents, one
per line of the .log; keys absent from the expected document are ignored, so
an expectation can be partial; `null` means the field must be absent).

A stream whose backend has no `ingest_pipeline` or no test/ directory is
reported as "no test" (a warning, not a failure) so coverage is visible.

Usage: OPENSEARCH_URL=https://admin:pw@localhost:9200 scripts/pipeline_test.py [package dirs...]
       --update   rewrite the .expected.json files from the simulate output
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import ssl
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import v2lib as L  # noqa: E402

FIXED_TS = "2026-01-01T00:00:00.000Z"


def simulate(url: str, pipeline: dict, docs: list[dict]) -> list[dict]:
    body = json.dumps({"pipeline": pipeline, "docs": [{"_index": "t", "_id": str(i), "_source": d} for i, d in enumerate(docs)]}).encode()
    req = urllib.request.Request(url.rstrip("/") + "/_ingest/pipeline/_simulate", data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx, timeout=60) as r:
        res = json.load(r)
    out = []
    for d in res["docs"]:
        if "error" in d:
            out.append({"__error__": d["error"]})
        else:
            out.append(d["doc"]["_source"])
    return out


def subset(expected, actual, path="") -> list[str]:
    diffs = []
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return [f"{path or '$'}: expected object, got {type(actual).__name__}"]
        for k, v in expected.items():
            p = f"{path}.{k}" if path else k
            if v is None:
                if k in actual:
                    diffs.append(f"{p}: expected absent, got {actual[k]!r}")
            elif k not in actual:
                diffs.append(f"{p}: missing")
            else:
                diffs += subset(v, actual[k], p)
    elif expected != actual:
        diffs.append(f"{path}: expected {expected!r}, got {actual!r}")
    return diffs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--update", action="store_true")
    args = ap.parse_args()
    url = os.environ.get("OPENSEARCH_URL")
    if not url:
        sys.exit("set OPENSEARCH_URL (e.g. https://admin:pw@localhost:9200)")
    # credentials in the URL -> basic auth header via an opener
    if "@" in url.split("//", 1)[1]:
        cred, host = url.split("//", 1)[1].rsplit("@", 1)
        scheme = url.split("//", 1)[0]
        url = f"{scheme}//{host}"
        import base64
        auth = base64.b64encode(cred.encode()).decode()
        opener = urllib.request.build_opener()
        opener.addheaders = [("Authorization", f"Basic {auth}")]
        urllib.request.install_opener(opener)

    dirs = [pathlib.Path(p) for p in args.paths] or list(L.iter_package_dirs(L.PACKAGES))
    failures, untested, passed = [], [], 0
    for vdir in dirs:
        pkg = L.load_package(vdir)
        for st in pkg.streams:
            be = (st.doc.get("backend") or {})
            label = f"{pkg.id}/{pkg.version}/{st.id}"
            if not be.get("ingest_pipeline"):
                continue
            cases = sorted((st.dir / "test").glob("*.log")) if (st.dir / "test").is_dir() else []
            if not cases:
                untested.append(label)
                continue
            pipeline = L.load_json(st.dir / be["ingest_pipeline"])
            for case in cases:
                lines = [ln for ln in case.read_text().splitlines() if ln.strip()]
                docs = [{"log": ln, "@timestamp": FIXED_TS} for ln in lines]
                got = simulate(url, pipeline, docs)
                exp_file = case.with_suffix(".expected.json")
                if args.update:
                    exp_file.write_text(json.dumps(got, indent=2, ensure_ascii=False) + "\n")
                    print(f"updated {exp_file.relative_to(L.ROOT)}")
                    continue
                if not exp_file.is_file():
                    failures.append(f"{label}/{case.name}: no expected file (run with --update to create)")
                    continue
                expected = L.load_json(exp_file)
                if len(expected) != len(got):
                    failures.append(f"{label}/{case.name}: {len(expected)} expected docs vs {len(got)} lines")
                    continue
                for i, (e, g) in enumerate(zip(expected, got)):
                    if "__error__" in g and "__error__" not in e:
                        failures.append(f"{label}/{case.name}#{i}: pipeline error: {g['__error__'].get('reason')}")
                        continue
                    for d in subset(e, g):
                        failures.append(f"{label}/{case.name}#{i}: {d}")
                passed += 1
    for u in untested:
        print(f"::warning::{u}: pipeline has no test/ cases (R24)")
    if failures:
        print(f"{len(failures)} problem(s):", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        sys.exit(1)
    print(f"pipeline tests: {passed} case(s) passed, {len(untested)} stream(s) untested")


if __name__ == "__main__":
    main()
