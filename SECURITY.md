# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.2.x   | ✅        |
| 0.1.x   | ❌        |

## Reporting a Vulnerability

We take security seriously. If you discover a vulnerability in **PBH (Project Bootstrap Harness)**:

**Preferred method** (keeps details private):
- Use [GitHub Private Vulnerability Reporting](https://github.com/renjianguojinqianfan/Project-Bootstrap-Harness/security/advisories)
- Click "Report a vulnerability" button

**Alternative method**:
- Email: 18108097611@163.com

**Please include**:
- Description of the vulnerability
- Steps to reproduce (if applicable)
- Affected version(s)
- Potential impact (e.g., template injection, CLI command execution)

## Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 5 business days
- **Fix release**: Based on severity (Critical: 7 days, High: 30 days)

## Security Scope

This policy covers:
- CLI argument parsing and execution logic
- Project template generation (file system operations)
- Dependency resolution in generated projects
- Configuration file handling

**Not in scope**: 
- Security of tools installed by generated projects (user responsibility)
- Issues in user-modified templates

## Security Features

PBH implements the following safeguards:
- CodeQL static analysis (SAST)
- Dependabot dependency scanning
- GitHub Secret Scanning (push protection enabled)
- MIT Licensed with no tracking/analytics
