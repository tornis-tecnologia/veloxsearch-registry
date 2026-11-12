"""Shared helpers for the Spec 2.0 tooling (validate_v2, build_index, render).

Pure functions over the on-disk layout; no network. Keep in step with
docs/spec/README.md.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
from dataclasses import dataclass, field

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas"
PACKAGES = ROOT / "packages"
CATALOG = ROOT / "fluent-bit"

CONTEXT_REFS = {"stream_tag", "artifact", "state_dir", "integration", "stream", "package_version"}
REF_RE = re.compile(r"\{([^{}]*)\}")
ENV_RE = re.compile(r"\$\{")
CONTROL_RE = re.compile(r"[\x00-\x1f]")
KIND_DIR = {
    "input": "inputs", "filter": "filters", "processor": "processors",
    "parser_format": "parsers", "multiline_parser": "multiline",
}
PLACEHOLDER_SIG_PREFIX = "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8"


def semver_key(v: str):
    core = v.split("+", 1)[0]
    main, _, pre = core.partition("-")
    nums = tuple(int(x) for x in main.split("."))
    # a pre-release sorts before the release it precedes
    return nums + ((0, pre) if pre else (1, ""))


def major_of(v: str) -> int:
    return int(v.split(".", 1)[0])


def artifact_name(stream_id: str, package_id: str, version: str) -> str:
    return f"veloxagent-{stream_id}.{package_id}-v{major_of(version)}"


def stream_tag(package_id: str, stream_id: str) -> str:
    return f"velox.{package_id}.{stream_id}"


def load_yaml(p: pathlib.Path):
    return yaml.safe_load(p.read_text())


def load_json(p: pathlib.Path):
    return json.loads(p.read_text())


def sha256_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Catalogue
# ---------------------------------------------------------------------------

@dataclass
class Catalog:
    version: str
    plugins: dict[str, dict[str, dict]] = field(default_factory=dict)  # kind -> name -> doc

    def get(self, kind: str, name: str) -> dict | None:
        return self.plugins.get(kind, {}).get(name)

    def chain_plugin(self, name: str) -> tuple[str, dict] | None:
        """A plugin usable in a processor chain: a processor, or a filter."""
        for kind in ("processor", "filter"):
            doc = self.get(kind, name)
            if doc:
                return kind, doc
        return None

    def params(self, doc: dict) -> dict[str, dict]:
        return {p["key"]: p for p in doc.get("params") or []}


def load_catalog(version_dir: pathlib.Path) -> Catalog:
    cat = Catalog(version=version_dir.name)
    for kind, sub in KIND_DIR.items():
        d = version_dir / sub
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.yaml")):
            doc = load_yaml(f)
            if isinstance(doc, dict) and doc.get("kind") == kind:
                cat.plugins.setdefault(kind, {})[doc["name"]] = doc
    return cat


def latest_catalog_dir() -> pathlib.Path | None:
    dirs = [d for d in CATALOG.iterdir() if d.is_dir()] if CATALOG.is_dir() else []
    if not dirs:
        return None
    return max(dirs, key=lambda d: semver_key(d.name + ".0" if d.name.count(".") == 1 else d.name))


# ---------------------------------------------------------------------------
# Packages
# ---------------------------------------------------------------------------

@dataclass
class Stream:
    id: str
    dir: pathlib.Path
    doc: dict


@dataclass
class Package:
    id: str
    version: str
    dir: pathlib.Path
    manifest: dict
    streams: list[Stream]

    def stream(self, sid: str) -> Stream | None:
        return next((s for s in self.streams if s.id == sid), None)


def load_package(version_dir: pathlib.Path) -> Package:
    manifest = load_yaml(version_dir / "manifest.yaml")
    streams = []
    for sid in manifest.get("streams") or []:
        sdir = version_dir / "streams" / str(sid)
        sfile = sdir / "stream.yaml"
        streams.append(Stream(id=str(sid), dir=sdir, doc=load_yaml(sfile) if sfile.is_file() else {}))
    return Package(
        id=str(manifest.get("id")), version=str(manifest.get("version")),
        dir=version_dir, manifest=manifest, streams=streams,
    )


def iter_package_dirs(packages_root: pathlib.Path):
    if not packages_root.is_dir():
        return
    for pkg in sorted(packages_root.iterdir()):
        if not pkg.is_dir() or pkg.name.startswith(("_", ".")):
            continue
        for ver in sorted(pkg.iterdir(), key=lambda p: p.name):
            if ver.is_dir() and (ver / "manifest.yaml").is_file():
                yield ver


def inventory(root: pathlib.Path) -> list[tuple[str, str]]:
    out = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            rel = p.relative_to(root).as_posix()
            if rel != "manifest.yaml":
                out.append((rel, sha256_file(p)))
    return out


# ---------------------------------------------------------------------------
# Field scopes (input / each processor / backend) — shared by validator + renderer
# ---------------------------------------------------------------------------

def field_scopes(stream_doc: dict):
    """Yield (scope_label, plugin_name_or_None, fields_list, fixed_dict)."""
    inp = stream_doc.get("input") or {}
    yield "input", inp.get("plugin"), inp.get("fields") or [], inp.get("fixed") or {}
    for item in (stream_doc.get("processors") or {}).get("defaults") or []:
        yield f"processors.{item.get('id')}", item.get("plugin"), item.get("fields") or [], item.get("fixed") or {}
    be = stream_doc.get("backend") or {}
    yield "backend", None, be.get("fields") or [], {}


def resolve_refs(value: str, ctx: dict[str, str]) -> str:
    def sub(m):
        name = m.group(1)
        if name not in ctx:
            raise KeyError(name)
        return ctx[name]
    return REF_RE.sub(sub, value)
