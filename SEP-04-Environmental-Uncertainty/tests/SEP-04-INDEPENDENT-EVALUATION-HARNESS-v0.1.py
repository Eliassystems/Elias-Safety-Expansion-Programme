from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

SPEC_PATH = (
    ROOT
    / "tests"
    / "SEP-04-ENVIRONMENTAL-EVIDENCE-SPEC-v1.0.jsonl"
)

STIMULI_PATH = (
    ROOT
    / "tests"
    / "SEP-04-ENVIRONMENTAL-STIMULI-v1.0.jsonl"
)

EVALUATOR_PATH = (
    ROOT
    / "implementation"
    / "sep04_environmental_evidence_evaluator_v0_1.py"
)

GATE_PATH = (
    ROOT
    / "implementation"
    / "sep04_environmental_uncertainty_gate_v0_1.py"
)

EXPECTED_SPEC_SHA256 = (
    "78BFB0FFB4E058B7E3027C81CFA46E19915B8C0D7968E5C95F5E679ECDB1171F"
)

EXPECTED_STIMULI_SHA256 = (
    "562BA8229E1F043F415F4CC4FFD03F6E550889670DB29A3B16EA7EFFA1C3E7A1"
)

EXPECTED_EVALUATOR_SHA256 = (
    "BA77FBC92749AE73AD47704AD1949557AA7AA9469715378D5969C2DBDDE81216"
)

EXPECTED_GATE_SHA256 = (
    "DDC7A4E42F3DF800320D6EF4781D75C74AF591EF2331B896BAEB2890A5F64CFC"
)


EXPECTED_STIMULUS_FIELDS = {
    "stimulus_id",
    "evidence_artifact_id",
    "constraint_id",
    "identity_state",
    "authority_state",
    "action_format_state",
    "target_state",
    "policy_admissibility_state",
    "technical_action_validity_state",
    "environmental_precondition_required",
    "facts",
}


EXPECTED_ORACLE_FIELDS = {
    "test_id",
    "stimulus_id",
    "evidence_artifact_id",
    "test_type",
    "environmental_uncertainty_class",
    "constraint_id",
    "expected_environmental_precondition_state",
    "expected_environmental_uncertainty_decision",
    "expected_reason",
    "expected_execution_attempted",
    "expected_side_effect",
    "expected_case_result",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest().upper()


def verify_pre_oracle_bound_identities() -> None:
    bound = {
        SPEC_PATH: EXPECTED_SPEC_SHA256,
        STIMULI_PATH: EXPECTED_STIMULI_SHA256,
        EVALUATOR_PATH: EXPECTED_EVALUATOR_SHA256,
        GATE_PATH: EXPECTED_GATE_SHA256,
    }

    for path, expected_hash in bound.items():
        actual_hash = sha256_file(path)

        if actual_hash != expected_hash:
            raise RuntimeError(
                f"Bound identity mismatch: {path.name}"
            )


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(
        name,
        path,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Unable to load module: {path}"
        )

    module = importlib.util.module_from_spec(spec)

    sys.modules[spec.name] = module

    spec.loader.exec_module(module)

    return module


def load_stimuli() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    with STIMULI_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        for line_number, line in enumerate(
            handle,
            start=1,
        ):
            if not line.strip():
                continue

            row = json.loads(line)

            if set(row) != EXPECTED_STIMULUS_FIELDS:
                raise RuntimeError(
                    "Stimulus schema mismatch "
                    f"at line {line_number}"
                )

            rows.append(row)

    if len(rows) != 10:
        raise RuntimeError(
            "Frozen stimulus count must equal 10"
        )

    stimulus_ids = [
        row["stimulus_id"]
        for row in rows
    ]

    if len(set(stimulus_ids)) != len(stimulus_ids):
        raise RuntimeError(
            "Stimulus IDs are not unique"
        )

    forbidden_fields = {
        "test_id",
        "test_type",
        "environmental_uncertainty_class",
        "expected_environmental_precondition_state",
        "expected_environmental_uncertainty_decision",
        "expected_reason",
        "expected_execution_attempted",
        "expected_side_effect",
        "expected_case_result",
    }

    for row in rows:
        if forbidden_fields.intersection(row):
            raise RuntimeError(
                "Oracle field present in stimulus"
            )

    return rows


def evaluate_stimuli(
    stimuli: list[dict[str, Any]],
    evaluator: Any,
    gate: Any,
) -> dict[str, dict[str, Any]]:
    actuals: dict[str, dict[str, Any]] = {}

    for stimulus in stimuli:
        computed_state = (
            evaluator.evaluate_environmental_precondition(
                stimulus["constraint_id"],
                stimulus["facts"],
            )
        )

        gate_input = gate.EnvironmentalUncertaintyGateInput(
            evidence_artifact_id=(
                stimulus["evidence_artifact_id"]
            ),
            identity_state=stimulus["identity_state"],
            authority_state=stimulus["authority_state"],
            action_format_state=(
                stimulus["action_format_state"]
            ),
            target_state=stimulus["target_state"],
            policy_admissibility_state=(
                stimulus["policy_admissibility_state"]
            ),
            technical_action_validity_state=(
                stimulus[
                    "technical_action_validity_state"
                ]
            ),
            environmental_precondition_required=(
                stimulus[
                    "environmental_precondition_required"
                ]
            ),
            computed_environmental_precondition_state=(
                computed_state
            ),
        )

        decision = (
            gate.evaluate_environmental_uncertainty_gate(
                gate_input
            )
        )

        stimulus_id = stimulus["stimulus_id"]

        actuals[stimulus_id] = {
            "stimulus_id": stimulus_id,
            "evidence_artifact_id": (
                stimulus["evidence_artifact_id"]
            ),
            "constraint_id": stimulus["constraint_id"],
            "computed_environmental_precondition_state": (
                computed_state
            ),
            "actual_environmental_uncertainty_decision": (
                decision.environmental_uncertainty_decision
            ),
            "actual_reason": decision.reason,
            "actual_execution_attempted": (
                decision.execution_attempted
            ),
            "actual_side_effect": (
                decision.side_effect_occurred
            ),
        }

    if len(actuals) != len(stimuli):
        raise RuntimeError(
            "Actual-result cardinality mismatch"
        )

    return actuals


def load_oracle_matrix() -> list[dict[str, Any]]:
    matrix_path = (
        ROOT
        / "tests"
        / "SEP-04-TEST-MATRIX-v1.0.jsonl"
    )

    expected_matrix_sha256 = (
        "11A633CF42AC807A66CBC3FD1444DB30D6F37A3FD3C244CF5AEE1D144456B0E1"
    )

    actual_hash = sha256_file(matrix_path)

    if actual_hash != expected_matrix_sha256:
        raise RuntimeError(
            "Frozen oracle matrix identity mismatch"
        )

    rows: list[dict[str, Any]] = []

    with matrix_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        for line_number, line in enumerate(
            handle,
            start=1,
        ):
            if not line.strip():
                continue

            row = json.loads(line)

            if set(row) != EXPECTED_ORACLE_FIELDS:
                raise RuntimeError(
                    "Oracle schema mismatch "
                    f"at line {line_number}"
                )

            rows.append(row)

    if len(rows) != 10:
        raise RuntimeError(
            "Frozen oracle count must equal 10"
        )

    test_ids = [
        row["test_id"]
        for row in rows
    ]

    stimulus_ids = [
        row["stimulus_id"]
        for row in rows
    ]

    if len(set(test_ids)) != len(test_ids):
        raise RuntimeError(
            "Oracle test IDs are not unique"
        )

    if len(set(stimulus_ids)) != len(stimulus_ids):
        raise RuntimeError(
            "Oracle stimulus bindings are not unique"
        )

    return rows


def compare_to_oracle(
    actuals: dict[str, dict[str, Any]],
    oracle_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []

    passed = 0
    failed = 0
    uncertainty_cases = 0
    benign_controls = 0

    for oracle in oracle_rows:
        stimulus_id = oracle["stimulus_id"]

        if stimulus_id not in actuals:
            raise RuntimeError(
                "Oracle references absent actual result: "
                f"{stimulus_id}"
            )

        actual = actuals[stimulus_id]

        checks = {
            "constraint_id": (
                actual["constraint_id"]
                == oracle["constraint_id"]
            ),
            "evidence_artifact_id": (
                actual["evidence_artifact_id"]
                == oracle["evidence_artifact_id"]
            ),
            "environmental_precondition_state": (
                actual[
                    "computed_environmental_precondition_state"
                ]
                == oracle[
                    "expected_environmental_precondition_state"
                ]
            ),
            "environmental_uncertainty_decision": (
                actual[
                    "actual_environmental_uncertainty_decision"
                ]
                == oracle[
                    "expected_environmental_uncertainty_decision"
                ]
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

        base_result = (
            "PASS"
            if all(checks.values())
            else "FAIL"
        )

        checks["expected_case_result"] = (
            base_result
            == oracle["expected_case_result"]
        )

        case_result = (
            "PASS"
            if all(checks.values())
            else "FAIL"
        )

        if oracle["test_type"] == "ENVIRONMENTAL_UNCERTAINTY":
            uncertainty_cases += 1
        elif oracle["test_type"] == "BENIGN_CONTROL":
            benign_controls += 1
        else:
            raise RuntimeError(
                "Unsupported oracle test type"
            )

        if case_result == "PASS":
            passed += 1
        else:
            failed += 1

        results.append(
            {
                "test_id": oracle["test_id"],
                "stimulus_id": stimulus_id,
                "evidence_artifact_id": (
                    actual["evidence_artifact_id"]
                ),
                "constraint_id": actual["constraint_id"],
                "test_type": oracle["test_type"],
                "environmental_uncertainty_class": (
                    oracle["environmental_uncertainty_class"]
                ),
                "computed_environmental_precondition_state": (
                    actual[
                        "computed_environmental_precondition_state"
                    ]
                ),
                "expected_environmental_precondition_state": (
                    oracle[
                        "expected_environmental_precondition_state"
                    ]
                ),
                "actual_environmental_uncertainty_decision": (
                    actual[
                        "actual_environmental_uncertainty_decision"
                    ]
                ),
                "expected_environmental_uncertainty_decision": (
                    oracle[
                        "expected_environmental_uncertainty_decision"
                    ]
                ),
                "actual_reason": actual["actual_reason"],
                "expected_reason": oracle["expected_reason"],
                "actual_execution_attempted": (
                    actual["actual_execution_attempted"]
                ),
                "expected_execution_attempted": (
                    oracle["expected_execution_attempted"]
                ),
                "actual_side_effect": (
                    actual["actual_side_effect"]
                ),
                "expected_side_effect": (
                    oracle["expected_side_effect"]
                ),
                "checks": checks,
                "case_result": case_result,
            }
        )

    if uncertainty_cases != 8:
        raise RuntimeError(
            "Environmental uncertainty case count != 8"
        )

    if benign_controls != 2:
        raise RuntimeError(
            "Benign control case count != 2"
        )

    if len(actuals) != len(oracle_rows):
        raise RuntimeError(
            "Actual/oracle cardinality mismatch"
        )

    return {
        "sep04_independent_evaluation": "EXECUTED",
        "evaluation_order": (
            "ENVIRONMENTAL_STIMULUS_THEN_"
            "ENVIRONMENTAL_EVIDENCE_EVALUATION_THEN_"
            "COMPUTED_STATE_THEN_"
            "ENVIRONMENTAL_UNCERTAINTY_GATE_THEN_ORACLE"
        ),
        "case_count": len(oracle_rows),
        "environmental_uncertainty_cases": uncertainty_cases,
        "benign_controls": benign_controls,
        "passed": passed,
        "failed": failed,
        "primary_proposition": (
            "REQUIRES_POST_EXECUTION_DETERMINATION"
        ),
        "results": results,
    }


def main() -> int:
    verify_pre_oracle_bound_identities()

    evaluator = load_module(
        "sep04_environmental_evidence_evaluator_v0_1",
        EVALUATOR_PATH,
    )

    gate = load_module(
        "sep04_environmental_uncertainty_gate_v0_1",
        GATE_PATH,
    )

    stimuli = load_stimuli()

    actuals = evaluate_stimuli(
        stimuli,
        evaluator,
        gate,
    )

    oracle_rows = load_oracle_matrix()

    summary = compare_to_oracle(
        actuals,
        oracle_rows,
    )

    print(
        json.dumps(
            summary,
            sort_keys=True,
            separators=(",", ":"),
        )
    )

    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
