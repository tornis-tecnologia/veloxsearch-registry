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

fail=0
for d in "${dirs[@]}"; do
  id=$(basename "$(dirname "$d")"); ver=$(basename "$d")
  cases=("defaults")
  for a in tests/activations/"$id"/*.json; do [ -f "$a" ] && cases+=("$a"); done
  for c in "${cases[@]}"; do
    name="$id-$ver-$(basename "${c%.json}")"
    if [ "$c" = defaults ]; then
      python3 -I scripts/render.py "$d" --context "$OUT/context.json" >"$OUT/$name.yaml" || { echo "::error::$name: render failed"; fail=1; continue; }
    else
      python3 -I scripts/render.py "$d" --context "$OUT/context.json" --activation "$c" >"$OUT/$name.yaml" || { echo "::error::$name: render failed"; fail=1; continue; }
    fi
    for v in $FB_VERSIONS; do
      if docker run --rm -e VELOX_OS_USER=u -e VELOX_OS_PASSWORD=p -e VELOX_OTLP_USER=u -e VELOX_OTLP_PASSWORD=p \
          -v "$OUT:/cfg:ro" "fluent/fluent-bit:$v" /fluent-bit/bin/fluent-bit -c "/cfg/$name.yaml" --dry-run >"$OUT/$name.$v.log" 2>&1 \
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
