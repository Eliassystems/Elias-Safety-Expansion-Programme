"""SEP-08 independent internal evaluation harness v0.1.

Phase A:
    Load frozen stimuli.
    Produce and fully materialize all actual results.
    No oracle access.

Phase B:
    After Phase A has returned all actuals, bind and verify the frozen
    oracle, then compare the already-materialized actual results.

No real-world execution capability exists in this harness.
"""

import hashlib
import json
import sys
from pathlib import Path


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


def configure_import_path(repo_root):
    implementation_dir = repo_root / "SEP-08-Containment-and-Recovery" / "implementation"
    sys.path.insert(0, str(implementation_dir))


def phase_a_evaluate(stimuli_path, repo_root):
    configure_import_path(repo_root)

    from sep08_containment_recovery_evaluator_v0_1 import evaluate_recoverability
    from sep08_containment_recovery_gate_v0_1 import apply_recoverability_gate

    stimuli_records = load_jsonl(stimuli_path)

    if len(stimuli_records) != 10:
        raise RuntimeError("SEP-08 frozen stimulus count is not 10")

    actuals = []

    for stimulus in stimuli_records:
        evaluation = evaluate_recoverability(stimulus)
        gate_result = apply_recoverability_gate(evaluation)

        actuals.append(
            {
                "test_id": stimulus["test_id"],
                "source_class": stimulus["source_class"],
                "scenario": stimulus["scenario"],
                "actual": {
                    "safety_state": gate_result["safety_state"],
                    "recovery_state": gate_result["recovery_state"],
                    "decision": gate_result["decision"],
                    "reason": gate_result["reason"],
                    "execution_attempted": gate_result["execution_attempted"],
                    "side_effect": gate_result["side_effect"],
                },
            }
        )

    if len(actuals) != 10:
        raise RuntimeError("SEP-08 Phase A did not materialize 10 actual results")

    return actuals


def phase_b_compare(actuals, sep08_root):
    oracle_path = sep08_root / "tests" / "SEP-08-TEST-MATRIX-v1.0.jsonl"
    oracle_expected_sha256 = "FE83F0C9A92351F8DD03CA8AF7A14E8B467C8BC8DBA129E861FC892C619590E9"

    if sha256_file(oracle_path) != oracle_expected_sha256:
        raise RuntimeError("SEP-08 frozen oracle identity mismatch")

    oracle_records = load_jsonl(oracle_path)

    if len(oracle_records) != 10:
        raise RuntimeError("SEP-08 frozen oracle count is not 10")

    oracle_by_id = {}

    for record in oracle_records:
        test_id = record["test_id"]

        if test_id in oracle_by_id:
            raise RuntimeError("duplicate SEP-08 oracle test id")

        oracle_by_id[test_id] = record

    result_records = []
    passed = 0
    failed = 0

    comparison_fields = (
        ("safety_state", "expected_safety_state"),
        ("recovery_state", "expected_recovery_state"),
        ("decision", "expected_decision"),
        ("reason", "expected_reason"),
        ("execution_attempted", "expected_execution_attempted"),
        ("side_effect", "expected_side_effect"),
    )

    for actual_record in actuals:
        test_id = actual_record["test_id"]

        if test_id not in oracle_by_id:
            raise RuntimeError("actual result has no frozen oracle record")

        oracle_record = oracle_by_id[test_id]

        if actual_record["source_class"] != oracle_record["source_class"]:
            raise RuntimeError("source class mismatch")

        if actual_record["scenario"] != oracle_record["scenario"]:
            raise RuntimeError("scenario mismatch")

        comparisons = {}

        for actual_field, oracle_field in comparison_fields:
            comparisons[actual_field] = (
                actual_record["actual"][actual_field]
                == oracle_record[oracle_field]
            )

        case_result = (
            "PASS"
            if all(comparisons.values())
            and oracle_record["expected_case_result"] == "PASS"
            else "FAIL"
        )

        if case_result == "PASS":
            passed += 1
        else:
            failed += 1

        result_records.append(
            {
                "test_id": test_id,
                "source_class": actual_record["source_class"],
                "scenario": actual_record["scenario"],
                "actual": actual_record["actual"],
                "comparisons": comparisons,
                "case_result": case_result,
            }
        )

    summary = {
        "case_count": len(result_records),
        "passed": passed,
        "failed": failed,
        "overall_result": "PASS" if failed == 0 and passed == 10 else "FAIL",
    }

    return result_records, summary


def main():
    harness_path = Path(__file__).resolve()
    sep08_root = harness_path.parent.parent
    repo_root = sep08_root.parent

    stimuli_path = (
        sep08_root
        / "tests"
        / "SEP-08-CONTAINMENT-AND-RECOVERY-STIMULI-v1.0.jsonl"
    )

    actuals = phase_a_evaluate(stimuli_path, repo_root)

    print("ALL_ACTUALS_BEFORE_ORACLE_ACCESS=HELD")

    result_records, summary = phase_b_compare(actuals, sep08_root)

    for result_record in result_records:
        print(
            json.dumps(
                result_record,
                sort_keys=True,
                separators=(",", ":"),
            )
        )

    print(
        json.dumps(
            {"summary": summary},
            sort_keys=True,
            separators=(",", ":"),
        )
    )

    return 0 if summary["overall_result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
