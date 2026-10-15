# Windows Technician V1.0 — Technician Operations Guide

## 1. Canonical investigation pipeline
Evidence -> Reasoning -> Recommendation -> Eligibility -> Decision ->
Authorization -> Execution -> Verification -> Recovery and History

No UI, remote, fleet or proactive workflow may bypass these boundaries.

## 2. Evidence and findings
Evaluate what was observed, when it was observed, which machine and case it
belongs to, what supports the interpretation, and what remains unknown.

Missing or contradictory evidence must remain explicit. Do not turn an
incomplete observation into a certain conclusion.

## 3. DiagnosticCase and workflow
DiagnosticCase is the canonical diagnostic case model. Preserve the association
between case identity, evidence, findings, correlations, root-cause reasoning,
explanations, recommendations and operational history.

Remote and proactive work must integrate with the established case and
technician workflow instead of creating a parallel case lifecycle.

## 4. Recommendation and authorization
Recommendations describe possible actions; they do not authorize execution.

Before an operation:
1. Confirm the target machine and case.
2. Evaluate eligibility.
3. Evaluate the decision and applicable policy.
4. Obtain the required authorization.
5. Execute through the approved boundary.
6. Verify the actual outcome.
7. Record the result and relevant history.

If a required stage fails or cannot be evaluated, do not silently skip it.
Use least privilege and never treat a warning as permission to act.

## 5. Verification and recovery
Execution success does not prove the expected outcome occurred.
Verification must compare the expected result with observed evidence.

On failure, preserve the error, assess whether partial changes occurred, follow
the applicable recovery policy and verify the recovery outcome. Avoid blind or
unlimited retries. Preserve operation identity and history.

## 6. Remote and fleet operations
Verify target identity, case association, authorization and operation scope.
Fleet summaries and priorities are decision-support information, not blanket
authorization to remediate every machine.

Only describe remote or fleet capabilities as operationally available when
the installed build and its configuration support them.

## 7. Operational records
Preserve the operation requested, target and case, decision and authorization,
execution and verification outcomes, failures, recovery actions and timestamps.
Protect records and avoid logging secrets or unnecessary personal information.

## 8. Escalation
Escalate when evidence conflicts, the cause is uncertain, the action is
destructive, authorization is unclear, recovery is unverified, or the issue
exceeds the supported capabilities of the installed build.
