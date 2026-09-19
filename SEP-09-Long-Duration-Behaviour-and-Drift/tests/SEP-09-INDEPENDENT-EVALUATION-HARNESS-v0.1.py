"""SEP-09 independent internal evaluation harness v0.1.

Phase A:
    Load only the frozen stimuli.
    Produce and fully materialize every actual result.
    Output every Phase-A actual before the oracle-access marker.
    No oracle access occurs in Phase A.

Phase B:
    Only after Phase A is complete, bind the frozen oracle locally,
    verify its identity, and compare the already-materialized actuals.

No continued-operation execution, monitoring, remediation, correction,
upgrade, migration, or other real-world side-effect capability exists here.
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
    implementation_dir = (
        repo_root
        / "SEP-09-Long-Duration-Behaviour-and-Drift"
        / "implementation"
    )

    sys.path.insert(0, str(implementation_dir))


def phase_a_evaluate(stimuli_path, repo_root):
    configure_import_path(repo_root)

    from sep09_long_duration_drift_evaluator_v0_1 import evaluate_drift
    from sep09_long_duration_drift_gate_v0_1 import apply_long_duration_drift_gate

    stimuli_records = load_jsonl(stimuli_path)

    if len(stimuli_records) != 10:
        raise RuntimeError("SEP-09 frozen stimulus count is not 10")

    actuals = []

    for stimulus in stimuli_records:
        evaluation = evaluate_drift(stimulus)
        gate_result = apply_long_duration_drift_gate(evaluation)

        actuals.append(
            {
                "test_id": stimulus["test_id"],
                "source_class": stimulus["source_class"],
                "scenario": stimulus["scenario"],
                "actual": {
                    "drift_state": gate_result["drift_state"],
                    "decision": gate_result["decision"],
                    "reason": gate_result["reason"],
                    "continuation_authorized": gate_result[
                        "continuation_authorized"
                    ],
                    "primary_proposition_support": gate_result[
                        "primary_proposition_support"
                    ],
                },
            }
        )

    if len(actuals) != 10:
        raise RuntimeError("SEP-09 Phase A did not materialize 10 actual results")

    return actuals


def phase_b_compare(actuals, sep09_root):
    oracle_path = (
        sep09_root
        / "tests"
        / "SEP-09-TEST-MATRIX-v1.0.jsonl"
    )

    oracle_expected_sha256 = (
        "7B9D38DFED617DA387279BF0FE03173ABF7B97A100AE7BED5A9FE4DDF474425D"
    )

    if sha256_file(oracle_path) != oracle_expected_sha256:
        raise RuntimeError("SEP-09 frozen oracle identity mismatch")

    oracle_records = load_jsonl(oracle_path)

    if len(oracle_records) != 10:
        raise RuntimeError("SEP-09 frozen oracle count is not 10")

    oracle_by_id = {}

    for oracle_record in oracle_records:
        test_id = oracle_record["test_id"]

        if test_id in oracle_by_id:
            raise RuntimeError("duplicate SEP-09 oracle test id")

        oracle_by_id[test_id] = oracle_record

    comparison_fields = (
        ("drift_state", "expected_drift_state"),
        ("decision", "expected_decision"),
        ("reason", "expected_reason"),
        ("continuation_authorized", "expected_continuation_authorized"),
        (
            "primary_proposition_support",
            "expected_primary_proposition_support",
        ),
    )

    result_records = []
    passed = 0
    failed = 0

    for actual_record in actuals:
        test_id = actual_record["test_id"]

        if test_id not in oracle_by_id:
            raise RuntimeError("actual SEP-09 result has no oracle record")

        oracle_record = oracle_by_id[test_id]

        if actual_record["source_class"] != oracle_record["source_class"]:
            raise RuntimeError("SEP-09 source-class mismatch")

        if actual_record["scenario"] != oracle_record["scenario"]:
            raise RuntimeError("SEP-09 scenario mismatch")

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
        "overall_result": (
            "PASS"
            if passed == 10 and failed == 0
            else "FAIL"
        ),
    }

    return result_records, summary


def main():
    harness_path = Path(__file__).resolve()
    sep09_root = harness_path.parent.parent
    repo_root = sep09_root.parent

    stimuli_path = (
        sep09_root
        / "tests"
        / "SEP-09-LONG-DURATION-BEHAVIOUR-AND-DRIFT-STIMULI-v1.0.jsonl"
    )

    expected_stimuli_sha256 = (
        "614265068FAE3BCEBCB917DB1C4A1912A5355E6F96699179EEFA1C91C6B3CC23"
    )

    if sha256_file(stimuli_path) != expected_stimuli_sha256:
        raise RuntimeError("SEP-09 frozen stimuli identity mismatch")

    actuals = phase_a_evaluate(stimuli_path, repo_root)

    for actual_record in actuals:
        print(
            json.dumps(
                {"phase_a_actual": actual_record},
                sort_keys=True,
                separators=(",", ":"),
            )
        )

    print("ALL_ACTUALS_BEFORE_ORACLE_ACCESS=HELD")

    result_records, summary = phase_b_compare(
        actuals,
        sep09_root,
    )

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
