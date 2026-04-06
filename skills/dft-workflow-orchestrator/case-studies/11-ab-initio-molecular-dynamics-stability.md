# Ab Initio Molecular Dynamics Stability

## Engineering Intent

Use this case when the key uncertainty is finite-temperature stability, short-time disorder, or rapid structural rearrangement that static relaxations cannot capture. This workflow is about extracting defensible short-time dynamical evidence, not pretending that a short AIMD trajectory is the same thing as full thermodynamic certainty.

Do not use this case by itself to make long-time kinetics or macroscopic lifetime claims.

## Questions This Workflow Must Answer

- Does the structure remain qualitatively intact over the accessible AIMD timescale?
- Which bonds, motifs, or adsorbates fluctuate, survive, or reconstruct under the chosen temperature window?
- Are the observed events consistent across more than one initial condition or reference state?
- Is AIMD only a diagnostic tool here, or does it reveal a mechanism that should be followed by static refinement?

## Theory And Modeling Boundary

- AIMD at the DFT level can reveal short-time bond fluctuations, local rearrangements, and obvious instability that static calculations miss.
- Short trajectories do not provide equilibrium thermodynamics, rare-event rates, or complete diffusion statistics.
- Thermostat choice, time step, supercell size, and trajectory length materially influence what can be claimed.
- If the system is too large or the dynamics too slow, this case may need a handoff to MLFF or classical MD after DFT-level validation.

## Minimum Inputs Before Launch

- the target temperature range and whether the user needs a qualitative stability screen or a comparative trend
- the structural motifs whose survival actually matters
- ensemble choice, thermostat policy, time step, and acceptable trajectory length
- whether multiple initial states or seeds are needed
- whether the system contains mobile species, soft modes, or adsorbates likely to reconstruct

## Structure Strategy

- begin from a fully relaxed static structure that is already defensible
- use a supercell large enough to permit the relevant local fluctuation or disorder motif
- if comparison is the point, keep the same cell and thermostat policy across the candidates
- pre-equilibrate carefully rather than shocking the system into an unphysical state
- store snapshots systematically so that any observed event can be post-processed or statically refined later

## Recommended Job Ladder

1. static bulk, slab, or interface reference relaxation
2. optional short pre-equilibration stage at a lower temperature or softened thermostat setting
3. production AIMD trajectory with documented ensemble and runtime settings
4. post-processing of temperature, total energy, bond metrics, and structural drift
5. optional quench and static refinement of representative snapshots or rearranged states

## Primary Outputs And Decisions

- trajectory-level stability verdict under the modeled timescale and temperature
- time traces for energy, temperature, key bond lengths, coordination counts, or diffusion proxies
- identification of any irreversible reconstruction, desorption, disordering, or phase drift
- recommendation on whether the observed event warrants follow-up with NEB, defect, or phonon workflows
- boundary statement on what timescale and ensemble the result actually covers

## Controls And Sensitivity Axes

- compare at least one reference or alternate initial condition when the claim is comparative
- keep time step, thermostat, and ensemble fixed across comparable branches
- test whether the observed event depends on a small or artificial supercell
- if the system is metallic or strongly anharmonic, verify the electronic settings remain stable throughout the run
- inspect whether equilibration artifacts are being mistaken for real chemistry

## Analysis Checklist

- verify the temperature profile and total energy drift are consistent with the chosen ensemble
- track the specific structural metrics tied to the user claim instead of relying on visual impressions alone
- distinguish reversible thermal fluctuation from irreversible structural failure
- if a new state appears, relax it statically before assigning a mechanism
- state clearly that the trajectory is a finite-time observation, not a complete phase diagram

## Frequent Failure Modes

- treating a few picoseconds as proof of long-term stability
- using an unstable or unconverged static starting structure
- reporting one noisy trajectory without a comparative reference
- ignoring supercell constraints that suppress the relevant fluctuation
- skipping post-processing and relying only on informal trajectory visualization

## Escalate Or Pair With

- pair with `16-phonon-and-thermal-transport.md` when harmonic instability or vibrational behavior also matters
- pair with `09-ionic-migration-and-neb.md` if AIMD suggests a specific hopping event that needs a barrier
- pair with `13-lammps-coupling-and-mlff-handoff.md` when longer-time or larger-cell sampling is needed
- pair with `12-plasma-surface-reaction-proxy.md` if radical-driven surface events appear during the trajectory

## Deliverables

- documented AIMD setup with ensemble, time step, and runtime
- trajectory diagnostics tied to the user's decisive observables
- representative snapshot packet for any significant rearranged states
- explicit limit statement on timescale and interpretability
