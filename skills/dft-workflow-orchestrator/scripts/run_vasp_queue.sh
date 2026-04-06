#!/bin/zsh
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 JOBLIST [NP]"
  exit 2
fi

JOBLIST_INPUT="$1"
NP="${2:-${NP:-8}}"
VASP_BIN="${VASP_BIN:-vasp_std}"
DISPLAY_JOBLIST="$JOBLIST_INPUT"
DISPLAY_VASP_BIN="$VASP_BIN"

if [[ "$DISPLAY_VASP_BIN" == */* ]]; then
  DISPLAY_VASP_BIN="${DISPLAY_VASP_BIN:t}"
fi

if [[ "$JOBLIST_INPUT" = /* ]]; then
  JOBLIST="$JOBLIST_INPUT"
  if [[ "$JOBLIST" == "$(pwd)"/* ]]; then
    DISPLAY_JOBLIST="${JOBLIST#$(pwd)/}"
  else
    DISPLAY_JOBLIST=$(python3 - "$JOBLIST" "$(pwd)" <<'PY'
import os, sys
print(os.path.relpath(sys.argv[1], sys.argv[2]))
PY
)
  fi
else
  JOBLIST="$(pwd)/$JOBLIST_INPUT"
fi

if [[ ! -f "$JOBLIST" ]]; then
  echo "Joblist not found: $DISPLAY_JOBLIST"
  exit 2
fi

PROJECT_ROOT="$(cd "$(dirname "$JOBLIST")/.." && pwd)"
QUEUE_NAME="$(basename "$JOBLIST" .txt)"
LOG_DIR="$PROJECT_ROOT/logs/$QUEUE_NAME"
RUN_ONE_SCRIPT="$(cd "$(dirname "$0")" && pwd)/run_one_vasp_job.sh"

export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
export VECLIB_MAXIMUM_THREADS="${VECLIB_MAXIMUM_THREADS:-1}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-1}"

mkdir -p "$LOG_DIR"
echo "Queue: $QUEUE_NAME" > "$LOG_DIR/queue.log"
echo "Project root: ." >> "$LOG_DIR/queue.log"
echo "NP=$NP VASP_BIN=$DISPLAY_VASP_BIN" >> "$LOG_DIR/queue.log"
echo "Started: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_DIR/queue.log"

while IFS= read -r relpath <&3 || [[ -n "$relpath" ]]; do
  if [[ -z "$relpath" || "$relpath" == \#* ]]; then
    continue
  fi

  if [[ "$relpath" = /* ]]; then
    workdir="$relpath"
    if [[ "$workdir" == "$PROJECT_ROOT"/* ]]; then
      display_relpath="${workdir#$PROJECT_ROOT/}"
    else
      display_relpath=$(python3 - "$workdir" "$PROJECT_ROOT" <<'PY'
import os, sys
print(os.path.relpath(sys.argv[1], sys.argv[2]))
PY
)
    fi
  else
    workdir="$PROJECT_ROOT/$relpath"
    display_relpath="$relpath"
  fi

  if [[ ! -d "$workdir" ]]; then
    echo "SKIP missing job directory $display_relpath" | tee -a "$LOG_DIR/queue.log"
    continue
  fi

  start_ts=$(date '+%Y-%m-%d %H:%M:%S')
  echo "START $start_ts $display_relpath" | tee -a "$LOG_DIR/queue.log"

  rc=0
  (
    cd "$PROJECT_ROOT"
    zsh "$RUN_ONE_SCRIPT" "$display_relpath" "$NP"
  ) >> "$LOG_DIR/queue.log" 2>&1 || rc=$?

  end_ts=$(date '+%Y-%m-%d %H:%M:%S')
  echo "DONE $end_ts rc=$rc $display_relpath" | tee -a "$LOG_DIR/queue.log"
done 3< "$JOBLIST"

echo "Finished: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_DIR/queue.log"
