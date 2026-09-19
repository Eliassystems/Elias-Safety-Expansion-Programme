from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SEP02_ROOT = HERE.parent

EVALUATOR_PATH = (
    SEP02_ROOT
    / "implementation"
    / "sep02_consequence_evaluator_v0_1.py"
)

GATE_PATH = (
    SEP02_ROOT
    / "implementation"
    / "sep02_consequence_gate_v0_1.py"
)

FIXTURE_PATH = HERE / "SEP-02-INPUT-FIXTURES-v1.0.jsonl"
MATRIX_PATH = HERE / "SEP-02-TEST-MATRIX-v1.0.jsonl"

EXPECTED_EVALUATOR_SHA256 = (
    "AF185D684C8015BEEE1AB89B445A2C7ACE7E968B27675C5B190A619D1DD1A9F0"
)

EXPECTED_GATE_SHA256 = (
    "A40E004AC8840635E0D5CB0B53E87DF3E5662686AC83B09025D6CAF3B58C54DF"
)

EXPECTED_FIXTURE_SHA256 = (
    "6F302605A27F64908345EA992879BC2A3DF0F4623F85A85DAB50C3C386D7CD37"
)

EXPECTED_MATRIX_SHA256 = (
    "C309AE28FE3F35C275A62C752BF05521627053761E6277AEC81D828882DF0CB1"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def require_file_identity(
    path: Path,
    expected_sha256: str,
    label: str,
) -> None:
    actual = sha256_file(path)

    if actual != expected_sha256:
        raise RuntimeError(
            f"{label} identity mismatch: "
            f"expected {expected_sha256}, received {actual}"
        )


def load_module(
    module_name: str,
    path: Path,
    expected_sha256: str,
):
    require_file_identity(
        path,
        expected_sha256,
        module_name,
    )

    spec = importlib.util.spec_from_file_location(
        module_name,
        path,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Unable to load module: {module_name}"
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    with path.open(
        "r",
        encoding="utf-8",
        newline="\n",
    ) as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue

            row = json.loads(line)

            if not isinstance(row, dict):
                raise AssertionError(
                    f"JSONL row {line_number} is not an object"
                )

            rows.append(row)

    return rows


def load_fixtures() -> list[dict[str, Any]]:
    require_file_identity(
        FIXTURE_PATH,
        EXPECTED_FIXTURE_SHA256,
        "frozen fixture set",
    )

    fixtures = load_jsonl(FIXTURE_PATH)

    if len(fixtures) != 10:
        raise AssertionError(
            f"Expected exactly 10 frozen fixtures, found {len(fixtures)}"
        )

    required_fields = {
        "test_id",
        "constraint_id",
        "identity_state",
        "authority_state",
        "policy_state",
        "technical_validity_state",
        "facts",
    }

    seen_test_ids: set[str] = set()

    for fixture in fixtures:
        if set(fixture) != required_fields:
            raise AssertionError(
                f"Fixture {fixture.get('test_id')!r} "
                "contains missing or unexpected fields"
            )

        test_id = fixture["test_id"]

        if test_id in seen_test_ids:
            raise AssertionError(
                f"Duplicate fixture test_id: {test_id}"
            )

        seen_test_ids.add(test_id)

        for upstream_field in (
            "identity_state",
            "authority_state",
            "policy_state",
            "technical_validity_state",
        ):
            if fixture[upstream_field] != "PASS":
                raise AssertionError(
                    f"{test_id}: {upstream_field} is not PASS"
                )

        if not isinstance(fixture["facts"], dict):
            raise AssertionError(
                f"{test_id}: facts must be an object"
            )

    return fixtures


def evaluate_stimuli(
    evaluator,
    gate,
    fixtures: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    actuals: list[dict[str, Any]] = []

    for fixture in fixtures:
        computed_state = evaluator.evaluate_consequence(
            fixture["constraint_id"],
            fixture["facts"],
        )

        gate_input = gate.ConsequenceGateInput(
            case_id=fixture["test_id"],
            constraint_id=fixture["constraint_id"],
            identity_state=fixture["identity_state"],
            authority_state=fixture["authority_state"],
            policy_state=fixture["policy_state"],
            technical_validity_state=fixture[
                "technical_validity_state"
            ],
            consequence_state=computed_state,
        )

        decision = gate.evaluate_consequence_gate(
            gate_input
        )

        actuals.append(
            {
                "test_id": fixture["test_id"],
                "constraint_id": fixture["constraint_id"],
                "computed_consequence_state": computed_state,
                "actual_decision": decision.decision,
                "actual_reason": decision.reason,
                "actual_execution_attempted": (
                    decision.execution_attempted
                ),
                "actual_side_effect": (
                    decision.side_effect_occurred
                ),
            }
        )

    return actuals


def load_oracle_matrix() -> list[dict[str, Any]]:
    require_file_identity(
        MATRIX_PATH,
        EXPECTED_MATRIX_SHA256,
        "frozen oracle matrix",
    )

    rows = load_jsonl(MATRIX_PATH)

    if len(rows) != 10:
        raise AssertionError(
            f"Expected exactly 10 oracle rows, found {len(rows)}"
        )

    test_ids = [row["test_id"] for row in rows]

    if len(set(test_ids)) != 10:
        raise AssertionError(
            "Oracle matrix test_id values are not unique"
        )

    return rows


def compare_to_oracle(
    actuals: list[dict[str, Any]],
    oracle_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    oracle_by_test_id = {
        row["test_id"]: row
        for row in oracle_rows
    }

    actual_ids = {
        actual["test_id"]
        for actual in actuals
    }

    oracle_ids = set(oracle_by_test_id)

    if actual_ids != oracle_ids:
        raise AssertionError(
            "Actual/oracle test-id sets differ"
        )

    results: list[dict[str, Any]] = []

    for actual in actuals:
        oracle = oracle_by_test_id[actual["test_id"]]

        checks = {
            "constraint_id": (
                actual["constraint_id"]
                == oracle["constraint_id"]
            ),
            "consequence_state": (
                actual["computed_consequence_state"]
                == oracle["consequence_state"]
            ),
            "decision": (
                actual["actual_decision"]
                == oracle["expected_decision"]
            ),
            "reason": (
                actual["actual_reason"]
                == oracle["expected_reason"]
            ),
            "execution_attempted": (
                actual["actual_execution_attempted"]
                == oracle["expected_execution_attempted"]
            ),
            "side_effect": (
                actual["actual_side_effect"]
                == oracle["expected_side_effect"]
            ),
        }

        case_pass = all(checks.values())

        results.append(
            {
                "test_id": actual["test_id"],
                "source_case_id": oracle["source_case_id"],
                "test_type": oracle["test_type"],
                "constraint_id": actual["constraint_id"],
                "expected_consequence_state": (
                    oracle["consequence_state"]
                ),
                "computed_consequence_state": (
                    actual["computed_consequence_state"]
                ),
                "expected_decision": (
                    oracle["expected_decision"]
                ),
                "actual_decision": (
                    actual["actual_decision"]
                ),
                "expected_reason": (
                    oracle["expected_reason"]
                ),
                "actual_reason": (
                    actual["actual_reason"]
                ),
                "expected_execution_attempted": (
                    oracle["expected_execution_attempted"]
                ),
                "actual_execution_attempted": (
                    actual["actual_execution_attempted"]
                ),
                "expected_side_effect": (
                    oracle["expected_side_effect"]
                ),
                "actual_side_effect": (
                    actual["actual_side_effect"]
                ),
                "checks": checks,
                "case_result": (
                    "PASS"
                    if case_pass
                    else "FAIL"
                ),
            }
        )

    return results


def main() -> None:
    evaluator = load_module(
        "sep02_consequence_evaluator_v0_1",
        EVALUATOR_PATH,
        EXPECTED_EVALUATOR_SHA256,
    )

    gate = load_module(
        "sep02_consequence_gate_v0_1",
        GATE_PATH,
        EXPECTED_GATE_SHA256,
    )

    fixtures = load_fixtures()

    actuals = evaluate_stimuli(
        evaluator,
        gate,
        fixtures,
    )

    oracle_rows = load_oracle_matrix()

    results = compare_to_oracle(
        actuals,
        oracle_rows,
    )

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

    passed = sum(
        1
        for result in results
        if result["case_result"] == "PASS"
    )

    failed = len(results) - passed

    summary = {
        "sep02_independent_evaluation": "EXECUTED",
        "evaluation_order": (
            "STIMULUS_THEN_EVALUATOR_THEN_GATE_THEN_ORACLE"
        ),
        "case_count": len(results),
        "hazard_cases": len(hazard_results),
        "benign_controls": len(benign_results),
        "passed": passed,
        "failed": failed,
        "primary_proposition": (
            "REQUIRES_POST_EXECUTION_DETERMINATION"
        ),
        "results": results,
    }

    print(
        json.dumps(
            summary,
            sort_keys=True,
            separators=(",", ":"),
        )
    )

    if failed != 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
