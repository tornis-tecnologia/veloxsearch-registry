#!/usr/bin/env python3
"""Generate packages/index.json from every packages/<id>/<version>/manifest.yaml.

Never edit index.json by hand. CI runs `--check` to refuse a stale index.

Usage: scripts/build_index.py [--check] [--packages DIR] [--out FILE]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import v2lib as L  # noqa: E402


def build(packages_root: pathlib.Path) -> dict:
    by_id: dict[str, dict] = {}
    for vdir in L.iter_package_dirs(packages_root):
        pkg = L.load_package(vdir)
        m = pkg.manifest
        comp = m["compatibility"]
        signals = sorted({s.doc.get("signal") for s in pkg.streams if s.doc})
        event_types = sorted({s.doc.get("event_type") for s in pkg.streams if s.doc})
        entry = by_id.setdefault(pkg.id, {
            "id": pkg.id, "title": m["title"], "summary": m["summary"],
            "categories": m["categories"], "versions": [],
        })
        if m.get("icon"):
            entry["icon"] = f"{pkg.id}/{pkg.version}/{m['icon']}"
        entry["versions"].append({
            "version": pkg.version,
            "release": m["release"],
            "path": f"{pkg.id}/{pkg.version}/",
            "manifest_sha256": L.sha256_file(vdir / "manifest.yaml"),
            "min_mesh_version": comp["min_mesh_version"],
            "min_agent_version": comp["min_agent_version"],
            "min_fluent_bit_version": comp["min_fluent_bit_version"],
            "os": comp["os"],
            "signals": signals,
            "event_types": event_types,
        })
    out = []
    for pid, entry in sorted(by_id.items()):
        entry["versions"].sort(key=lambda v: L.semver_key(v["version"]), reverse=True)
        ga = [v for v in entry["versions"] if v["release"] == "ga"]
        latest = (ga or entry["versions"])[0]
        entry["latest"] = latest["version"]
        # title/summary/icon from the latest version
        lv = L.load_package(packages_root / pid / latest["version"]).manifest
        entry["title"], entry["summary"], entry["categories"] = lv["title"], lv["summary"], lv["categories"]
        if lv.get("icon"):
            entry["icon"] = f"{pid}/{latest['version']}/{lv['icon']}"
        out.append(entry)
    return {"spec_version": "2.0", "generated_at": None, "packages": out}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--packages", default=str(L.PACKAGES))
    ap.add_argument("--out")
    args = ap.parse_args()
    root = pathlib.Path(args.packages)
    out = pathlib.Path(args.out) if args.out else root / "index.json"
    idx = build(root)
    if args.check:
        if not out.is_file():
            sys.exit(f"{out}: missing — run scripts/build_index.py")
        cur = json.loads(out.read_text())
        cur_cmp = {**cur, "generated_at": None}
        if cur_cmp != idx:
            sys.exit(f"{out}: stale — run scripts/build_index.py")
        print(f"{out}: current ({len(idx['packages'])} packages)")
        return
    idx["generated_at"] = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(idx, indent=2, ensure_ascii=False) + "\n")
    print(f"{out}: {len(idx['packages'])} packages, {sum(len(p['versions']) for p in idx['packages'])} versions")


if __name__ == "__main__":
    main()
