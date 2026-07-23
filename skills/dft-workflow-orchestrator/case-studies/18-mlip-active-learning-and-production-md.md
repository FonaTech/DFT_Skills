# MLIP Active Learning And Production Molecular Dynamics

## Engineering Intent

Use this case when a pretrained or seed potential is not sufficient and the project needs iterative DFT labeling, a frozen validated model, and larger or longer production molecular dynamics.

Read `references/mlip-workflows.md`, `references/aimd-workflows.md`, and `references/multiscale-validation.md`.

## Questions This Workflow Must Answer

- What exact state space will production MD visit?
- Which configurations seed the model and which remain immutable tests?
- How will extrapolation or uncertainty trigger new labels?
- Which downstream observables, rather than only fitting errors, define readiness?
- When does active learning stop?

## Minimum Inputs

- deployment-domain statement covering chemistry, structures, state variables, and tasks
- consistent DFT labeling protocol for energies, forces, and stresses
- seed configurations spanning equilibrium and controlled off-equilibrium states
- grouped validation, immutable test, and hard challenge definitions
- model family, baseline, training resources, label budget, and stop criteria
- production MD protocol with abort and DFT spot-check rules

## Recommended Experiment Ladder

1. assemble and audit seed labels with stable parent and trajectory groups
2. train a simple baseline and the first candidate or committee
3. evaluate grouped validation and hard challenges
4. explore deployment state points with short guarded trajectories
5. cluster high-risk candidates and remove integration artifacts
6. label a diverse acquisition batch with consistent DFT
7. retrain from a documented checkpoint policy and revalidate
8. repeat until acquisition and decision metrics meet stop criteria
9. freeze checkpoint and run immutable tests once
10. conduct replicated production MD with online domain monitoring

## Required Challenge Families

- strained and compressed cells
- elevated-temperature distorted configurations
- relevant phases and composition boundaries
- defects, surfaces, interfaces, or reactions in deployment
- close-contact and high-force configurations near integration failures
- transition or rare-event neighborhoods when kinetics matters

## Production Observables

Select only those needed by the claim:

- phase stability and order parameters
- diffusion, conductivity, viscosity, or reaction populations
- structural distribution functions and spectra
- phonons, heat capacity, or Green-Kubo transport
- stress-strain, defect motion, dislocations, or fracture indicators
- state-dependent data for a later FEM handoff

## Controls And Sensitivity

- compare model seeds, architectures, or committee members when model form matters
- vary timestep, cell size, replica, thermostat or barostat, and state-grid density
- perform DFT spot checks on ordinary, uncertain, and extreme frames
- keep the immutable test and challenge sets outside active-learning acquisition
- test whether the final scientific verdict changes across acceptable model variants

## Frequent Failure Modes

- consuming the test set during active learning
- random frame splitting of correlated trajectories
- labeling every uncertain frame without diversity selection
- optimizing force RMSE while failing the target transport or phase observable
- running production through obvious extrapolation
- using one model and one trajectory as the uncertainty estimate

## Deliverables

- versioned dataset manifest and split hashes
- active-learning ledger with acquisition reason and label cost
- training configuration, learning curves, and baseline comparison
- frozen model card and checksum
- final in-domain, immutable-test, and challenge results
- production MD protocol, trajectories, uncertainty, and stop events
- deployment-domain and prohibited-use statement
