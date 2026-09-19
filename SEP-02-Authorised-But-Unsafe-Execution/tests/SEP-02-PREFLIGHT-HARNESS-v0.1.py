from __future__ import annotations

import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SEP02_ROOT = HERE.parent

IMPLEMENTATION_PATH = (
    SEP02_ROOT
    / "implementation"
    / "sep02_consequence_gate_v0_1.py"
)

MATRIX_PATH = HERE / "SEP-02-TEST-MATRIX-v1.0.jsonl"


def load_gate_module():
    spec = importlib.util.spec_from_file_location(
        "sep02_consequence_gate_v0_1",
        IMPLEMENTATION_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load SEP-02 consequence gate module")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_matrix():
    rows = []

    with MATRIX_PATH.open("r", encoding="utf-8", newline="\n") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue

            row = json.loads(line)
            row["_line_number"] = line_number
            rows.append(row)

    return rows


def evaluate_case(gate, row):
    inp = gate.ConsequenceGateInput(
        case_id=row["test_id"],
        constraint_id=row["constraint_id"],
        identity_state=row["identity_state"],
        authority_state=row["authority_state"],
        policy_state=row["policy_state"],
        technical_validity_state=row["technical_validity_state"],
        consequence_state=row["consequence_state"],
    )

    decision = gate.evaluate_consequence_gate(inp)

    checks = {
        "decision": decision.decision == row["expected_decision"],
        "reason": decision.reason == row["expected_reason"],
        "execution_attempted": (
            decision.execution_attempted
            == row["expected_execution_attempted"]
        ),
        "side_effect_occurred": (
            decision.side_effect_occurred
            == row["expected_side_effect"]
        ),
    }

    case_pass = all(checks.values())

    return {
        "test_id": row["test_id"],
        "source_case_id": row["source_case_id"],
        "constraint_id": row["constraint_id"],
        "test_type": row["test_type"],
        "expected_decision": row["expected_decision"],
        "actual_decision": decision.decision,
        "expected_reason": row["expected_reason"],
        "actual_reason": decision.reason,
        "expected_execution_attempted": row[
            "expected_execution_attempted"
        ],
        "actual_execution_attempted": decision.execution_attempted,
        "expected_side_effect": row["expected_side_effect"],
        "actual_side_effect": decision.side_effect_occurred,
        "checks": checks,
        "case_result": "PASS" if case_pass else "FAIL",
    }


def main():
    gate = load_gate_module()
    rows = load_matrix()

    if len(rows) != 10:
        raise AssertionError(
            f"Expected exactly 10 frozen SEP-02 cases, found {len(rows)}"
        )

    results = [evaluate_case(gate, row) for row in rows]

    hazard_results = [
        result
        for result in results
        if result["test_type"] == "HAZARD"
    ]

    benign_results = [
        result
        for result in results
        if result["test_type"] == "BENIGN_CONTROL"
    ]

    summary = {
        "sep02_preflight": "EXECUTED",
        "case_count": len(results),
        "hazard_cases": len(hazard_results),
        "benign_controls": len(benign_results),
        "passed": sum(
            1 for result in results if result["case_result"] == "PASS"
        ),
        "failed": sum(
            1 for result in results if result["case_result"] != "PASS"
        ),
        "primary_proposition": "NOT_DETERMINED_BY_PREFLIGHT_ALONE",
        "results": results,
    }

    print(
        json.dumps(
            summary,
            sort_keys=True,
            separators=(",", ":"),
        )
    )

    if summary["failed"] != 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
