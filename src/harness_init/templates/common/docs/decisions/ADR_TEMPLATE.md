# docs/decisions/ADR_TEMPLATE.md - {project_name}

> **Purpose**: Architecture Decision Records (ADR) for {project_name}.
> Every significant design decision MUST be documented here.
>
> **Change Control Matrix Reference**:
> | Error Type | Rollback Level | Mechanical Guard |
> |------------|----------------|------------------|
> | Design error | Update architecture decision | No code without ADR in `docs/decisions/` |

---

## Template

Use this template for new ADRs. Name the file `NNNN-title.md` where `NNNN` is a zero-padded number.

```markdown
# ADR-NNNN: [Short Title]

## Status

- Proposed
- Accepted
- Deprecated
- Superseded by [ADR-NNNN](NNNN-title.md)

## Context

What is the issue that we're seeing that is motivating this decision or change?

## Decision

What is the change that we're proposing or have agreed to implement?

## Consequences

What becomes easier or more difficult to do because of this change?

### Positive
- Consequence 1
- Consequence 2

### Negative
- Consequence 1
- Consequence 2
```

---

## Example ADR

### ADR-0001: Use Typer as CLI Framework

**Status**: Accepted

**Context**:
{project_name} needs a CLI entry point. We evaluated `argparse`, `click`, and `typer`.
- `argparse`: No type hints, verbose boilerplate.
- `click`: Good, but requires manual type annotations.
- `typer`: Built on `click`, native type hints, auto-generated help.

**Decision**:
Use `typer` as the CLI framework. It aligns with the project's Python 3.11+ type-hinting philosophy and reduces boilerplate.

**Consequences**:
- **Positive**: Less boilerplate, better IDE support, modern developer experience.
- **Negative**: Extra dependency; developers must learn `typer` conventions.

---

## Guidelines

1. **One decision per ADR**. Do not bundle multiple decisions.
2. **Status must be explicit**. Start as `Proposed`, update to `Accepted` after review.
3. **Superseded ADRs stay**. Do not delete deprecated ADRs; mark them and link to the replacement.
4. **Keep it short**. An ADR should be readable in under 5 minutes.
5. **No code without ADR**. If a design change affects architecture, document it here before writing code.
