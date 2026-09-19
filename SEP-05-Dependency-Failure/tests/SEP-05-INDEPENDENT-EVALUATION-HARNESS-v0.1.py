"""SEP-05 oracle-separated independent evaluation harness.

Phase A computes every actual result without constructing, opening,
hashing, reading, or parsing the frozen oracle matrix.

Phase B begins only after the complete actual-result set exists.
"""

import hashlib
import importlib.util
import json
from pathlib import Path


EXPECTED_SPEC_SHA256 = "950E78DD4AE4715EA540460429760E4EF868E0E4E8E6DA003B3974AD92D84DCA"
EXPECTED_STIMULI_SHA256 = "B9AB8436A8FF9D21C49CEFC23730CC43E9DAE7D204961782783C10B4048DFCAC"
EXPECTED_EVALUATOR_SHA256 = "8201AD3BDCFD56A5B48745728D6B85F95EB27B742DA50FA4D7DC41F6279A596E"
EXPECTED_GATE_SHA256 = "AAE83790567E9F06E9472C85A520ABEA0A1C472FF436EA7A87B8DABA874CEE23"
EXPECTED_ORACLE_MATRIX_SHA256 = "25C8BEAE5BA5DDAD67641291CD617A9F242E71A6CD925D3142155A06C9BE6F22"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)

    return digest.hexdigest().upper()


def require_hash(path: Path, expected: str) -> None:
    actual = sha256_file(path)

    if actual != expected:
        raise RuntimeError(
            f"identity mismatch for {path.name}: {actual}"
        )


def load_jsonl(path: Path) -> list[dict]:
    rows = []

    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()

            if stripped:
                rows.append(json.loads(stripped))

    return rows


def load_module(
    path: Path,
    module_name: str,
    expected_hash: str,
):
    require_hash(path, expected_hash)

    spec = importlib.util.spec_from_file_location(
        module_name,
        path,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path.name}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def phase_a_compute(root: Path) -> list[dict]:
    spec_path = (
        root
        / "tests"
        / "SEP-05-DEPENDENCY-FAILURE-SPEC-v1.0.jsonl"
    )

    stimuli_path = (
        root
        / "tests"
        / "SEP-05-DEPENDENCY-STIMULI-v1.0.jsonl"
    )

    evaluator_path = (
        root
        / "implementation"
        / "sep05_dependency_state_evaluator_v0_1.py"
    )

    gate_path = (
        root
        / "implementation"
        / "sep05_dependency_failure_gate_v0_1.py"
    )

    require_hash(spec_path, EXPECTED_SPEC_SHA256)
    require_hash(stimuli_path, EXPECTED_STIMULI_SHA256)

    spec_rows = load_jsonl(spec_path)
    stimuli = load_jsonl(stimuli_path)

    if len(spec_rows) != 1:
        raise RuntimeError("spec row count must equal 1")

    if len(stimuli) != 10:
        raise RuntimeError("stimulus row count must equal 10")

    dependency_evaluator = load_module(
        evaluator_path,
        "sep05_dependency_state_evaluator",
        EXPECTED_EVALUATOR_SHA256,
    )

    dependency_gate = load_module(
        gate_path,
        "sep05_dependency_failure_gate",
        EXPECTED_GATE_SHA256,
    )

    actuals = []

    for stimulus in stimuli:
        evaluation = (
            dependency_evaluator.evaluate_dependency_state(
                stimulus
            )
        )

        gate_result = dependency_gate.apply_dependency_gate(
            evaluation["dependency_state"],
            evaluation["dependency_determination"],
        )

        actuals.append(
            {
                "test_id": stimulus["test_id"],
                "dependency_state": (
                    evaluation["dependency_state"]
                ),
                "dependency_determination": (
                    evaluation["dependency_determination"]
                ),
                "decision": gate_result["decision"],
                "reason": gate_result["reason"],
                "execution_attempted": (
                    gate_result["execution_attempted"]
                ),
                "side_effect": gate_result["side_effect"],
            }
        )

    if len(actuals) != 10:
        raise RuntimeError("actual-result count must equal 10")

    return actuals


def phase_b_compare(
    root: Path,
    actuals: list[dict],
) -> tuple[list[dict], dict]:
    matrix_path = (
        root
        / "tests"
        / "SEP-05-TEST-MATRIX-v1.0.jsonl"
    )

    require_hash(
        matrix_path,
        EXPECTED_ORACLE_MATRIX_SHA256,
    )

    oracle_rows = load_jsonl(matrix_path)

    if len(oracle_rows) != 10:
        raise RuntimeError("oracle row count must equal 10")

    actual_by_id = {
        row["test_id"]: row
        for row in actuals
    }

    if len(actual_by_id) != 10:
        raise RuntimeError("actual test IDs are not unique")

    results = []

    compare_fields = (
        ("dependency_state", "expected_dependency_state"),
        (
            "dependency_determination",
            "expected_dependency_determination",
        ),
        ("decision", "expected_decision"),
        ("reason", "expected_reason"),
        (
            "execution_attempted",
            "expected_execution_attempted",
        ),
        ("side_effect", "expected_side_effect"),
    )

    for oracle in oracle_rows:
        test_id = oracle["test_id"]

        if test_id not in actual_by_id:
            raise RuntimeError(
                f"actual result absent for {test_id}"
            )

        actual = actual_by_id[test_id]

        comparisons = {}

        for actual_field, expected_field in compare_fields:
            comparisons[actual_field] = (
                actual[actual_field]
                == oracle[expected_field]
            )

        case_pass = (
            all(comparisons.values())
            and oracle["expected_case_result"] == "PASS"
        )

        results.append(
            {
                "test_id": test_id,
                "source_class": oracle["source_class"],
                "actual": actual,
                "comparisons": comparisons,
                "case_result": (
                    "PASS"
                    if case_pass
                    else "FAIL"
                ),
            }
        )

    passed = sum(
        1
        for result in results
        if result["case_result"] == "PASS"
    )

    failed = len(results) - passed

    summary = {
        "case_count": len(results),
        "passed": passed,
        "failed": failed,
        "overall_result": (
            "PASS"
            if failed == 0 and len(results) == 10
            else "FAIL"
        ),
    }

    return results, summary


def main() -> int:
    root = Path(__file__).resolve().parents[1]

    actuals = phase_a_compute(root)

    print("ALL_ACTUALS_BEFORE_ORACLE_ACCESS=HELD")

    results, summary = phase_b_compare(
        root,
        actuals,
    )

    for result in results:
        print(
            json.dumps(
                result,
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

    return (
        0
        if summary["overall_result"] == "PASS"
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
