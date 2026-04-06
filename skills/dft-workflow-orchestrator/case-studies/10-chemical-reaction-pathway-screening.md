# Chemical Reaction Pathway Screening

## Engineering Intent

Use this case when the question is not only where a molecule binds, but which elementary-step sequence is chemically plausible and energetically competitive. The workflow turns a mechanistic claim into a structured ladder of intermediates and barriers instead of a loose collection of endpoints.

Do not use this case to claim a full catalytic cycle, rate law, or reactor-scale selectivity unless the screened steps are later embedded into a more complete kinetic framework.

## Questions This Workflow Must Answer

- Which intermediates and elementary steps must be included so the proposed route is chemically closed?
- Which branch of the mechanism is likely favored under the chosen approximation?
- Are the decisive differences driven by endpoint thermodynamics, barriers, or both?
- Which steps deserve high-cost refinement and which can be rejected early?

## Theory And Modeling Boundary

- DFT can screen intermediates, transition-state proxies, and relative barrier ladders for explicitly modeled steps.
- A partial pathway is not a full mechanism unless the missing competing branches are shown to be irrelevant or explicitly left open.
- Surface chemistry, electrochemistry, plasma chemistry, and homogeneous molecular reaction steps require different reference conventions. State which one is in play.
- Even a well-screened barrier ladder does not replace microkinetics or finite-temperature ensemble effects.

## Minimum Inputs Before Launch

- a clear reaction network hypothesis with reactants, products, and plausible intermediates
- the environment model: gas phase, surface, electrochemical, or plasma proxy
- whether the decision target is route ranking, bottleneck step, or qualitative mechanistic support
- stoichiometric bookkeeping and reference states for each branch
- whether spin crossing, charged intermediates, or solvent participation are likely to matter

## Structure Strategy

- define the intermediate set before job launch so branches can be compared on equal footing
- keep each step tied to a concrete structure pair or path instead of abstract names only
- if the route is surface mediated, maintain one clean slab reference and one coverage convention per branch
- if multiple spin or charge states are plausible, treat them as separate mechanistic branches
- preserve the structural provenance between screening endpoints and higher-cost barrier jobs

## Recommended Job Ladder

1. reference-state relaxations for the host, surface, and free reactants or products
2. endpoint relaxations for each key intermediate along each branch
3. thermodynamic ranking to eliminate obviously noncompetitive branches
4. targeted NEB or transition-state searches for the decisive steps only
5. static refinement and electronic-structure interpretation for the bottleneck steps
6. optional free-energy assembly, if the environment model justifies it

## Primary Outputs And Decisions

- pathway table with intermediate energies, key barriers, and branch labels
- identification of the likely bottleneck step under the stated approximation
- structural and electronic interpretation of the decisive transformations
- recommendation on which branches are worth refinement and which can be dropped
- explicit statement of whether the current result is a route-screening outcome or a stronger mechanistic claim

## Controls And Sensitivity Axes

- compare at least one competing branch when the mechanism is not unique
- keep reference states and stoichiometric balancing explicit for every step
- test whether the decisive ranking survives changes in spin, coverage, solvent proxy, or correlation treatment
- separate low-cost endpoint screening from high-cost barrier refinement in the workflow packet
- if one step is obviously dominant, refine that one before spending resources on every branch equally

## Analysis Checklist

- verify the pathway is chemically closed and does not hide missing species
- distinguish endpoint stabilization from true barrier lowering
- map each branch onto a clear set of structures and job folders
- highlight which steps are directly computed and which remain inferred
- state whether the remaining uncertainty is kinetic, environmental, or structural

## Frequent Failure Modes

- assembling a mechanism from unrelated single-point calculations
- comparing branches with inconsistent reference species or unit cells
- treating one barrier as proof of the whole cycle
- ignoring spin, charge, or solvent-state changes across the pathway
- launching too many expensive barrier jobs before thermodynamic screening narrows the field

## Escalate Or Pair With

- pair with `01-catalytic-adsorption-and-dissociation.md` when the first uncertainty is still adsorption or dissociation endpoints
- pair with `02-electrocatalysis-and-surface-potential.md` when electrochemical free energies define the branch ranking
- pair with `12-plasma-surface-reaction-proxy.md` if radicals and non-equilibrium feed species dominate the pathway
- pair with `14-comsol-coupling-and-property-handoff.md` only after the screened pathway has been reduced to a defensible coarse-grained model

## Deliverables

- branch-resolved reaction packet with intermediates and references
- screened pathway energy and barrier table
- bottleneck-step note with explicit caveats
- recommendation on what must be refined before making a strong mechanism claim
