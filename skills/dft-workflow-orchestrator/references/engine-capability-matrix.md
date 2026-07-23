# Engine And Ecosystem Capability Matrix

Select software after selecting the physical model. Confirm behavior against the installed version's official documentation before generating version-sensitive inputs.

## Contents

1. Electronic-structure engines
2. Atomistic dynamics and sampling
3. MLIP ecosystems
4. FEM and multiphysics engines
5. Interoperability rules
6. Environment audit

## Electronic-Structure Engines

| Engine family | Typical strengths | Watch carefully |
|---|---|---|
| VASP | plane-wave periodic DFT, broad materials workflows, AIMD | license, POTCAR provenance, version-specific tags |
| Quantum ESPRESSO | open plane-wave ecosystem, phonons, perturbation theory | pseudopotential family consistency, executable layout |
| CP2K | mixed Gaussian/plane-wave methods, large systems, liquids, AIMD | basis and auxiliary cutoff convergence, SCF strategy |
| GPAW | Python/ASE integration, grids and plane waves, rapid workflow composition | mode-dependent convergence and parallel setup |
| ABINIT | plane-wave DFT and response properties | dataset syntax and pseudopotential compatibility |
| CASTEP | periodic DFT and materials properties | license and pseudopotential provenance |
| SIESTA or OpenMX | localized orbitals and larger systems | basis-set superposition and basis convergence |
| all-electron codes | high-accuracy reference and spectroscopy | computational cost and method-specific conventions |

Do not translate cutoff values, smearing widths, k-point densities, stress signs, or pseudopotential labels by string substitution. Translate physical accuracy targets and reconverge.

## Atomistic Dynamics And Sampling

| Tool family | Use | Boundary |
|---|---|---|
| engine-native AIMD | electronic-structure forces during dynamics | limited length and time scales |
| ASE dynamics | calculator-neutral orchestration and prototypes | validate thermostat, units, checkpointing, and parallel behavior |
| LAMMPS | scalable classical or MLIP-driven MD | pair style and units depend on model plugin |
| i-PI | path-integral and advanced driver/client sampling | force-provider latency and socket robustness |
| PLUMED | enhanced sampling and collective variables | collective-variable completeness and reweighting |
| phonopy/phono3py | harmonic and anharmonic lattice dynamics | displacement convergence and force consistency |

## MLIP Ecosystems

Model names evolve quickly. Treat this table as a family router, not an API contract.

| Family | Typical use | Required checks |
|---|---|---|
| equivariant graph networks such as MACE, NequIP, Allegro, SevenNet | accurate energies, forces, stresses and scalable MD | element coverage, cutoff, precision, backend, checkpoint license |
| materials graph potentials such as CHGNet and MatGL/M3GNet | pretrained crystalline-material screening and fine-tuning | chemistry and phase coverage, charge or magnetic assumptions, target-domain benchmarks |
| DeePMD models | large-scale production MD with trained deep potentials | descriptor settings, model compression, LAMMPS plugin compatibility |
| GAP/QUIP | kernel-based potentials with explicit sparse environments | descriptor and sparse-point coverage, uncertainty interpretation |
| ACE and related polynomial models | efficient systematic fits and interpretable basis control | basis truncation, regularization, extrapolation |
| foundation atomistic models | broad pretrained inference and transfer learning | exact checkpoint, license, training-domain disclosure, downstream calibration |
| delta-learning models | correction from a lower-fidelity baseline | baseline consistency and error cancellation outside training data |

Never claim that a family is universally more accurate. Benchmark the installed checkpoint on the target state space.

## FEM And Multiphysics Engines

| Engine | Typical strengths | Watch carefully |
|---|---|---|
| COMSOL Multiphysics | integrated GUI, many coupled physics modules | license, version-specific model API, hidden defaults |
| FEniCSx | programmable weak forms and research-grade PDE development | element spaces, stabilization, nonlinear and parallel configuration |
| MOOSE | multiphysics, phase field, solid mechanics, scalable coupling | application modules, material-property interfaces, execution environment |
| Abaqus | structural, thermal, contact, and industrial workflows | license, user subroutines, material convention |
| CalculiX | open finite-element structural and thermal workflows | feature coverage and input-deck conventions |
| deal.II or MFEM | custom high-performance finite-element solvers | substantial implementation and verification burden |
| OpenFOAM | finite-volume flow, transport, and reacting systems | not a generic FEM replacement; coupling and discretization differ |

Generate a solver-neutral specification first: strong form, weak form where relevant, fields, coefficients, domains, boundary and initial conditions, coupling terms, outputs, and verification cases.

## Interoperability Rules

- Use ASE `Atoms` or another structured atomistic format for in-memory exchange; use `extxyz` with explicit properties for portable datasets.
- Record energy, force, stress, virial, cell, periodicity, charge, spin, source calculation, and units on every labeled configuration.
- Do not rely on XYZ alone for periodic cells, stresses, or provenance.
- Preserve trajectory and parent-structure group identifiers across data splits.
- Record tensor ordering explicitly. Voigt order is not universal across codes.
- Record whether stress is tensile-positive or compressive-positive and whether virial is extensive.
- Store continuum parameter tables in a machine-readable CSV or JSON alongside equations and basis metadata.
- Pin package and checkpoint versions in the project environment; keep weights outside version control unless licensing and size policies permit.

## Environment Audit

The preflight script reports availability, not scientific readiness:

```bash
python3 scripts/preflight_multiscale_env.py --workspace . --pretty
```

For each selected engine, also record:

- executable or import path and version
- license status
- MPI, GPU, compiler, and plugin compatibility
- pseudopotential, basis, force-field, or checkpoint location
- model checksum and download source
- calculator or coupling interface
- scheduler and resource constraints
- a minimal smoke-test result

## Selection Rule

Choose the engine that satisfies all three:

1. it represents the required physics at the target scale
2. the local implementation can be verified and executed reproducibly
3. its outputs can meet the next stage's data contract without ambiguous conversion

If no engine satisfies all three, stop at a solver-neutral design or split the work into a validated pilot.
