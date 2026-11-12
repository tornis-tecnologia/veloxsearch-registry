#!/usr/bin/env python3
"""Regenerate the `files:` inventory of a Spec 2.0 package version.

Every file under the version directory except manifest.yaml is listed with its
sha256, sorted by path. The block between the `files:` line and the next
top-level key is replaced in place, so comments elsewhere in the manifest
survive.

Usage: scripts/inventory.py packages/<id>/<version> [--check]
  --check   exit 1 if the inventory on disk is not what it would be regenerated to
"""
import argparse, hashlib, pathlib, re, sys


def inventory(root: pathlib.Path) -> list[tuple[str, str]]:
    out = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if rel == "manifest.yaml":
            continue
        if any(part.startswith(".") for part in p.relative_to(root).parts):
            sys.exit(f"{root}: hidden file {rel!r} is not allowed in a package")
        out.append((rel, hashlib.sha256(p.read_bytes()).hexdigest()))
    return out


def render(entries) -> str:
    lines = ["files:"]
    lines += [f"  - {{path: {rel}, sha256: {digest}}}" for rel, digest in entries]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("version_dir")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    root = pathlib.Path(args.version_dir)
    manifest = root / "manifest.yaml"
    text = manifest.read_text()
    block = re.compile(r"^files:\n(?:[ \t].*\n|\n)*?(?=^[A-Za-z#]|\Z)", re.M)
    if not block.search(text):
        sys.exit(f"{manifest}: no top-level `files:` block to regenerate")
    new = block.sub(lambda _m: render(inventory(root)) + "\n", text, count=1)
    new = re.sub(r"\n{3,}", "\n\n", new)
    if args.check:
        if new != text:
            sys.exit(f"{manifest}: `files:` inventory is stale — run scripts/inventory.py {root}")
        return
    manifest.write_text(new)
    print(f"{manifest}: {len(inventory(root))} files")


if __name__ == "__main__":
    main()
