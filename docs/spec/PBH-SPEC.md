# PBH Protocol Specification (PBH-SPEC)

**Version**: v2.0.0-draft
**Status**: Draft, Pending Finalization
**Release Date**: 2026-05-06
**Highlights**: Defines the standardized project "Collaboration Constitution" and core protocols, marking PBH's evolution from a "tool" to a "universal standard."

## Core Principles

1.  **Protocol as Language**: `AGENTS.md` is the common "language" between AI and the project. This specification ensures the consistency, completeness, and clarity of that language.
2.  **Constraint as a Service**: By seeding deterministic rules and gates, it builds a predictable and verifiable safe collaboration space for non-deterministic AI agents.
3.  **Protocol as Code**: A sufficiently detailed protocol is itself "code" that can be accurately executed, verified, and reproduced.

## 1. Problem Domain Definition

When an AI coding agent enters a new project, it faces three core information gaps:

1.  **Invisible Rules**: Project-specific rules like coding style, test requirements, and commit conventions are not automatically discoverable by the agent on first contact.
2.  **Unverifiable Quality**: After generating code, the agent lacks a unified, automated entry point to determine if the task is "done."
3.  **Imperceptible State**: The agent cannot perceive the project's development phase (early, active, pre-release), and thus cannot adjust its working strategy.

PBH aims to **systematically resolve** these issues upon project initialization. It creates a standardized set of core files, providing AI agents with a **predictable, verifiable, and cross-language reproducible** working environment.

## 2. Core Protocols

### 2.1 `AGENTS.md` Specification

**Purpose**: To provide AI agents with a structured "project operations manual" that can be parsed within 30 seconds.

**Implementation Requirement**: Any PBH v2.0-compatible implementation **MUST** be able to generate or verify an `AGENTS.md` file that fully conforms to the following specifications.

**Format Requirements**:
- **Path**: `AGENTS.md` at the project root directory.
- **Format**: Markdown conforming to the CommonMark standard, with numbered section headings.
- **Quick Variant**: A compatible implementation **MAY** provide a streamlined `AGENTS.quick.md` (**MUST** be ≤ 50 lines). If provided, it **MUST** contain the content of the §2 Quick Start and §5 Critical Rules sections.

**Mandatory Section Definitions**:
This specification clearly distinguishes between "mandatory (MUST)" and "optional (MAY)" sections for implementors to validate against.

| Section | Requirement | Content Requirements |
| :--- | :--- | :--- |
| §1 Project Snapshot | **Mandatory** | Project name, one-line description, project type (**MUST** be one of `cli`/`lib`/`web`/`notebook`), and maintainer. All information **MUST** be rendered by the implementation from user-provided metadata. |
| §2 Quick Start | **Mandatory** | No more than 3 steps for an agent to **verify the environment works and understand the project entry point**. The first step **MUST** always be `make verify`. |
| §5 Critical Rules | **Mandatory** | Non-negotiable hard rules. **MUST** include: self-evaluation ban (only `make verify` output is ground truth), security ban (no hardcoded secrets), and the `make verify` commit gate (never commit failing code). |
| §8 File Mapping | **Mandatory** | Quick-reference table of key directories/fil es. **MUST** include entries for `src/`, `tests/`, `docs/`, `tasks/`, and `.harness/`. |
| §9 Commands | **Mandatory** | Quick-reference table of common dev commands. **MUST** include entries for `make verify`, `make test`, and `make lint`. |

**Optional Section Definitions**:
| Section | Requirement | Content Requirements |
| :--- | :--- | :--- |
| §3 Multi-Agent Notice | Optional | Declare whether the project supports multi-agent collaboration and recommended practices (e.g., using independent git worktrees). |
| §4 Working Guidelines | Optional | Core principles agents should follow. All constraints **MUST** be stated as principles, not numeric limits. Specific numeric limits **SHOULD** be placed in IDE-specific adapter files. |
| §6 / §7 | Reserved | Section numbers reserved for future extensions. Compatible implementations **MUST NOT** use these numbers. |

### 2.2 `make verify` Specification

**Purpose**: To define a unified quality gate entry point for the project.

**Implementation Requirement**: Any compatible tool **MUST** be able to generate or verify a `Makefile` containing a `verify` target.

**Interface Specification**:
- **Command**: `make verify`
- **Expected Behavior**: It **MUST** complete all quality checks required by the project (e.g., code style scanning, test execution, coverage verification) in a **single command**, ensuring the project is in a "deliverable" state.
- **Exit Code Convention**:
  - `0`: All quality checks passed.
  - Non-`0`: At least one check failed. Specific error codes can be custom-defined by each implementation but **MUST** align with the "failure" semantics of CI/CD tools.

### 2.3 `.harness/progress.json` Specification

**Purpose**: To provide a **structured, queryable project phase snapshot** for AI agents and upper-level orchestrators (e.g., Symphony, Multica).

**Implementation Requirement**: Any compatible implementation **MUST** be able to generate or validate a `progress.json` file conforming to the data structure below.

**Schema Definition**:
```json
{
  "project_name": "string",
  "current_stage": "enum['init','plan','execute','evaluate','done']",
  "plans": ["string"],
  "last_updated": "ISO 8601 datetime string"
}
```

| Field | Description |
| :--- | :--- |
| `project_name` | Project name. **MUST** match the name declared in `AGENTS.md`. |
| `current_stage` | Current project phase. **MUST** be one of the enumerated values. See lifecycle definition below. |
| `plans` | List of external specification or plan files adopted by the project (e.g., `tasks/task_plan.md`), providing additional context sources for the Agent. |
| `last_updated` | ISO 8601 datetime string of the last update. **MUST** be precise to the second. |

**Lifecycle Definition**:
| Stage | Meaning | Expected Agent Behavior |
| :--- | :--- | :--- |
| `init` | Project has just completed initialization. | Run `make verify` to ensure a clean environment before starting work. |
| `plan` | Architecture design and task decomposition are in progress. | Only perform planning and analysis; do not modify core code. |
| `execute` | Features are being implemented. | Activate only quality rules (suppress style noise) to improve development efficiency. |
| `evaluate` | Preparing for delivery. | Strictly check all rules and CI-block repeated violations. |
| `done` | The current version is complete; the project is stable. | Only make minimal fixes; do not undertake large changes. |

## 3. Compliance Definition

A project **MAY** declare itself **"PBH v2.0 Compliant"** if and only if it passes the **automated checks** by `harness-init validate` or an equivalent tool:

1.  **File Existence**: The project root **MUST** contain:
    *   An `AGENTS.md` file conforming to the format specification in §2.1.
    *   A `Makefile` containing a `verify` target that conforms to the behavioral specification in §2.2.
    *   A `.harness/progress.json` file conforming to the Schema specification in §2.3.
2.  **Content Compliance**: The content of the above files **MUST** pass the automated checks of any tool implementing the verifier interface defined in §4.1, with a "passed" result.
3.  **Behavioral Compliance**: The project's `make verify` target **MUST** successfully execute and return the correct exit code.

## 4. Ecosystem

### 4.1 Configuration & Runtime

Compatible implementations **MAY** provide support for an optional `WORKFLOW.md` file. This file should serve as a pluggable component within the PBH ecosystem for integrating project rules with automated pipelines or external task trackers (e.g., Linear, GitHub Issues). Its format and implementation create **no direct impact** on the PBH compliance declaration.

### 4.2 Version Control

- **Protocol Version**: The version of this protocol itself (e.g., v2.0.0) is independent of any specific implementation's version. This is the cornerstone of ecosystem stability.
- **Compatibility Mechanism**: `.harness/progress.json` **SHOULD** include a `harness_version` field to record the PBH protocol version used when seeding the project. This is crucial for ensuring that ecosystem tools from different versions can correctly identify and handle the project.

## 5. Reference Implementation

The officially maintained first reference implementation is the `harness-init` in Python. It is developed based on the core terms of this specification (v2.0.0) and serves as the seeding tool of the PBH ecosystem. We encourage the community to contribute implementations in other languages or related tools based on this specification.