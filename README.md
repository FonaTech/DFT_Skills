# DFT Skills

[中文](./README_zh.md) | [日本語](./README_ja.md)

Cross-platform DFT, AIMD, MLIP/MLMD, and FEM workflow skills for Clouds_Coder, Codex, Claude Code, and OpenCode.

This repository packages one reusable skill bundle, `dft-workflow-orchestrator`, plus its references, case studies, presets, and helper scripts. It chooses the smallest sufficient physical scale, turns literature-grounded materials questions into reproducible projects, and can escalate from DFT to AIMD, validated MLIP-driven MD, statistical reduction, and FEM only when the scientific decision requires it.

It is optimized first for the same ecosystem as [FonaTech/Clouds-Coder](https://github.com/FonaTech/Clouds-Coder), especially for Clouds_Coder discovery, compact skill loading, entrypoint-guided reads, and RAG-aware theory grounding. At the same time, the repository is packaged to remain portable across Codex, Claude Code, and OpenCode.

## GitHub Quick Links

- Optimized upstream runtime: [FonaTech/Clouds-Coder](https://github.com/FonaTech/Clouds-Coder)

## Optimization Positioning

- primary optimization target: `Clouds_Coder` in the `FonaTech/Clouds-Coder` ecosystem
- first-class portability targets: Codex, Claude Code, OpenCode
- design principle: Clouds-first optimization without sacrificing cross-platform skill portability

## Architecture Overview

The repository is organized as one Clouds-first skill bundle with platform-neutral scientific assets and runtime-specific mirrors around it.

```mermaid
flowchart TB
    U[User Goal or Literature Claim]
    P[Runtime Probe]
    S[dft-workflow-orchestrator]
    R[References]
    C[Case Studies]
    T[Presets]
    H[Helper Scripts]
    W[Project Workspace]
    J[Rendered Jobs]
    M[Live Monitoring]
    O[Results and Summaries]

    U --> P --> S
    S --> R
    S --> C
    S --> T
    S --> H
    R --> W
    C --> W
    T --> W
    H --> W
    W --> J --> M --> O
```

## Key Framework Sub-Architectures

### 1. Clouds-First Discovery and On-Demand Loading

This is the path optimized for the same ecosystem as [FonaTech/Clouds-Coder](https://github.com/FonaTech/Clouds-Coder).

```mermaid
flowchart LR
    A[Clouds_Coder]
    B[Skill Discovery]
    C[Frontmatter Contract]
    D[Entrypoint Manifest]
    E[Compact Load]
    F[Selective Deep Read]
    G[References or Cases or Presets or Scripts]
    H[Project Outputs]

    A --> B --> C --> D --> E --> F --> G --> H
```

### 2. Knowledge Grounding Cascade

The collection chain stops early if the current tier is already sufficient for theory selection and experiment routing.

```mermaid
flowchart TD
    A[Need More Theory Context]
    B{Runtime}
    C[Uploaded or Local Files]
    D{Enough Information}
    E[Local RAG]
    F[Online Retrieval]
    G[Model Knowledge]
    H[Claim Matrix and Method Routing]

    A --> B
    B -->|Clouds_Coder| C
    B -->|Codex or Claude Code or OpenCode| C
    C --> D
    D -->|Yes| H
    D -->|No on Clouds_Coder| E
    D -->|No on other runtimes| F
    E --> D
    F --> D
    D -->|Still insufficient| G
    G --> H
```

### 3. Cross-Platform Packaging Layout

The repository keeps GitHub-visible adapter directories, while the sync script materializes the actual hidden runtime install targets.

```mermaid
flowchart TB
    A[skills/dft-workflow-orchestrator]
    B[claude-plugin/]
    C[codex/]
    D[opencode/]
    E[agents/openai.yaml]
    F[sync_skill_to_platforms.py]
    G[.claude or ~/.claude targets]
    H[.opencode or ~/.config/opencode targets]
    I[~/.codex or ~/.agents targets]
    J[Shared references cases presets scripts]

    A --> B
    A --> C
    A --> D
    A --> E
    A --> F
    A --> J
    F --> G
    F --> H
    F --> I
    B --> J
    C --> J
    D --> J
```

### 4. Execution and Live Monitoring Loop

The execution side is designed to keep background calculations observable instead of waiting blindly for job completion.

```mermaid
flowchart LR
    A[Preflight]
    B[Knowledge Packet]
    C[Structure Intake]
    D[Method Selection]
    E[Project Scaffold]
    F[Job Rendering]
    G[Queue Launch]
    H[Live Status Polling]
    I[Convergence or Failure Triage]
    J[Summary and Next-Step Routing]

    A --> B --> C --> D --> E --> F --> G --> H --> I --> J
    I -->|needs adjustment| D
    I -->|needs rerun| F
```

### 5. Scale Insight And Research-Spine Control

The workflow does not assume every task is multiscale. Complex work is kept on course through a live objective, claim gates, bounded branches, data lineage, and one prioritized next action.

```mermaid
flowchart LR
    Q[Scientific Decision]
    S{Smallest Sufficient Scale}
    D[DFT]
    A[AIMD]
    M[MLIP or MLMD]
    F[FEM]
    R[Research Spine]
    B[Bounded Branches]
    L[Artifact Lineage]
    V[Validated Verdict]

    Q --> S
    S --> D
    S --> A
    S --> M
    S --> F
    D --> R
    A --> R
    M --> R
    F --> R
    R --> B
    R --> L
    B --> V
    L --> V
```

## What This Repository Contains

- a portable agent skill under `skills/dft-workflow-orchestrator/`
- workflow references for scale routing, complex-task clarification, theory intake, AIMD, MLIP selection/training/active learning, FEM coupling, uncertainty, and platform interop
- research-spine controls for claim gates, bounded branches, data/model lineage, append-only decisions, and prioritized next actions
- expanded engineering case studies covering catalysis, defects, transport, optics, mechanics, AIMD, finite-temperature phase behavior, pretrained MLIP screening, active-learning MLMD, DFT-FEM and DFT-MLIP-FEM coupling, and high-throughput discovery
- preset manifests for structure acquisition and project bootstrapping
- helper scripts for cross-stack preflight, multiscale scaffolding, manifest validation, MLIP dataset auditing, ASE surrogate inference/relaxation, trajectory diagnostics, research-spine maintenance, structure intake, VASP job rendering, queue execution, monitoring, and summarization

## Supported Runtimes

- `Clouds_Coder`
- Codex
- Claude Code
- OpenCode

The primary skill file is:

- `skills/dft-workflow-orchestrator/SKILL.md`

## Repository Layout

```text
DFT_Skills/
├── README.md
├── INSTALL.md
├── LICENSE
├── THIRD_PARTY_AND_COPYRIGHT.md
├── claude-plugin/
├── codex/
├── opencode/
└── skills/
    └── dft-workflow-orchestrator/
        ├── SKILL.md
        ├── agents/
        ├── case-studies/
        ├── presets/
        ├── references/
        └── scripts/
```

## Installation

For the primary optimized runtime, `Clouds_Coder`, start with:

- [INSTALL.md](./INSTALL.md)

Platform-specific install helpers are also provided in:

- [`claude-plugin/INSTALL.md`](./claude-plugin/INSTALL.md)
- [`codex/INSTALL.md`](./codex/INSTALL.md)
- [`opencode/INSTALL.md`](./opencode/INSTALL.md)

The repository keeps these adapter directories visible so they can be uploaded to GitHub without relying on dot-prefixed folders. Actual installs still land in the runtime-native paths such as `.claude/`, `.opencode/`, `~/.codex/`, or `~/.agents/`.

## Clouds_Coder Compatibility

This package keeps the source `SKILL.md` standard and uses a Clouds-only sidecar overlay for compact loading:

- portable source frontmatter contains only `name` and `description`
- `agents/clouds-coder.json` carries aliases, triggers, entrypoints, attachments, preferred tools, and the runtime contract
- `scripts/sync_skill_to_platforms.py --targets clouds --mode copy` applies that overlay only to the generated Clouds target
- entrypoint resources are separated from the full body so the runtime can load them on demand
- the compatibility checker validates standard source packaging and the rendered Clouds copy; it also tests runtime compact mode when `Clouds_Coder` is importable

## Cross-Platform Portability

Even though the repository is optimized first for Clouds, it is not Clouds-only.

- Codex support is carried by standard `SKILL.md` plus `agents/openai.yaml`
- Claude Code support is carried by visible `claude-plugin/` metadata plus installs into `.claude/skills/...` compatible paths
- OpenCode support is carried by visible `opencode/` helpers plus installs into `.opencode/skills/...` compatible paths
- the scientific workflow, cases, presets, and scripts remain platform-neutral and path-relative

You can verify this directly with:

```bash
python3 DFT_Skills/skills/dft-workflow-orchestrator/scripts/verify_clouds_compat.py
```

## VASP And Other Upstream Tools

This repository is an orchestration and documentation layer. It is not a redistribution of VASP or any other third-party simulation package.

In particular:

- no VASP source code or binary is included
- no `POTCAR` or PAW dataset is included
- no official VASP manual mirror, portal dump, or copied wiki archive is included
- no pretrained MLIP checkpoint, restricted training dataset, proprietary FEM model, or solver license file is included
- helper scripts assume the user already has a separately licensed local installation where required

See the full legal and boundary document here:

- [THIRD_PARTY_AND_COPYRIGHT.md](./THIRD_PARTY_AND_COPYRIGHT.md)

## License

The original repository content is released under:

- [MIT](./LICENSE)

That MIT grant applies only to the original content of this repository. Third-party software, websites, datasets, user uploads, and separately licensed executables remain under their own terms.

## Reference Pages Used For VASP-Facing Packaging

These official pages were used as boundary references while packaging the VASP-facing parts of this repository:

- <https://www.vasp.at/>
- <https://www.vasp.at/home/wiki/>
- <https://www.vasp.at/info/faq/public_domain/>
- <https://www.vasp.at/info/faq/purchase_vasp/>
- <https://www.vasp.at/info/faq/vasp_access/>
- <https://www.vasp.at/wiki/index.php/POTCAR>
- <https://www.vasp.at/wiki/index.php/Preparing_a_POTCAR>
- <https://www.vasp.at/wiki/index.php/Nudged_elastic_bands>
- <https://www.vasp.at/wiki/index.php/Optical_properties>
- <https://www.vasp.at/wiki/Berry_phases_and_finite_electric_fields>
- <https://www.vasp.at/wiki/Molecular_dynamics_calculations?redirect=no&title=Molecular_dynamics_calculations>

Those pages remain the property of their respective owners and are linked here as references only.
