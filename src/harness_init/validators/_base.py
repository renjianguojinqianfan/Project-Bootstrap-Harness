"""Shared validation helpers and constants."""


_CHECK = "check"
_PASSED = "passed"
_MESSAGE = "message"

_REQUIRED_SECTIONS = {
    "snapshot": r"#+\s*\d*\.?\s*Project\s+Snapshot",
    "quick_start": r"#+\s*\d*\.?\s*Quick\s+Start",
    "critical_rules": r"#+\s*\d*\.?\s*Critical\s+Rules",
    "file_mapping": r"#+\s*\d*\.?\s*File\s+Mapping",
    "commands": r"#+\s*\d*\.?\s*Commands",
}

_CRITICAL_RULES_MUST = [
    r"make\s+verify",
    r"(self.?evaluation|自评估)",
    r"(secret|密钥|hardcode)",
]

_FILE_MAPPING_MUST = [r"src/", r"tests/", r"docs/", r"tasks/", r"\.harness/"]

_COMMANDS_MUST = [r"make\s+verify", r"make\s+test", r"make\s+lint"]

_VALID_STAGES = {"init", "plan", "execute", "evaluate", "done"}


def _result(check: str, passed: bool, message: str) -> dict:
    """Create a single validation result dict."""
    return {_CHECK: check, _PASSED: passed, _MESSAGE: message}
