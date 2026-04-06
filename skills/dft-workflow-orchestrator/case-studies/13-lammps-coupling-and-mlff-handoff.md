# LAMMPS Coupling And MLFF Handoff

## Engineering Intent

Use this case when DFT is the upstream truth source for a later LAMMPS, classical MD, or machine-learned force-field workflow. The point is to define a training and validation packet with clear coverage of the downstream chemistry and structural space, not to fit a narrow DFT dataset and hope it extrapolates safely.

Do not use this case if the downstream workflow has not yet defined what environments, temperatures, defects, or interfaces it must cover.

## Questions This Workflow Must Answer

- What chemistry and configuration space will the downstream force field actually encounter?
- Which DFT observables must be reproduced: energies, forces, stresses, elastic response, defect energetics, or migration barriers?
- Is the planned dataset wide enough to support the intended LAMMPS regime without obvious extrapolation?
- What validation packet will decide whether the handoff is acceptable?

## Theory And Modeling Boundary

- DFT provides the reference labels and physically trustworthy local configurations used for fitting or validating the downstream model.
- A force field or MLFF trained on DFT does not inherit universal validity. Its safe domain is defined by the dataset and validation coverage.
- Fitting quality on a narrow training set is not evidence of transferability to surfaces, defects, liquids, or reaction chemistry unless those were included.
- If the downstream model must capture reactive or electronically driven events beyond the training manifold, record that risk explicitly.

## Minimum Inputs Before Launch

- the intended downstream regime: bulk thermodynamics, diffusion, fracture proxy, interfaces, liquids, surfaces, or reactions
- the set of observables that must remain accurate after handoff
- chemistry space, oxidation-state diversity, and structural motifs that the model must see
- acceptable error metrics and the validation tests that matter operationally
- whether active learning, AIMD snapshots, or targeted perturbations will be part of the data generation plan

## Structure Strategy

- begin from converged DFT reference structures covering the expected local environments
- include distortions, strain states, thermal snapshots, and off-equilibrium structures if downstream dynamics will sample them
- if interfaces or defects matter, include them in the training packet instead of hoping bulk data will transfer
- maintain exact provenance from each DFT job to each fitting datum
- reserve a held-out validation slice that is chemically meaningful rather than randomly trivial

## Recommended Job Ladder

1. define the downstream state space and the required observable set
2. generate pristine reference structures and controlled distortions
3. add chemically relevant defect, interface, adsorption, or thermal snapshots
4. collect DFT energies, forces, and stresses with one consistent methodology
5. partition the dataset into training, validation, and hard challenge subsets
6. fit the downstream model and validate it against the challenge subset
7. if necessary, iterate via targeted active-learning expansion rather than blind dataset growth

## Primary Outputs And Decisions

- a labeled DFT training packet with full provenance
- a held-out validation packet tied to the downstream use case
- error summary for energies, forces, stresses, and any special observables
- a safe-domain statement that says where the model can and cannot be trusted
- recommendation on whether more DFT coverage or a narrower deployment target is required

## Controls And Sensitivity Axes

- ensure the validation set includes the difficult environments, not only more of the same bulk states
- keep the DFT methodology fixed across all labels unless an explicit multi-level strategy is documented
- include off-equilibrium structures if the downstream MD will sample them
- test transferability separately for bulk, surfaces, defects, and interfaces if all are in scope
- if the model is reactive, check whether bond-breaking and bond-forming configurations are actually represented

## Analysis Checklist

- confirm the dataset spans the temperatures, strains, and chemistries relevant to the downstream problem
- quantify errors on held-out structures that matter operationally
- keep training-set performance separate from real validation performance
- identify the failure envelope, not just the best-fit metrics
- state clearly whether the model is ready for production or only for controlled exploratory use

## Frequent Failure Modes

- fitting to a narrow low-temperature bulk dataset and deploying to surfaces or defect diffusion
- reporting training loss as though it were validation evidence
- forgetting stress labels when the downstream workflow needs equation-of-state or elastic fidelity
- mixing DFT labels from inconsistent settings into one fitting pool
- omitting provenance, which makes later failure diagnosis almost impossible

## Escalate Or Pair With

- pair with `11-ab-initio-molecular-dynamics-stability.md` when AIMD snapshots are the natural training source
- pair with `09-ionic-migration-and-neb.md` if migration barriers must be preserved by the handoff model
- pair with `07-heterointerface-band-alignment-and-charge-transfer.md` or `08-defect-chemistry-and-trap-states.md` if those environments dominate the deployment regime
- pair with `16-phonon-and-thermal-transport.md` when vibrational fidelity matters for the later model usage

## Deliverables

- DFT data-generation plan tied to downstream deployment
- training, validation, and challenge-set manifest
- quantitative validation summary and safe-domain note
- explicit statement of what the handoff model still cannot be trusted to simulate
