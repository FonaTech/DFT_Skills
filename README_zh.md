# DFT Skills

[English](./README.md) | [日本語](./README_ja.md)

面向 Clouds_Coder、Codex、Claude Code、OpenCode 的跨平台 DFT、AIMD、MLIP/MLMD 与 FEM workflow skills。

本仓库提供一个可复用的核心 skill 包 `dft-workflow-orchestrator`，以及配套的 references、case studies、presets 和 scripts。系统会先判断能够回答研究决策的最小尺度；只有确有必要时，才从 DFT 升级到 AIMD、经验证的 MLIP-MD、统计约化与 FEM，而不是默认把每个任务都做成多尺度。

本仓库首先针对同源生态的 [FonaTech/Clouds-Coder](https://github.com/FonaTech/Clouds-Coder) 做专门优化，尤其是面向 Clouds_Coder 的技能发现、按需加载、entrypoint 导航、RAG 优先级和运行边界控制。同时，它也保持对 Codex、Claude Code、OpenCode 的适配性，不做单平台绑定。

## GitHub 快速跳转

- 优先适配的上游运行时仓库：[FonaTech/Clouds-Coder](https://github.com/FonaTech/Clouds-Coder)

## 优化定位

- 首要优化目标：`FonaTech/Clouds-Coder` 生态中的 `Clouds_Coder`
- 一等适配目标：Codex、Claude Code、OpenCode
- 设计原则：以 Clouds 为优先优化对象，同时保持 skill 的跨平台可移植性

## 架构总览

本仓库以一个核心 skill 为中心组织，外围挂接平台无关的 scientific assets，并针对 `Clouds_Coder` 做优先优化。

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

## 关键框架子架构图

### 1. Clouds 优先的发现与按需加载

这一层对应与 [FonaTech/Clouds-Coder](https://github.com/FonaTech/Clouds-Coder) 同源生态的优先适配路径。

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

### 2. 知识收集与理论归因链路

只要当前节点的信息已经足够支持理论判断和实验编排，就会提前停止继续收集。

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

### 3. 跨平台封装与镜像布局

仓库内保持 GitHub 可见的适配目录，再由同步脚本落地到各平台实际使用的隐藏运行时目录。

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

### 4. 执行与后台监控回路

这一层的目标是在后台计算运行时持续拉取状态、识别偏离、并及时回到方法或作业层做修正。

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

### 5. 尺度洞察与研究主线控制

复杂任务启动前可先向用户确认技术路线、目标深度、预期交付物和资源边界。执行过程中由研究主线、claim 验证门、受控分支、数据血缘与唯一优先下一动作持续校正方向。

```mermaid
flowchart LR
    Q[研究决策]
    S{最小充分尺度}
    D[DFT]
    A[AIMD]
    M[MLIP or MLMD]
    F[FEM]
    R[研究主线]
    B[有界分支]
    L[数据与模型血缘]
    V[经验证结论]

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

## 仓库包含内容

- `skills/dft-workflow-orchestrator/` 下的核心 agent skill
- 尺度路由、复杂任务澄清、theory intake、AIMD、MLIP 选型/训练/主动学习、FEM 耦合、不确定性与平台互操作参考资料
- 面向长任务的研究主线控制：claim gates、有界分支、数据/模型血缘、追加式决策日志和下一动作队列
- 大幅扩充的工程案例库，覆盖催化、缺陷、迁移、能带、光学、力学、AIMD、有限温相行为、预训练 MLIP 筛选、主动学习 MLMD、DFT-FEM、DFT-MLIP-FEM 与高通量发现
- 用于结构获取和项目起步的 preset manifests
- 用于跨栈 preflight、多尺度 scaffold、manifest 校验、MLIP 数据审计、ASE 代理推理/松弛、轨迹诊断、研究主线维护、structure intake、VASP job render、queue execution、run monitoring 与 result summary 的辅助脚本

## 支持的平台

- `Clouds_Coder`
- Codex
- Claude Code
- OpenCode

主 skill 文件位于：

- `skills/dft-workflow-orchestrator/SKILL.md`

## 仓库结构

```text
DFT_Skills/
├── README.md
├── README_zh.md
├── README_ja.md
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

## 安装

如果你使用的是本仓库优先优化的平台 `Clouds_Coder`，先看：

- [INSTALL.md](./INSTALL.md)

其他平台安装说明：

- [`claude-plugin/INSTALL.md`](./claude-plugin/INSTALL.md)
- [`codex/INSTALL.md`](./codex/INSTALL.md)
- [`opencode/INSTALL.md`](./opencode/INSTALL.md)

为了方便 GitHub 展示和手动上传，仓库内使用可见目录 `claude-plugin/`、`codex/`、`opencode/`。真正安装到平台时，仍然会落到 `.claude/`、`.opencode/`、`~/.codex/`、`~/.agents/` 等运行时原生路径。

## Clouds_Coder 专门适配点

本仓库让源 `SKILL.md` 保持 Agent Skills 标准格式，并通过 Clouds 专用侧车清单实现 compact loading：

- 标准源 frontmatter 只包含 `name` 与 `description`
- `agents/clouds-coder.json` 保存 aliases、triggers、entrypoints、attachments、preferred tools 与 runtime contract
- `scripts/sync_skill_to_platforms.py --targets clouds --mode copy` 只对生成的 Clouds 副本应用该 overlay
- 资源被拆分为 entrypoints 与 attachments，支持按需读取，而不是一次性粗暴展开
- 兼容性检查会验证标准源、overlay 和生成副本；若本地可导入 `Clouds_Coder`，还会实测 compact mode

可以直接运行兼容性检查：

```bash
python3 DFT_Skills/skills/dft-workflow-orchestrator/scripts/verify_clouds_compat.py
```

## 其他平台适配性

虽然本仓库首先为 Clouds 优化，但并不依赖 Clouds 专属机制才能工作。

- Codex 通过标准 `SKILL.md` 和 `agents/openai.yaml` 适配
- Claude Code 通过可见的 `claude-plugin/` 元数据配合 `.claude/skills/...` 安装路径适配
- OpenCode 通过可见的 `opencode/` 安装辅助目录配合 `.opencode/skills/...` 路径适配
- 核心 scientific workflow、case、preset、script 均保持相对路径和平台中立

## VASP 与第三方边界

本仓库是 workflow / orchestration / packaging 层，不是 VASP 本体，也不重新分发第三方模拟软件。

特别是：

- 不包含 VASP 源码或二进制
- 不包含 `POTCAR` 或 PAW 数据
- 不镜像官方 VASP manual、portal 下载物或官方 wiki 存档
- 不附带预训练 MLIP checkpoint、受限训练数据、专有 FEM 模型或求解器 license 文件
- 脚本只会调用用户本地已合法获取的安装

完整边界说明见：

- [THIRD_PARTY_AND_COPYRIGHT.md](./THIRD_PARTY_AND_COPYRIGHT.md)

## 许可证

仓库原创内容采用：

- [MIT](./LICENSE)

这个 MIT 只覆盖本仓库原创内容，不覆盖第三方软件、网页、数据集、用户上传资料和单独授权的可执行文件。
