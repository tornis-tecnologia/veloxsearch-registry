#!/usr/bin/env bash
# Render every package version with its defaults (and with every activation
# fixture under tests/activations/<id>/*.json) and run `fluent-bit --dry-run`
# on the result, in Docker, for each Fluent Bit version listed in FB_VERSIONS.
#
# Usage: scripts/dryrun.sh [packages/<id>/<version> ...]
#   FB_VERSIONS="3.2 latest" scripts/dryrun.sh
set -euo pipefail
cd "$(dirname "$0")/.."

FB_VERSIONS="${FB_VERSIONS:-3.2 latest}"
OUT="${DRYRUN_OUT:-$(mktemp -d)}"
mkdir -p "$OUT"

# A policy context with an OTLP endpoint, so metrics streams render too.
cat >"$OUT/context.json" <<'EOF'
{"opensearch": {"host": "os.example.internal", "port": 9200, "tls": true, "tls_verify": true},
 "otlp": {"host": "otlp.example.internal", "port": 4318, "tls": true, "tls_verify": true, "path": "/v1/metrics"}}
EOF

if [ $# -gt 0 ]; then
  dirs=("$@")
else
  mapfile -t dirs < <(find packages -mindepth 2 -maxdepth 2 -type d -name '[0-9]*' | sort)
fi
[ ${#dirs[@]} -gt 0 ] || { echo "no packages"; exit 0; }

# A tag like 3.2 is compared as 3.2.0; `latest` is treated as newer than everything.
fb_full() { case "$1" in latest) echo 999.0.0;; *) case "$1" in *.*.*) echo "$1";; *) echo "$1.0";; esac;; esac; }
ver_ge() { [ "$(printf '%s\n%s\n' "$2" "$1" | sort -V | head -1)" = "$2" ]; }

fail=0
for d in "${dirs[@]}"; do
  id=$(basename "$(dirname "$d")"); ver=$(basename "$d")
  if grep -qE "^$id[[:space:]]" tests/dryrun-skip.txt 2>/dev/null; then
    echo "skip $id-$ver  ($(grep -E "^$id[[:space:]]" tests/dryrun-skip.txt | sed -E "s/^$id[[:space:]]+//"))"; continue
  fi
  minfb=$(python3 -c "import yaml,sys; print(yaml.safe_load(open('$d/manifest.yaml'))['compatibility']['min_fluent_bit_version'])")
  if ! python3 -c "import yaml,sys; sys.exit(0 if 'linux' in yaml.safe_load(open('$d/manifest.yaml'))['compatibility']['os'] else 1)"; then
    echo "skip $id-$ver  (not a Linux package; the official image cannot load its plugins)"; continue
  fi
  cases=("defaults")
  for a in tests/activations/"$id"/*.json; do [ -f "$a" ] && cases+=("$a"); done
  for v in $FB_VERSIONS; do
    vf=$(fb_full "$v")
    if ! ver_ge "$vf" "$minfb"; then echo "skip $id-$ver  fluent-bit:$v < min $minfb"; continue; fi
    # the compiler omits fields whose `since` is newer than the agent's Fluent Bit
    python3 -c "import json; c=json.load(open('$OUT/context.json')); c['fluent_bit_version']='$vf'; json.dump(c, open('$OUT/context.$v.json','w'))"
    for c in "${cases[@]}"; do
      name="$id-$ver-$(basename "${c%.json}")"
      act=(); [ "$c" = defaults ] || act=(--activation "$c")
      if ! python3 -I scripts/render.py "$d" --context "$OUT/context.$v.json" "${act[@]}" >"$OUT/$name.$v.yaml" 2>"$OUT/$name.$v.render.err"; then
        if grep -q "no stream enabled" "$OUT/$name.$v.render.err"; then echo "skip $name  (no stream enabled by default)"; continue; fi
        echo "::error::$name: render failed"; cat "$OUT/$name.$v.render.err"; fail=1; continue
      fi
      if docker run --rm -e VELOX_OS_USER=u -e VELOX_OS_PASSWORD=p -e VELOX_OTLP_USER=u -e VELOX_OTLP_PASSWORD=p \
          -v "$OUT:/cfg:ro" "fluent/fluent-bit:$v" /fluent-bit/bin/fluent-bit -c "/cfg/$name.$v.yaml" --dry-run >"$OUT/$name.$v.log" 2>&1 \
         && grep -q "configuration test is successful" "$OUT/$name.$v.log"; then
        echo "ok   $name  fluent-bit:$v"
      else
        echo "::error::$name on fluent-bit:$v"; grep -iE 'error|invalid|unknown' "$OUT/$name.$v.log" | head -5; fail=1
      fi
    done
  done
done
echo "rendered configs in $OUT"
exit $fail
