# High-Throughput Multifidelity Materials Screening

## Engineering Intent

Use this case to screen many materials, structures, compositions, surfaces, or defects with a controlled fidelity ladder: cheap descriptors or MLIP first, targeted DFT next, and optional downstream validation. Optimize decision quality and provenance, not calculation count.

## Questions This Workflow Must Answer

- What property or Pareto decision defines success?
- Which cheap proxy preserves ranking near the decision boundary?
- How will uncertainty and diversity allocate expensive DFT calculations?
- Which candidates, negatives, and outliers receive confirmation?
- How will failed calculations and selection bias be represented?

## Minimum Inputs

- candidate universe, stable identifiers, structures, provenance, and license
- target observables, constraints, thresholds, and multiobjective rule
- fidelity levels with cost and expected error
- baseline model and validation subset
- compute budget, scheduler, retry policy, and stopping rule
- immutable external or high-fidelity test set when available

## Recommended Funnel

```text
schema and deduplication -> physical sanity filters -> cheap baseline
-> pretrained MLIP or low-fidelity calculation -> uncertainty and diversity selection
-> converged DFT confirmation -> method-sensitive refinement
-> experimental or device-scale validation -> final Pareto set
```

## Selection Strategy

- preserve families, compositions, phases, and rare motifs during sampling
- quantify recall of known positives and false negatives near thresholds
- combine expected improvement or uncertainty with structural diversity
- include negative and failed examples in the ledger
- recompute a random audit subset, not only apparent winners
- calibrate surrogate ranking separately for each materially different domain

## DFT Production Controls

- standardized but material-aware convergence policy
- consistent pseudopotential, functional, charge, spin, and reference conventions
- explicit retry tree for electronic, ionic, symmetry, and cell failures
- method escalation only for candidates whose decision depends on it
- workflow-level duplicate detection and content hashes

## Analysis

- coverage of the original candidate universe
- pass rate and failure reasons at every funnel stage
- surrogate rank correlation and top-k recall
- uncertainty calibration and enrichment over random selection
- sensitivity of the Pareto frontier to thresholds and method choices
- cost per confirmed candidate and marginal information gained

## Frequent Failure Modes

- screening with inconsistent structures or reference energies
- discarding failed jobs and biasing the apparent success rate
- choosing only high-scoring similar candidates and losing diversity
- tuning thresholds on the final test candidates
- allowing a fast surrogate to define truth without DFT confirmation
- reporting database scale instead of decision reliability

## Deliverables

- versioned candidate and exclusion manifests
- fidelity ladder, scheduler plan, and retry policy
- surrogate and DFT validation reports
- complete funnel ledger with failures and costs
- confirmed candidates and robust Pareto frontier
- reproducible shortlist with method and validity limitations
