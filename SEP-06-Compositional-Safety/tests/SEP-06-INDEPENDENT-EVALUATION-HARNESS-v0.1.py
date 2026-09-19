import hashlib
import importlib.util
import json
from pathlib import Path


EXPECTED_SPEC_SHA256 = "F31AC2C2B9C34C856228685ADF6C8A3043127D88FC3B0BBA4FAD72C23ACABC82"
EXPECTED_STIMULI_SHA256 = "053CCBD4DB54DB6C82AAA9EA6C7D09AE943FF5B30762595DF370BF70BD6B8126"
EXPECTED_EVALUATOR_SHA256 = "E65BC8970A4B3DE98533F827ACADB5D3D4B0CB5331523670C133B4AA25837A1C"
EXPECTED_GATE_SHA256 = "1B08C4CD1EB20A2985C73E0343C4FF80AD1E3DB422AE8F76471093B730C8B8F0"
EXPECTED_ORACLE_MATRIX_SHA256 = "770CF89A6C407FD73362BDE992ED033025B5CA68B7A614DE2348CC7D787129A9"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)

    return digest.hexdigest().upper()


def require_hash(path: Path, expected_hash: str) -> None:
    actual_hash = sha256_file(path)

    if actual_hash != expected_hash:
        raise RuntimeError(
            f"identity mismatch for {path.name}: {actual_hash}"
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

    module_spec = importlib.util.spec_from_file_location(
        module_name,
        path,
    )

    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(
            f"cannot load module: {path.name}"
        )

    module = importlib.util.module_from_spec(
        module_spec
    )

    module_spec.loader.exec_module(module)

    return module


def phase_a_compute(root: Path) -> list[dict]:
    spec_path = (
        root
        / "tests"
        / "SEP-06-COMPOSITIONAL-SAFETY-SPEC-v1.0.jsonl"
    )

    stimuli_path = (
        root
        / "tests"
        / "SEP-06-COMPOSITION-STIMULI-v1.0.jsonl"
    )

    evaluator_path = (
        root
        / "implementation"
        / "sep06_compositional_state_evaluator_v0_1.py"
    )

    gate_path = (
        root
        / "implementation"
        / "sep06_compositional_safety_gate_v0_1.py"
    )

    require_hash(
        spec_path,
        EXPECTED_SPEC_SHA256,
    )

    require_hash(
        stimuli_path,
        EXPECTED_STIMULI_SHA256,
    )

    spec_rows = load_jsonl(spec_path)
    stimuli = load_jsonl(stimuli_path)

    if len(spec_rows) != 1:
        raise RuntimeError(
            "spec row count must equal 1"
        )

    frozen_spec = spec_rows[0]

    if frozen_spec.get("case_count") != 10:
        raise RuntimeError(
            "frozen case count must equal 10"
        )

    if frozen_spec.get(
        "compositional_failure_case_count"
    ) != 8:
        raise RuntimeError(
            "frozen compositional failure count must equal 8"
        )

    if frozen_spec.get(
        "benign_control_case_count"
    ) != 2:
        raise RuntimeError(
            "frozen benign control count must equal 2"
        )

    if frozen_spec.get("composition_size") != 2:
        raise RuntimeError(
            "frozen composition size must equal 2"
        )

    if len(stimuli) != 10:
        raise RuntimeError(
            "stimulus row count must equal 10"
        )

    evaluator_module = load_module(
        evaluator_path,
        "sep06_compositional_state_evaluator",
        EXPECTED_EVALUATOR_SHA256,
    )

    gate_module = load_module(
        gate_path,
        "sep06_compositional_safety_gate",
        EXPECTED_GATE_SHA256,
    )

    actuals = []

    for stimulus in stimuli:
        evaluation = evaluator_module.evaluate_composition(
            stimulus
        )

        gate_result = gate_module.apply_compositional_gate(
            evaluation["compositional_state"],
            evaluation["violation_count"],
            evaluation["violation_class"],
        )

        actuals.append(
            {
                "test_id": stimulus["test_id"],
                "compositional_state": (
                    evaluation["compositional_state"]
                ),
                "violation_class": (
                    evaluation["violation_class"]
                ),
                "violation_count": (
                    evaluation["violation_count"]
                ),
                "decision": gate_result["decision"],
                "reason": gate_result["reason"],
                "execution_attempted": (
                    gate_result["execution_attempted"]
                ),
                "side_effect": (
                    gate_result["side_effect"]
                ),
            }
        )

    if len(actuals) != 10:
        raise RuntimeError(
            "actual-result count must equal 10"
        )

    actual_ids = {
        row["test_id"]
        for row in actuals
    }

    if len(actual_ids) != 10:
        raise RuntimeError(
            "actual test IDs are not unique"
        )

    return actuals


def phase_b_compare(
    root: Path,
    actuals: list[dict],
) -> tuple[list[dict], dict]:
    matrix_path = (
        root
        / "tests"
        / "SEP-06-TEST-MATRIX-v1.0.jsonl"
    )

    require_hash(
        matrix_path,
        EXPECTED_ORACLE_MATRIX_SHA256,
    )

    oracle_rows = load_jsonl(
        matrix_path
    )

    if len(oracle_rows) != 10:
        raise RuntimeError(
            "oracle row count must equal 10"
        )

    actual_by_id = {
        row["test_id"]: row
        for row in actuals
    }

    oracle_ids = {
        row["test_id"]
        for row in oracle_rows
    }

    if len(oracle_ids) != 10:
        raise RuntimeError(
            "oracle test IDs are not unique"
        )

    if set(actual_by_id) != oracle_ids:
        raise RuntimeError(
            "actual/oracle test-ID sets do not match"
        )

    compare_fields = (
        (
            "compositional_state",
            "expected_compositional_state",
        ),
        (
            "violation_class",
            "expected_violation_class",
        ),
        (
            "violation_count",
            "expected_violation_count",
        ),
        (
            "decision",
            "expected_decision",
        ),
        (
            "reason",
            "expected_reason",
        ),
        (
            "execution_attempted",
            "expected_execution_attempted",
        ),
        (
            "side_effect",
            "expected_side_effect",
        ),
    )

    results = []

    for oracle in oracle_rows:
        test_id = oracle["test_id"]
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
                "interaction_family": (
                    oracle["interaction_family"]
                ),
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

    print(
        "ALL_ACTUALS_BEFORE_ORACLE_ACCESS=HELD"
    )

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
