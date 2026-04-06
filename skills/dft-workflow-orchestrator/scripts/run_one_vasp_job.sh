#!/bin/zsh
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 JOB_DIR [NP]"
  exit 2
fi

JOB_DIR_INPUT="$1"
NP="${2:-${NP:-8}}"
VASP_BIN="${VASP_BIN:-vasp_std}"
CLEAN="${CLEAN:-1}"
HEARTBEAT_SECONDS="${HEARTBEAT_SECONDS:-60}"
DISPLAY_JOB_DIR="$JOB_DIR_INPUT"
DISPLAY_VASP_BIN="$VASP_BIN"

if [[ "$DISPLAY_VASP_BIN" == */* ]]; then
  DISPLAY_VASP_BIN="${DISPLAY_VASP_BIN:t}"
fi

if [[ "$JOB_DIR_INPUT" = /* ]]; then
  WORKDIR="$JOB_DIR_INPUT"
  if [[ "$WORKDIR" == "$(pwd)"/* ]]; then
    DISPLAY_JOB_DIR="${WORKDIR#$(pwd)/}"
  else
    DISPLAY_JOB_DIR=$(python3 - "$WORKDIR" "$(pwd)" <<'PY'
import os, sys
print(os.path.relpath(sys.argv[1], sys.argv[2]))
PY
)
  fi
else
  WORKDIR="$(pwd)/$JOB_DIR_INPUT"
fi

export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
export VECLIB_MAXIMUM_THREADS="${VECLIB_MAXIMUM_THREADS:-1}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-1}"

if [[ ! -d "$WORKDIR" ]]; then
  echo "Job directory not found: $DISPLAY_JOB_DIR"
  exit 2
fi

for req in INCAR KPOINTS POSCAR POTCAR; do
  if [[ ! -f "$WORKDIR/$req" ]]; then
    echo "Missing $req in $DISPLAY_JOB_DIR"
    exit 2
  fi
done

if [[ "$CLEAN" == "1" ]]; then
  rm -f \
    "$WORKDIR/.status" \
    "$WORKDIR/.heartbeat" \
    "$WORKDIR/CHG" \
    "$WORKDIR/CHGCAR" \
    "$WORKDIR/CONTCAR" \
    "$WORKDIR/DOSCAR" \
    "$WORKDIR/EIGENVAL" \
    "$WORKDIR/IBZKPT" \
    "$WORKDIR/OSZICAR" \
    "$WORKDIR/OUTCAR" \
    "$WORKDIR/PCDAT" \
    "$WORKDIR/REPORT" \
    "$WORKDIR/WAVECAR" \
    "$WORKDIR/XDATCAR" \
    "$WORKDIR/vasp.out" \
    "$WORKDIR/vasprun.xml"
fi

echo "RUNNING $(date '+%Y-%m-%d %H:%M:%S')" > "$WORKDIR/.status"
echo "RUNNING $(date '+%Y-%m-%d %H:%M:%S')" > "$WORKDIR/.heartbeat"
echo "============================================================"
echo "Job directory: $DISPLAY_JOB_DIR"
echo "MPI ranks: $NP"
echo "OMP threads: $OMP_NUM_THREADS"
echo "VASP binary: $DISPLAY_VASP_BIN"
echo "Clean start: $CLEAN"
echo "Start time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

cd "$WORKDIR"

heartbeat_loop() {
  while true; do
    echo "RUNNING $(date '+%Y-%m-%d %H:%M:%S')" > "$WORKDIR/.heartbeat"
    sleep "$HEARTBEAT_SECONDS"
  done
}

heartbeat_loop &
HEARTBEAT_PID=$!

cleanup_heartbeat() {
  kill "$HEARTBEAT_PID" >/dev/null 2>&1 || true
  wait "$HEARTBEAT_PID" >/dev/null 2>&1 || true
}

trap cleanup_heartbeat EXIT

set +e
mpirun -np "$NP" "$VASP_BIN" 2>&1 | tee vasp.out
rc=${pipestatus[1]}
set -e

cleanup_heartbeat
trap - EXIT
echo "DONE rc=$rc $(date '+%Y-%m-%d %H:%M:%S')" > "$WORKDIR/.status"
echo "DONE rc=$rc $(date '+%Y-%m-%d %H:%M:%S')" > "$WORKDIR/.heartbeat"
echo "============================================================"
echo "Finished: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Exit code: $rc"
echo "Status file: $DISPLAY_JOB_DIR/.status"
echo "Main log: $DISPLAY_JOB_DIR/vasp.out"
echo "============================================================"

exit "$rc"
