# Known Pitfalls - {project_name}

> This file tracks recurring issues, anti-patterns, and gotchas specific to this project.
> Update it as you discover new pitfalls during development.

## Getting Started

When you encounter a problem that costs you >15 minutes to debug, add it here with:
- **Symptom**: What went wrong
- **Root Cause**: Why it happened
- **Fix**: How to resolve it
- **Prevention**: How to avoid it next time

## Template Pitfalls

Replace this section with actual pitfalls as you discover them.

Example format:

### Import cycles in src/{package_name}

- **Symptom**: `ImportError: cannot import name 'X'`
- **Root Cause**: Circular imports between modules
- **Fix**: Move shared types to a separate `types.py` module
- **Prevention**: Use dependency injection; avoid importing at module level
