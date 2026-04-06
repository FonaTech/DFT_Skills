# Live Run Monitoring

Use this reference when calculations are already running and the front-end agent must keep pulling status, interpreting progress, and deciding whether the workflow is still aligned with plan.

## Core Signals

This workflow combines the same signal classes used in `VASP_Project_ML`:

1. `.status` and `.heartbeat` for launcher-level state
2. `logs/<queue>/queue.log` for queue order and active job identity
3. `OSZICAR` for ionic step, free energy, and recent `dE`
4. `OUTCAR` for force blocks, electronic loop timing, and convergence markers
5. `vasp.out` for runtime warnings that may require intervention

Do not rely on only one file.

## Background Launch Pattern

If you need the front-end to remain free while jobs run, launch the queue in the background from the project root:

```bash
nohup zsh scripts/run_vasp_queue.sh joblists/bootstrap.txt 8 > logs/bootstrap/launcher.out 2>&1 &
```

Then monitor continuously:

```bash
python3 scripts/monitor_vasp_runs.py \
  --project-root . \
  --interval-seconds 120 \
  --iterations 0 \
  --pretty
```

This refreshes:

- `analysis/live_status.csv`
- `analysis/live_status.json`
- `analysis/queue_status.json`
- `analysis/live_monitor_report.md`

## Front-End Monitoring Loop

On each monitoring cycle:

1. Read `analysis/live_monitor_report.md`.
2. Re-open `workflow/experiment_matrix.csv`.
3. Check whether converged jobs now unlock the next control, reference, static, DOS, optics, or barrier tasks.
4. If a run is stale, failed, or warning-heavy, stop queue expansion until the method issue is understood.
5. Update `analysis/claim_verdicts.md` only when a converged job can actually support a planned observable.

## State Meanings

| State | Meaning | Immediate action |
|---|---|---|
| `queued` | job is planned or listed but not yet active | keep next-stage routing ready |
| `running` | runtime files are updating normally | continue polling and compare with pass conditions |
| `running-stale` | marked running but runtime files have not changed recently | inspect process health and runtime tail |
| `finished-converged` | finished and convergence evidence exists | promote `CONTCAR` into the next dependent task |
| `finished-unverified` | exit code is clean but convergence evidence is not explicit | inspect `OUTCAR` before trusting the result |
| `finished-error` | VASP ended with non-zero return code | inspect warnings and restart only after fixing the cause |
| `queue-missing-target` | queue lists a directory that does not exist | repair the queue before launch |

## Intervention Rules

- If `BRMIX`, `ZBRENT`, `Sub-Space-Matrix`, `ZHEGV`, or similar warnings appear, inspect the job before scaling out.
- If a relax job is stale, check whether it is a real stall, a dead process, or just a long electronic step.
- If a correlated or magnetic bootstrap job converges but only covers one branch, one magnetic order, or one `U`, do not treat that as the final physics packet.
- If a control run is missing, do not let attractive primary results outrun the reference design.

## Correlated-System Reminder

For nickelates, rare-earth oxides, or similarly sensitive materials:

- one converged relax is a checkpoint, not a conclusion
- keep structure branch, magnetic order, and `U` sensitivity visible
- do not write the final verdict until the control axis planned in `workflow/experiment_matrix.csv` is actually covered
