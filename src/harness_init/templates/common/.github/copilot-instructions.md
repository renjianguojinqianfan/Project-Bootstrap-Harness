# Copilot Instructions for {project_name}

This project uses the Harness Engineering protocol. Key guidelines:

1. Read `.harness/progress.json` before starting work
2. Run `make verify` — baseline must be clean
3. State your plan before modifying code
4. One session = one atomic task
5. Verify against acceptance criteria before finishing
6. Function ≤ 30 lines, file ≤ 200 lines
7. Never commit code that fails `make verify`
