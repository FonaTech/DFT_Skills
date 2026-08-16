# Research Mode Router

Choose the smallest validated stack that can answer the user's decision. Do not route by software name alone.

## Contents

1. Decision sequence
2. Design brief for complex requests
3. Scale and observable routing
4. Composite workflow patterns
5. Scope expansion map
6. Budget and evidence tiers
7. Scale-insight checklist
8. Routing anti-patterns

## Decision Sequence

Answer in order:

1. What decision will the result change?
2. What is the primary observable and what constitutes a pass?
3. Which degrees of freedom control that observable: electrons, atoms, microstructure, fields, or several?
4. What length and time scales must be represented?
5. Is equilibrium, kinetics, a rare event, a driven response, or failure behavior required?
6. What reference evidence and controls are available?
7. What accuracy, uncertainty, cost, and turnaround are acceptable?

Use the answers to select a route. If the user names a code that cannot resolve the decisive physics, preserve the requested code as a possible implementation but explain the missing layer.

## Design Brief For Complex Requests

Ask for clarification before locking a costly route when the answer could change the stage DAG, evidence tier, or deliverable. Use this compact prompt shape:

```text
Route: Which route do you prefer or permit (DFT-only, AIMD, MLIP/MLMD, FEM, staged coupling)?
Depth: Is the target a design, smoke test, pilot, production, or decision-grade result?
Goal: What decision and final artifact matter most?
Standards: What accuracy, uncertainty, controls, and independent validation are required?
Resources: Which structures, labels, checkpoints, solvers, licenses, hardware, time, and budget are available?
Boundaries: Which assumptions or substitutions are unacceptable, and what partial result is useful?
```

Do not block a routine, reversible, single-scale task on this questionnaire. For an unanswered complex brief, create a design-tier packet with explicit assumptions and identify the decisions that remain open.

The default answer is allowed to be a single-scale workflow. Explicitly write `required_scales`, `deferred_scales`, and `escalation_trigger` before adding a stage. A downstream scale is justified only when its observable, state, or boundary condition cannot be represented by the upstream scale within the decision tolerance.

## Scale And Observable Routing

| Scientific need | Smallest defensible route | Escalate when | Typical decisive outputs |
|---|---|---|---|
| relaxed geometry or relative electronic energy | static DFT | correlation, excited states, temperature, or size dominates | energy, force, structure |
| adsorption, defects, interfaces, or reaction endpoints | DFT with explicit references | path, solvent, potential, entropy, or disorder matters | formation or adsorption energy, charge, geometry |
| migration or reaction barrier | DFT NEB or constrained path | several mechanisms or rare-event sampling matter | barrier and path |
| band, charge, polarization, optical, or magnetic response | property-specific DFT ladder | quasiparticles, excitons, strong correlation, noncollinearity, or finite temperature matters | spectra, tensors, moments, topology |
| harmonic stability or lattice thermal response | DFT plus phonons | anharmonicity or disorder dominates | force constants, free energy, thermal conductivity |
| short-time finite-temperature atomistic behavior | AIMD | cell or time scale is inaccessible | trajectories, distributions, candidate events |
| equilibrium free energy with a known collective variable | AIMD or MLMD plus enhanced sampling | the collective variable is incomplete | free-energy surface, transition ensemble |
| large-cell or long-time atomistic behavior | validated MLIP-MD | chemistry leaves the training domain | diffusion, phase behavior, fracture, thermal transport |
| rapid screening across many configurations | validated pretrained or fitted MLIP | ranking uncertainty overlaps decisions | energies, forces, relaxed candidates |
| constitutive response or device-scale fields | FEM or multiphysics | material law is not known or scale separation fails | field maps, fluxes, deformation, failure indicator |
| atomistic parameters feeding continuum | sequential DFT/MLIP to FEM | feedback materially changes atomistic state | parameter surfaces and continuum response |
| local atomistics embedded in a continuum | adaptive or concurrent coupling | no supported handshake or energy-consistent interface exists | coupled local and global response |

## Method Boundary Questions

### Use DFT when

- bond making, charge transfer, magnetic or electronic structure, or reference labels are decisive
- the system size and sampling requirements fit the chosen engine
- zero-temperature or limited finite-temperature evidence is sufficient

Do not use static DFT alone for macroscopic lifetime, disordered equilibrium, hydrodynamic transport, or device fields.

### Use AIMD when

- electronic rearrangement during dynamics is important
- picosecond-scale behavior and modest cells can address the question
- AIMD will seed a surrogate, reveal candidate events, or validate local finite-temperature stability

Do not use short trajectories as converged kinetics or thermodynamics.

### Use MLIP or MLMD when

- the target requires atomistic length and time scales beyond AIMD
- a compatible pretrained checkpoint or enough reference labels exists
- the deployment domain can be stated and monitored

Do not substitute MLIP inference for target-domain validation.

### Use FEM when

- geometry, boundary conditions, spatially varying fields, microstructure, or component scale controls the decision
- a defensible constitutive equation and parameters exist
- continuum assumptions are reasonable relative to the characteristic length scale

Do not interpret FEM solver convergence as proof that the constitutive law is correct.

## Composite Workflow Patterns

### DFT to AIMD

Use for finite-temperature stability, liquids, disorder, surface reconstruction, and initial training snapshots.

```text
static convergence -> relaxed references -> AIMD equilibration
-> replicated production -> snapshot refinement or event follow-up
```

### DFT to MLIP to MLMD

Use for diffusion, phase transitions, liquids, fracture, interfaces, and thermal transport at expanded scales.

```text
deployment definition -> seed labels -> grouped split -> baseline model
-> challenge validation -> active learning -> frozen model -> production MD
```

### DFT to FEM

Use when intrinsic tensors, energetics, or reduced kinetic parameters drive a continuum model.

```text
parameter requirement -> atomistic calculation -> constitutive mapping
-> unit and basis verification -> FEM verification -> continuum prediction
```

### DFT to MLIP to FEM

Use when continuum parameters depend on temperature, composition, defects, interfaces, or microstructure that need large atomistic sampling.

```text
DFT labels -> MLIP validation -> state-grid MLMD -> statistical reduction
-> constitutive fit with uncertainty -> FEM -> sensitivity and validation
```

### Experiment-Calibrated Multiscale Chain

Use when first-principles information constrains but does not uniquely determine a continuum closure.

```text
DFT or MLMD prior + experimental calibration -> posterior parameters
-> held-out experimental validation -> FEM prediction
```

Label the empirical calibration explicitly. Do not call the resulting chain purely first-principles.

## Scope Expansion Map

| Research family | Baseline | Common deeper branch | Common cross-scale branch |
|---|---|---|---|
| catalysis | adsorption and barriers | solvent, potential, free energies, microkinetics | reactor FEM or transport-reaction model |
| electrochemistry | defect and interface energetics | constant-potential or explicit-solvent sampling | phase-field or porous-electrode model |
| batteries and ionic conductors | defects and NEB | AIMD or MLMD diffusion and phase behavior | chemo-mechanical FEM |
| semiconductors | defects, bands, dielectric response | hybrid, GW/BSE, nonradiative transitions | drift-diffusion or electrothermal FEM |
| magnetic and quantum materials | magnetic branches and SOC | noncollinear spin, topology, DMFT | micromagnetics or device transport |
| thermal materials | phonons | anharmonic force constants or MLMD Green-Kubo | heat-transfer FEM |
| mechanics and fracture | elastic and cleavage energetics | MLIP dislocations, plasticity, crack-tip sampling | crystal-plasticity or fracture FEM |
| liquids and amorphous matter | AIMD seed | MLIP melt-quench and free-energy sampling | rheology or transport continuum model |
| irradiation and extreme conditions | defects and collision seeds | MLIP cascades or high-pressure sampling | damage-evolution FEM |
| ferroelectrics and piezoelectrics | polarization and response tensors | finite-temperature domain sampling | phase-field or electromechanical FEM |
| polymers and molecular solids | dispersion-aware DFT | MLIP or classical MD ensembles | viscoelastic or diffusion FEM |
| high-throughput discovery | converged reference subset | pretrained MLIP screening plus DFT confirmation | process or device optimization |

## Budget And Evidence Tiers

Use one of these declared tiers:

| Tier | Purpose | Minimum content |
|---|---|---|
| 0: design | no execution available | assumptions, route, inputs, controls, acceptance gates, cost estimate |
| 1: smoke test | verify plumbing | one minimal structure or mesh, dry run, parser and unit checks |
| 2: pilot | de-risk methods | small convergence set, baseline model, one coupling handoff |
| 3: production | answer the claim | converged matrix, controls, replicas or holdouts, uncertainty |
| 4: decision-grade | support consequential use | independent validation, robustness, audit trail, locked artifacts |

Never describe a lower tier using a higher-tier conclusion.

## Scale-Insight Checklist

Use this short test before routing:

| Question | If yes | If no |
|---|---|---|
| Is the decisive observable an electronic, local structural, or ground-state quantity? | DFT-only candidate | inspect finite-temperature and larger-scale needs |
| Does the claim require fluctuations or rearrangements at a reachable atomistic time scale? | AIMD candidate | keep static DFT |
| Does the claim require longer time, larger cells, or many configurations? | MLIP/MLMD candidate after validation | keep AIMD or DFT |
| Does the claim require spatial fields, geometry, or component boundary conditions? | FEM candidate | do not add FEM |
| Does a downstream equation consume a state-dependent upstream quantity? | define a handoff and uncertainty map | stop at the upstream gate |

This checklist is a triage aid, not a substitute for the claim matrix. If two answers are yes, test whether the second stage changes the decision before creating it.

## Required Route Record

Write this into `workflow/research_contract.md`:

- chosen route and rejected alternatives
- primary observable and pass condition
- evidence tier
- stage list and dependencies
- largest scientific and numerical risks
- compute and licensing assumptions
- planned validation and stopping rules

## Routing Anti-Patterns

- selecting MLIP because it is fast before defining the deployment domain
- adding FEM because the project is called multiscale when no continuum observable is needed
- adding AIMD as decoration to a question already answered by static DFT
- deriving rates from barriers without thermodynamics, prefactors, or a kinetic model
- treating a single temperature, composition, or strain as a universal constitutive property
- using random frame splits that leak adjacent MD snapshots across train and test
- continuing downstream after an upstream gate fails
- interpreting software availability as evidence that another scale is scientifically required
