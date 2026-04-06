#!/bin/zsh
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Usage: $0 SRC_JOB_DIR DST_JOB_DIR [bj|zero]"
  exit 2
fi

SRC_INPUT="$1"
DST_INPUT="$2"
MODE="${3:-bj}"
DISPLAY_SRC="$SRC_INPUT"
DISPLAY_DST="$DST_INPUT"

if [[ "$SRC_INPUT" = /* ]]; then
  SRC="$SRC_INPUT"
  if [[ "$SRC" == "$(pwd)"/* ]]; then
    DISPLAY_SRC="${SRC#$(pwd)/}"
  else
    DISPLAY_SRC=$(python3 - "$SRC" "$(pwd)" <<'PY'
import os, sys
print(os.path.relpath(sys.argv[1], sys.argv[2]))
PY
)
  fi
else
  SRC="$(pwd)/$SRC_INPUT"
fi

if [[ "$DST_INPUT" = /* ]]; then
  DST="$DST_INPUT"
  if [[ "$DST" == "$(pwd)"/* ]]; then
    DISPLAY_DST="${DST#$(pwd)/}"
  else
    DISPLAY_DST=$(python3 - "$DST" "$(pwd)" <<'PY'
import os, sys
print(os.path.relpath(sys.argv[1], sys.argv[2]))
PY
)
  fi
else
  DST="$(pwd)/$DST_INPUT"
fi

if [[ ! -d "$SRC" ]]; then
  echo "Source job directory not found: $DISPLAY_SRC"
  exit 2
fi

mkdir -p "$DST"
cp "$SRC/POSCAR" "$DST/POSCAR"
cp "$SRC/POTCAR" "$DST/POTCAR"
cp "$SRC/KPOINTS" "$DST/KPOINTS"
cp "$SRC/INCAR" "$DST/INCAR"

python3 - "$DST/INCAR" "$MODE" <<'PY'
from pathlib import Path
import sys

incar_path = Path(sys.argv[1])
mode = sys.argv[2]
lines = incar_path.read_text().splitlines()
lines = [line for line in lines if not line.strip().startswith("IVDW")]
if mode == "bj":
    lines.append("IVDW = 12")
elif mode == "zero":
    lines.append("IVDW = 11")
else:
    raise SystemExit(f"Unsupported D3 mode: {mode}")
incar_path.write_text("\n".join(lines) + "\n")
PY

echo "Created D3-enabled job:"
echo "  src: $DISPLAY_SRC"
echo "  dst: $DISPLAY_DST"
echo "  mode: $MODE"
