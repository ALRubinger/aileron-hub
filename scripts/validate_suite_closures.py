#!/usr/bin/env python3
"""
Verify Hub suite-entry invariants beyond JSON Schema.

For every YAML under suites/:

  1. Every FQN in `member_actions` resolves to an entry under actions/.
  2. If `connectors_required` is present, it equals the set of
     `connector_fqn` values from the resolved member actions.

Intentionally lenient when `connectors_required` is omitted: that matches
the daemon's `resolveSuiteConnectorClosure` fallback (Aileron PR #717),
which derives the closure from `member_actions` at query time.

Exit codes:
  0  all suites valid
  1  one or more suites violate an invariant
  2  load/parse error (treated as a validation failure)
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
ACTIONS_DIR = REPO_ROOT / "actions"
SUITES_DIR = REPO_ROOT / "suites"


def load_actions() -> dict[str, str]:
    """Return {action_fqn: connector_fqn} for every actions/*.yaml."""
    by_fqn: dict[str, str] = {}
    if not ACTIONS_DIR.is_dir():
        return by_fqn
    for path in sorted(ACTIONS_DIR.glob("*.y*ml")):
        with path.open() as f:
            entry = yaml.safe_load(f) or {}
        fqn = entry.get("fqn")
        connector_fqn = entry.get("connector_fqn")
        if not fqn or not connector_fqn:
            raise SystemExit(
                f"actions/{path.name}: missing fqn or connector_fqn "
                "(should have been caught by JSON Schema)"
            )
        if fqn in by_fqn:
            raise SystemExit(f"duplicate action fqn: {fqn}")
        by_fqn[fqn] = connector_fqn
    return by_fqn


def check_suite(path: Path, action_index: dict[str, str]) -> list[str]:
    """Return a list of human-readable errors for one suite file."""
    errors: list[str] = []
    with path.open() as f:
        suite = yaml.safe_load(f) or {}

    members = suite.get("member_actions") or []
    declared = suite.get("connectors_required")

    derived: set[str] = set()
    for member_fqn in members:
        connector_fqn = action_index.get(member_fqn)
        if connector_fqn is None:
            errors.append(
                f"member_actions references unknown action: {member_fqn} "
                "(no matching entry under actions/)"
            )
            continue
        derived.add(connector_fqn)

    if declared is not None:
        declared_set = set(declared)
        if declared_set != derived:
            missing = sorted(derived - declared_set)
            extra = sorted(declared_set - derived)
            parts = []
            if missing:
                parts.append(f"missing {missing}")
            if extra:
                parts.append(f"unexpected {extra}")
            errors.append(
                "connectors_required does not match the union of "
                f"member_actions[].connector_fqn: {'; '.join(parts)}. "
                "Either fix the list or remove it (the daemon derives "
                "the closure from member_actions when omitted)."
            )

    return errors


def main() -> int:
    try:
        action_index = load_actions()
    except SystemExit:
        raise
    except Exception as exc:
        print(f"failed to load actions/: {exc}", file=sys.stderr)
        return 2

    if not SUITES_DIR.is_dir():
        print("No suites/ directory; nothing to validate.")
        return 0

    suite_files = sorted(SUITES_DIR.glob("*.y*ml"))
    if not suite_files:
        print("No suite entries found under suites/; nothing to validate.")
        return 0

    failed = False
    for path in suite_files:
        try:
            errors = check_suite(path, action_index)
        except Exception as exc:
            print(f"suites/{path.name}: parse error: {exc}", file=sys.stderr)
            failed = True
            continue
        if errors:
            failed = True
            for err in errors:
                print(f"suites/{path.name}: {err}", file=sys.stderr)
        else:
            print(f"suites/{path.name}: OK")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
