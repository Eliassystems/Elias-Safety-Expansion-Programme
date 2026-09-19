# ELIAS SAFETY EXPANSION PROGRAMME

## SEP-01 — HAZARD COVERAGE DEFINITION v0.1

STATUS: PROSPECTIVE / NOT FROZEN
PROGRAMME: Elias Safety Expansion Programme
OBJECT: SEP-01 Hazard Coverage
VERSION: 0.1

---

## 1. PURPOSE

SEP-01 exists to define the classes of harmful consequence that the Elias Safety Expansion Programme will attempt to identify, distinguish, test, and govern.

SEP-01 does not establish that Elias can prevent these hazards.

SEP-01 does not establish complete hazard coverage.

SEP-01 establishes only the prospective hazard taxonomy and the rules under which later safety tests may be constituted.

---

## 2. BASELINE POSITION

At SEP-01 commencement:

GENERAL CONSEQUENCE SAFETY=NOT_ESTABLISHED

UNIVERSAL_AI_SAFETY=NOT_ESTABLISHED

COMPLETE_HAZARD_IDENTIFICATION=NOT_ESTABLISHED

HAZARD_PREVENTION=NOT_ESTABLISHED

HAZARD_CONTAINMENT=NOT_ESTABLISHED

HAZARD_RECOVERY=NOT_ESTABLISHED

A hazard class being identified SHALL NOT be treated as evidence that Elias can detect, prevent, contain, or recover from that hazard.

---

## 3. CORE HAZARD QUESTION

For any proposed action, Elias safety analysis must eventually be capable of asking:

WHAT UNACCEPTABLE CONSEQUENCE COULD OCCUR EVEN IF THE ACTION IS:

- correctly identified;
- correctly authorised;
- policy-permitted;
- technically executable;
- integrity-preserved;
- and successfully delivered?

SEP-01 begins by defining those consequence classes.

---

## 4. INITIAL HAZARD CLASSES

### H01 — HUMAN PHYSICAL HARM

Potential consequence involving:

- bodily injury;
- loss of life;
- unsafe physical actuation;
- hazardous machinery or environment interaction;
- unsafe medical or health-related consequence;
- physical-world escalation.

STATUS: HAZARD CLASS DEFINED ONLY

---

### H02 — DIGITAL / SYSTEM HARM

Potential consequence involving:

- corruption of systems;
- destructive modification;
- unauthorised technical state change;
- loss of system integrity;
- malware-like consequence;
- destructive automation;
- privilege misuse.

STATUS: HAZARD CLASS DEFINED ONLY

---

### H03 — DATA / PRIVACY HARM

Potential consequence involving:

- disclosure of protected information;
- unauthorised data access;
- excessive collection;
- improper retention;
- unintended inference;
- cross-boundary disclosure;
- irreversible privacy loss.

STATUS: HAZARD CLASS DEFINED ONLY

---

### H04 — FINANCIAL / ECONOMIC HARM

Potential consequence involving:

- unauthorised or unsafe transfer of value;
- financial loss;
- contractual exposure;
- destructive trading or purchasing action;
- irreversible economic consequence;
- resource depletion.

STATUS: HAZARD CLASS DEFINED ONLY

---

### H05 — AUTHORITY / CONSENT HARM

Potential consequence involving:

- action beyond legitimate human authority;
- invalid delegation;
- revoked consent;
- excessive delegated power;
- conflict between authorised actors;
- coercive or non-consensual consequence.

STATUS: HAZARD CLASS DEFINED ONLY

---

### H06 — INFORMATION / DECISION HARM

Potential consequence involving:

- materially false information driving action;
- fabricated evidence;
- misleading confidence;
- corrupted decision support;
- unsafe omission of relevant uncertainty;
- false representation of system state.

STATUS: HAZARD CLASS DEFINED ONLY

---

### H07 — AVAILABILITY / CONTINUITY HARM

Potential consequence involving:

- interruption of critical service;
- destructive shutdown;
- lockout;
- denial of required capability;
- continuity failure;
- unrecoverable operational state.

STATUS: HAZARD CLASS DEFINED ONLY

---

### H08 — ENVIRONMENTAL / CONTEXTUAL HARM

Potential consequence caused by:

- stale environment state;
- incomplete observation;
- contradictory data;
- changed real-world conditions;
- unknown external dependencies;
- context assumed valid when it is not.

STATUS: HAZARD CLASS DEFINED ONLY

---

### H09 — COMPOSITIONAL / CASCADING HARM

Potential consequence where:

- individually acceptable actions combine unsafely;
- one agent changes another agent's safety conditions;
- multiple tools create emergent risk;
- a safe local action creates unsafe downstream state;
- distributed execution produces cascading failure.

STATUS: HAZARD CLASS DEFINED ONLY

---

### H10 — HUMAN ERROR / MISUSE HARM

Potential consequence involving:

- legitimate operator mistake;
- excessive authority grant;
- mistaken approval;
- misunderstood consequence;
- unsafe emergency action;
- valid human instruction producing unacceptable harm.

STATUS: HAZARD CLASS DEFINED ONLY

---

### H11 — IRREVERSIBILITY / RECOVERY HARM

Potential consequence involving:

- irreversible state change;
- inability to roll back;
- unsafe partial completion;
- recovery causing additional harm;
- evidence loss during recovery;
- restoration to an incorrect state.

STATUS: HAZARD CLASS DEFINED ONLY

---

### H12 — LONG-DURATION / DRIFT HARM

Potential consequence arising from:

- accumulated state;
- repeated executions;
- model change;
- policy drift;
- configuration drift;
- dependency evolution;
- authority becoming stale over time.

STATUS: HAZARD CLASS DEFINED ONLY

---

## 5. HAZARD RECORD REQUIREMENTS

Every later SEP hazard object SHALL attempt to record:

HAZARD_ID

HAZARD_CLASS

TARGET_ACTION

EXPECTED_BENEFICIAL_OUTCOME

FORESEEABLE_HARM

AFFECTED_PARTY_OR_SYSTEM

PRECONDITIONS

TRIGGER_CONDITIONS

SEVERITY

REVERSIBILITY

DETECTABILITY

DEPENDENCIES

UNCERTAINTIES

EXISTING_CONTROL

CONTROL_GAP

TESTABILITY

EVIDENCE_REQUIRED

CURRENT_DETERMINATION

---

## 6. REQUIRED DETERMINATION STATES

Hazards may use determinations including:

IDENTIFIED

PLAUSIBLE

NOT_ESTABLISHED

TESTABLE

NOT_YET_TESTABLE

CONTROL_PRESENT

CONTROL_PARTIAL

CONTROL_ABSENT

PREVENTION_ESTABLISHED_WITHIN_SCOPE

CONTAINMENT_ESTABLISHED_WITHIN_SCOPE

RECOVERY_ESTABLISHED_WITHIN_SCOPE

FAILED

UNRESOLVED

A hazard SHALL NOT be silently removed because it produces an inconvenient result.

---

## 7. COVERAGE RULE

A hazard taxonomy is not complete merely because no additional hazard has yet been identified.

Therefore:

NO_NEW_HAZARD_FOUND

DOES NOT IMPLY

ALL_HAZARDS_IDENTIFIED

Complete or universal hazard coverage remains NOT ESTABLISHED unless independently justified by evidence capable of supporting that claim.

---

## 8. CROSS-CLASS RULE

A single action MAY belong to multiple hazard classes simultaneously.

Later testing SHALL permit:

H01 + H05

H02 + H07

H03 + H06

H08 + H09

or any other supported combination.

Hazards SHALL NOT be forced into one category where the consequence crosses boundaries.

---

## 9. FIRST SUCCESSOR TARGET

SEP-01 SHALL produce a bounded hazard corpus suitable for use by SEP-02.

SEP-02 will then test:

CAN A CORRECTLY AUTHORISED, POLICY-PERMITTED, TECHNICALLY VALID ACTION BE WITHHELD BECAUSE ITS CONSEQUENCE MATCHES A FROZEN UNACCEPTABLE HAZARD?

At SEP-01 commencement:

SEP-02_RESULT=NOT_YET_TESTED

---

## 10. NON-CLAIMS

SEP-01 SHALL NOT claim:

- that every hazard has been identified;
- that every identified hazard is detectable;
- that every detected hazard can be prevented;
- that every prevention mechanism is correct;
- that every harmful outcome is foreseeable;
- that all human values can be represented as safety constraints;
- that all environments are sufficiently observable;
- that safe local actions guarantee safe global outcomes;
- that absence of failure proves safety.

---

## 11. INITIAL DETERMINATION

SEP-01_HAZARD_TAXONOMY=PROSPECTIVE

HAZARD_CLASSES_DEFINED=12

COMPLETE_HAZARD_COVERAGE=NOT_ESTABLISHED

HAZARD_PREVENTION=NOT_ESTABLISHED

HAZARD_CONTAINMENT=NOT_ESTABLISHED

HAZARD_RECOVERY=NOT_ESTABLISHED

SEP-01_IMPLEMENTATION_AUTHORIZATION=NO

SEP-01_EXECUTION_AUTHORIZATION=NO

SEP-02_AUTHORIZATION=NO

---

## 12. GOVERNING DISCIPLINE

Identify the harm.

Define the condition.

Preserve uncertainty.

Test the control.

Preserve the failure.

Expand only what the evidence earns.

Lock it. Log it. Prove it.
