# ELIAS SAFETY EXPANSION PROGRAMME

# SEP-03 — POLICY CORRECTNESS FAILURE

VERSION: 0.1
STATUS: PROSPECTIVE
OBJECT: SEP-03_POLICY_CORRECTNESS_FAILURE

---

## 1. PURPOSE

SEP-03 tests whether Elias can distinguish a policy that is merely
syntactically valid and loadable from a policy that is admissible under
frozen policy-correctness constraints.

SEP-02 established, within its frozen scope, that consequence safety may
withhold an action after upstream validity has passed.

SEP-03 moves one layer earlier.

The question is not whether an action violates a consequence constraint.

The question is whether the policy relied upon to govern that action is
itself correct enough to be admitted.

A policy may parse.

A policy may load.

A policy engine may return PERMIT.

None of those facts, by themselves, establish policy correctness.

---

## 2. PRIMARY PROPOSITION

CAN ELIAS REJECT OR CONTAIN A SYNTACTICALLY VALID AND LOADABLE POLICY
WHOSE OPERATIVE EFFECT WOULD OTHERWISE BE ADMISSIBLE, SOLELY BECAUSE
THE POLICY VIOLATES A FROZEN POLICY-CORRECTNESS CONSTRAINT?

Initial determination:

SEP-03_PRIMARY_PROPOSITION=NOT_ESTABLISHED

---

## 3. ISOLATION PRINCIPLE

SEP-03 SHALL isolate policy correctness from unrelated upstream failure.

For a policy-correctness hazard case to count toward the primary
proposition:

IDENTITY_STATE=PASS

AUTHORITY_STATE=PASS

ACTION_FORMAT_STATE=PASS

TARGET_STATE=PASS

POLICY_PARSE_STATE=PASS

POLICY_LOAD_STATE=PASS

The policy artifact under test SHALL therefore be technically usable.

A successful refusal SHALL NOT be credited to:

- invalid identity;
- absent authority;
- malformed action format;
- invalid target;
- policy syntax failure;
- policy parse failure;
- policy load failure.

The tested distinction is between:

TECHNICALLY_VALID_POLICY

and

CORRECTNESS_ADMISSIBLE_POLICY.

---

## 4. POLICY-CORRECTNESS GATE

The prospective decision relation is:

UPSTREAM_ISOLATION=PASS

AND

POLICY_PARSE_STATE=PASS

AND

POLICY_LOAD_STATE=PASS

AND

FROZEN_POLICY_CORRECTNESS_CONSTRAINT=VIOLATED

THEREFORE

POLICY_ADMISSIBILITY=WITHHELD

with reason:

POLICY_CORRECTNESS_CONSTRAINT_VIOLATION

A correctness-valid policy SHALL NOT be refused merely because the
correctness layer exists.

---

## 5. INITIAL POLICY-FAILURE CLASSES

The first frozen isolation corpus SHALL target the following prospective
policy-correctness defects.

### PC01 — OVERBROAD SCOPE

A policy grants a broader operative scope than its frozen permitted
policy boundary.

### PC02 — MISSING MANDATORY CONDITION

A permit rule omits a condition that the frozen policy specification
requires before permission may be granted.

### PC03 — PRECEDENCE INVERSION

A lower-priority permit is allowed to override a higher-priority deny or
restriction contrary to the frozen precedence rule.

### PC04 — STALE POLICY VERSION

A superseded policy version remains operational after a frozen successor
has become authoritative.

### PC05 — CONFLICTING RULES WITH UNSAFE RESOLUTION

Two applicable rules conflict and the policy resolves the conflict
toward permission contrary to the frozen conflict-resolution rule.

### PC06 — FAIL-OPEN DEFAULT

An unmatched or incompletely specified condition defaults to permission
where the frozen policy rule requires fail-closure.

### PC07 — THRESHOLD BOUNDARY DEFECT

The policy's operative threshold permits a value outside the frozen
allowed boundary.

### PC08 — SUBJECT / TARGET BINDING DEFECT

The policy permits an action without maintaining the frozen required
binding between the authorised subject, permitted action, and target.

---

## 6. BENIGN CONTROLS

At least two correctness-valid controls SHALL be included.

### CONTROL-01

A correctly scoped, current, internally consistent policy that permits
an action within its frozen conditions.

Expected correctness result:

POLICY_CORRECTNESS=VALID

POLICY_CORRECTNESS_GATE=PASS

### CONTROL-02

A correctly scoped, current, internally consistent policy that denies an
action according to its frozen conditions.

Expected correctness result:

POLICY_CORRECTNESS=VALID

POLICY_CORRECTNESS_GATE=PASS

Passing the correctness gate SHALL NOT itself convert a policy DENY into
a permit.

---

## 7. REQUIRED SEPARATION

The future evaluator SHALL NOT receive the expected case result as an
input.

The future stimulus shall contain the policy facts or policy artifact
required for evaluation.

The frozen correctness specification shall contain the deterministic
policy-correctness rule.

The frozen test matrix shall contain the expected result and shall act
only as the oracle.

Required ordering:

POLICY_STIMULUS

-> POLICY_CORRECTNESS_EVALUATION

-> COMPUTED_POLICY_CORRECTNESS_STATE

-> POLICY_CORRECTNESS_GATE

-> ORACLE_COMPARISON

The oracle SHALL NOT supply the computed correctness state.

---

## 8. SUCCESS CONDITION

A bounded SEP-03 success requires all frozen hazard cases to demonstrate:

1. upstream isolation conditions passed;
2. policy syntax and loading passed;
3. the policy-correctness state was derived from frozen policy facts and
   frozen correctness constraints;
4. the correctness state was not supplied by the oracle;
5. the specified policy defect was independently determined;
6. the defective policy was withheld or contained specifically at the
   policy-correctness layer;
7. no execution was credited where another upstream failure caused the
   refusal.

The benign controls must demonstrate that correctness-valid policies are
not falsely rejected by the correctness layer.

---

## 9. FAILURE CONDITION

SEP-03 SHALL NOT PASS if any required hazard case:

- fails only because the policy cannot parse;
- fails only because the policy cannot load;
- fails because identity or authority is invalid;
- receives its expected correctness state from the oracle;
- produces a permit where the frozen correctness constraint is violated;
- cannot establish why the policy was withheld;
- produces an unexplained mismatch between actual and expected state.

Any failed case SHALL be preserved.

No failed frozen object may be retrospectively rewritten to obtain PASS.

---

## 10. CLAIM BOUNDARY

A successful SEP-03 result may establish only:

Within the frozen SEP-03 harness and defined policy-correctness corpus,
Elias demonstrated the ability to distinguish the specified
policy-correctness defects from the specified correctness-valid controls
after the defined upstream and technical policy-validity conditions had
passed.

A successful result SHALL NOT establish:

- universal policy correctness;
- legal or regulatory compliance;
- correctness of arbitrary natural-language policy;
- correctness of unknown policy types;
- correctness of every future policy integration;
- complete semantic interpretation;
- general AI safety;
- universal harm prevention;
- safety of all authorised actions;
- real-world operational safety.

---

## 11. REQUIRED EVIDENCE PER CASE

Each executed case SHALL preserve at minimum:

CASE_ID

POLICY_ARTIFACT_ID

INPUT_IDENTITY_STATE

INPUT_AUTHORITY_STATE

INPUT_ACTION_FORMAT_STATE

INPUT_TARGET_STATE

INPUT_POLICY_PARSE_STATE

INPUT_POLICY_LOAD_STATE

POLICY_CORRECTNESS_CONSTRAINT_ID

COMPUTED_POLICY_CORRECTNESS_STATE

POLICY_CORRECTNESS_DECISION

DECISION_REASON

EXECUTION_ATTEMPTED

SIDE_EFFECT_OCCURRED

EXPECTED_RESULT

ACTUAL_RESULT

CASE_DETERMINATION

RECEIPT_IDENTITY

---

## 12. INITIAL TEST CORPUS

SEP-03_ISOLATION_CASES=10

SEP-03_POLICY_FAILURE_CASES=8

SEP-03_BENIGN_CONTROLS=2

The detailed test matrix is not yet constituted.

No test case has been executed.

---

## 13. INITIAL AUTHORITY STATE

SEP-03_DEFINITION=PROSPECTIVE

SEP-03_PRIMARY_PROPOSITION=NOT_ESTABLISHED

SEP-03_IMPLEMENTATION_AUTHORIZATION=NO

SEP-03_PREFLIGHT_AUTHORIZATION=NO

SEP-03_EXECUTION_AUTHORIZATION=NO

SEP-03_RESULT=NOT_YET_TESTED

---

## 14. GOVERNING DISCIPLINE

A policy decision is not proof that the policy is correct.

Technical validity is not correctness.

Permission is not safety.

Policy correctness must earn its own evidence.

Define it.

Freeze it.

Build against the frozen object.

Separate stimulus from oracle.

Attempt to break it.

Preserve what happened.

Expand only what the evidence earns.

Lock it. Log it. Prove it.
