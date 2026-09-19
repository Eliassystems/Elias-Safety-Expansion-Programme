"""SEP-07 independent internal oracle-separated evaluation harness v0.1."""

import hashlib
import json
import sys
from pathlib import Path


EXPECTED_SPEC_SHA256 = "C2A52D1EDBBF67BCF3454C6A2A18275DF7E70DEAC7C9CB1CD291F75ADA149B59"
EXPECTED_STIMULI_SHA256 = "A467CE2F8B3208744D0702980E8CCC1C79AC7D265F94AE2537774116913ECDF8"


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_jsonl(path):
    records = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def require_sha256(path, expected, label):
    actual = sha256_file(path)
    if actual != expected:
        raise RuntimeError(
            f"{label}_SHA256_MISMATCH:{actual}"
        )


def phase_a_compute_actuals(root):
    spec_path = root / "tests" / "SEP-07-HUMAN-ERROR-AND-MISUSE-SPEC-v1.0.jsonl"
    stimuli_path = root / "tests" / "SEP-07-HUMAN-ERROR-AND-MISUSE-STIMULI-v1.0.jsonl"

    require_sha256(spec_path, EXPECTED_SPEC_SHA256, "SPEC")
    require_sha256(stimuli_path, EXPECTED_STIMULI_SHA256, "STIMULI")

    implementation_dir = root / "implementation"
    sys.path.insert(0, str(implementation_dir))

    from sep07_human_error_misuse_evaluator_v0_1 import (
        evaluate_human_error_misuse,
    )
    from sep07_human_error_misuse_gate_v0_1 import (
        apply_human_error_misuse_gate,
    )

    stimuli = load_jsonl(stimuli_path)

    if len(stimuli) != 10:
        raise RuntimeError(
            f"STIMULUS_CASE_COUNT_INVALID:{len(stimuli)}"
        )

    actuals = []

    for case in stimuli:
        evaluation = evaluate_human_error_misuse(case)
        gate = apply_human_error_misuse_gate(evaluation)

        actuals.append(
            {
                "test_id": case["test_id"],
                "source_class": case["source_class"],
                "scenario": case["scenario"],
                "actual": {
                    "safety_state": evaluation["safety_state"],
                    "conflict_class": evaluation["conflict_class"],
                    "decision": gate["decision"],
                    "reason": evaluation["reason"],
                    "execution_attempted": gate["execution_attempted"],
                    "side_effect": gate["side_effect"],
                },
            }
        )

    if len(actuals) != 10:
        raise RuntimeError(
            f"ACTUAL_CASE_COUNT_INVALID:{len(actuals)}"
        )

    return actuals


def phase_b_compare(actuals, root):
    expected_oracle_sha256 = "B2476CD12D028CC42726A215D8A3DEF2CD379F98AA657B6CB906439099D2728E"
    matrix_path = root / "tests" / "SEP-07-TEST-MATRIX-v1.0.jsonl"

    require_sha256(
        matrix_path,
        expected_oracle_sha256,
        "ORACLE_MATRIX",
    )

    oracle_records = load_jsonl(matrix_path)

    if len(oracle_records) != 10:
        raise RuntimeError(
            f"ORACLE_CASE_COUNT_INVALID:{len(oracle_records)}"
        )

    oracle_by_id = {
        record["test_id"]: record
        for record in oracle_records
    }

    if len(oracle_by_id) != 10:
        raise RuntimeError("ORACLE_TEST_ID_UNIQUENESS_FAILURE")

    results = []

    for actual_record in actuals:
        test_id = actual_record["test_id"]

        if test_id not in oracle_by_id:
            raise RuntimeError(
                f"ORACLE_CASE_ABSENT:{test_id}"
            )

        expected = oracle_by_id[test_id]
        actual = actual_record["actual"]

        comparisons = {
            "safety_state": (
                actual["safety_state"]
                == expected["expected_safety_state"]
            ),
            "conflict_class": (
                actual["conflict_class"]
                == expected["expected_conflict_class"]
            ),
            "decision": (
                actual["decision"]
                == expected["expected_decision"]
            ),
            "reason": (
                actual["reason"]
                == expected["expected_reason"]
            ),
            "execution_attempted": (
                actual["execution_attempted"]
                == expected["expected_execution_attempted"]
            ),
            "side_effect": (
                actual["side_effect"]
                == expected["expected_side_effect"]
            ),
        }

        all_six = all(comparisons.values())
        expected_pass = (
            expected["expected_case_result"] == "PASS"
        )

        case_result = (
            "PASS"
            if all_six and expected_pass
            else "FAIL"
        )

        results.append(
            {
                "test_id": test_id,
                "source_class": actual_record["source_class"],
                "scenario": actual_record["scenario"],
                "actual": actual,
                "comparisons": comparisons,
                "case_result": case_result,
            }
        )

    return results


def main():
    root = Path(__file__).resolve().parents[1]

    actuals = phase_a_compute_actuals(root)

    print("ALL_ACTUALS_BEFORE_ORACLE_ACCESS=HELD")

    results = phase_b_compare(actuals, root)

    passed = sum(
        1
        for record in results
        if record["case_result"] == "PASS"
    )
    failed = len(results) - passed

    for record in results:
        print(
            json.dumps(
                record,
                separators=(",", ":"),
                sort_keys=True,
            )
        )

    summary = {
        "summary": {
            "case_count": len(results),
            "passed": passed,
            "failed": failed,
            "overall_result": (
                "PASS"
                if len(results) == 10 and failed == 0
                else "FAIL"
            ),
        }
    }

    print(
        json.dumps(
            summary,
            separators=(",", ":"),
            sort_keys=True,
        )
    )

    if summary["summary"]["overall_result"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
