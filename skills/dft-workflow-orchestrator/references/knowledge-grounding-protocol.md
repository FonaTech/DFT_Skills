# Knowledge Grounding Protocol

Use this protocol before choosing a method or generating jobs.

## Goal

Force the workflow to understand the theory well enough that the experiment matrix is defensible.

## Source Priority By Platform

### On Clouds_Coder.py

Use the strongest grounding path:

1. inspect uploaded files and local workspace sources first: PDFs, notes, CIF metadata, prior project files, and existing workflow packets
2. if the above is not sufficient, query local RAG with material, mechanism, observable, and theory-model prompts
3. query again with multilingual variants if the corpus is mixed and the first RAG pass is thin
4. if the local sources plus RAG coverage are still incomplete, use online literature search or database lookup
5. only then use model prior knowledge to bridge gaps, and label those sections as inferred

Early-stop rule:

- if a current tier already provides enough evidence to select the working model, write the claim matrix, and define controls, stop there
- move to the next tier only when a real ambiguity remains

Recommended query decomposition:

- material system: `correlated oxide hydrogen insertion`
- theory model: `charge transfer bond disproportionation transition metal oxide`
- observable: `hydrogen insertion energy DOS transition metal oxide`
- method check: `DFT+U optical response limitations correlated oxide`

### On Other Platforms

When no native RAG exists:

1. inspect uploaded files first
2. inspect local workspace literature, structure files, and prior workflow packets
3. if the local evidence is still incomplete, use web or shell retrieval if available
4. fall back to model knowledge only after the above are exhausted

Early-stop rule:

- if uploaded and local materials already determine the theory basis and experiment design, do not continue to web retrieval
- use model knowledge only for residual gaps, not as a replacement for readable sources

Never pretend model-memory-only synthesis is equivalent to a grounded literature pass.

## Theory Escalation Checklist

Before committing to a calculation, confirm:

- what mechanism the paper is claiming
- whether the target observable is structural, electronic, optical, thermodynamic, or kinetic
- whether plain DFT, DFT+U, hybrid, NEB, phonons, AIMD, GW, or DMFT is the right level
- what DFT can test directly
- what DFT can only support indirectly

## Required Output Files

Write these into the project packet:

- `workflow/knowledge_sources.md`
- `workflow/theory_packet.md`

## Minimum Contents For `workflow/knowledge_sources.md`

For each source, log:

- source type: uploaded | local | RAG | web | model prior
- citation or path
- why it matters
- confidence
- whether it supports direct evidence, model selection, or only background context

## Minimum Contents For `workflow/theory_packet.md`

Document:

- candidate theoretical pictures
- chosen working model
- rejected alternatives and why
- method ladder: baseline and escalation path
- observable-to-theory map
- unresolved theoretical risks

## Failure Modes

- jumping straight from a paper abstract to a VASP job
- using one retrieved paper as the whole theory basis
- choosing `+U` or hybrid without saying which physical ambiguity it resolves
- calling a kinetic or finite-temperature mechanism "proven" by static zero-K calculations
