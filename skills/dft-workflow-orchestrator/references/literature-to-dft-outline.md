# Literature To DFT Outline

Convert a paper or user request into a DFT work packet with explicit boundaries.

## Step 1: Capture the Paper's Actual Claims

List:

- material system
- experimental observable
- stated mechanism
- controls or counterexamples
- whether the claim is causal, comparative, or descriptive

Do not paraphrase away uncertainty. Keep the paper's own scope visible.

## Step 2: Separate What DFT Can Test

Classify each claim as one of:

- directly DFT-testable
- indirectly supportable by DFT
- out of scope for static DFT

Examples:

- "H insertion stabilizes a new local electronic state" is DFT-testable.
- "PtO2 ablates better in PLD" is only indirectly supportable through optical or energetic proxies.
- "The full finite-temperature MIT pathway is reproduced" is not a plain DFT claim.

## Step 3: Build the Claim Matrix

For each DFT-testable or DFT-supportable claim, write:

- `claim_id`
- `claim_text`
- `evidence_type`
- `model_system`
- `observable`
- `control`
- `method_limit`

Also write:

- `workflow/knowledge_sources.md`
- `workflow/theory_packet.md`

These two files explain where the theoretical understanding came from and why the chosen model ladder is appropriate.

## Step 4: Choose the Minimum Calculation Packet

Use the router reference to avoid overbuilding.

Examples:

- bulk energetic comparison
- adsorption comparison
- insertion-energy scan
- DOS or PDOS comparison
- optics proxy
- interface transfer barrier

## Step 5: Write the Guardrails

Document what you are not claiming.

For every final packet include at least:

- "What the calculation can say"
- "What the calculation cannot say"
- "What extra calculations would be needed for stronger evidence"

## Expected Files

The literature-intake phase should produce:

- `workflow/request_summary.md`
- `workflow/knowledge_sources.md`
- `workflow/theory_packet.md`
- `workflow/claim_matrix.md`
- `workflow/experiment_matrix.csv`
- `workflow/method_guardrails.md`
