# Windows Technician Technician Guide

## Purpose

This guide describes the technician-facing workflow for Windows Technician.

It explains how a technician should move from an investigation through evidence, diagnosis, decision-making, authorization, remediation, verification, recovery, and case closure.

The technician workflow is evidence-driven and does not treat a recommendation as permission to modify a machine.

---

# 1. Technician Workflow

The canonical technician workflow is:

**Case → Evidence → Diagnosis → Decision → Authorization → Remediation → Verification → Recovery → Closure**

Each stage has a distinct responsibility.

A technician should not skip evidence or verification simply because a likely solution is already known.

---

# 2. Diagnostic Case

A `DiagnosticCase` is the central diagnostic object.

A case brings together the information required to understand a machine condition.

A case may contain:

- Observations
- Signals
- Correlations
- Findings
- Root causes
- Explanations
- Recommendations
- Evidence
- Remediation actions
- Verification information
- Case status
- Case origin

The case is the canonical diagnostic context.

Do not create a parallel case lifecycle for a new diagnostic capability.

---

# 3. Case Origin

Cases may originate from different operational contexts.

Examples include:

- Local diagnostics
- Remote diagnostics
- Proactive monitoring

Different origins do not create different diagnostic lifecycles.

Remote and proactive investigations should still enter the canonical case and workflow architecture.

---

# 4. Evidence First

Technicians should begin with evidence.

Useful evidence may include:

- System observations
- Process information
- Memory information
- Historical information
- Signals
- Correlations
- Diagnostic findings
- Root-cause candidates
- Application logs
- Verification results
- Recovery history

Evidence should be preserved before destructive actions are considered.

---

# 5. Diagnostic Reasoning Chain

Windows Technician uses a structured reasoning chain:

**Observation → Signal → Correlation → Finding → Root Cause → Explanation → Recommendation**

The purpose of this chain is to prevent isolated observations from being presented as unsupported conclusions.

An observation is evidence.

A finding is a diagnostic conclusion supported by evidence.

A root-cause candidate explains why the finding may exist.

An explanation communicates the reasoning.

A recommendation proposes an action.

---

# 6. Findings

A finding represents a meaningful diagnostic conclusion.

When reviewing a finding, the technician should determine:

1. What evidence supports it.
2. Which observations contributed to it.
3. Which signals or correlations connect the evidence.
4. Whether the finding is current or historical.
5. Whether the confidence is sufficient for further action.

Do not treat an isolated observation as a confirmed root cause.

---

# 7. Root-Cause Reasoning

Root-cause reasoning should remain evidence-based.

A root-cause candidate should identify:

- Cause type
- Category
- Explanation

The technician should be able to trace the candidate back to supporting diagnostic evidence.

If evidence is insufficient, the correct decision may be to collect more evidence rather than force a root cause.

---

# 8. Explanations

An explanation translates diagnostic reasoning into understandable language.

A technician should be able to answer:

- What was observed?
- Why does it matter?
- What evidence supports the finding?
- What is believed to be causing the condition?
- What should happen next?

An explanation should not invent evidence that was not collected.

---

# 9. Recommendations

A recommendation represents a proposed next action.

It is not authorization.

The technician should review:

- The intended action
- The reason for the recommendation
- The finding it addresses
- The expected outcome
- Potential consequences
- Whether the action is eligible for automation

A recommendation can legitimately result in no automated action.

---

# 10. Remediation Decision Boundary

Remediation must cross an explicit decision boundary.

The canonical sequence is:

**Eligibility → Decision → Authorization → Execution → Verification**

Diagnosis does not automatically authorize remediation.

The existence of a recommendation does not authorize execution.

The technician should make the decision using the available evidence and safety constraints.

---

# 11. Authorization

Authorization is separate from diagnosis.

A diagnostic system may identify an eligible remediation without executing it.

The technician or authorized user must explicitly authorize an action before execution.

An action may therefore exist in a state such as:

- Unauthorized
- Authorized
- Denied

Authorization should not be inferred from a diagnostic result.

---

# 12. Remediation Execution

When an authorized remediation is executed:

1. Confirm that the action is the intended action.
2. Confirm that authorization exists.
3. Execute through the appropriate remediation boundary.
4. Record the execution result.
5. Proceed to verification.

Do not execute remediation directly from diagnostic code.

Do not bypass authorization because the remediation appears safe.

---

# 13. Verification

Execution is not verification.

**Executed ≠ Verified**

After remediation, Windows Technician should determine whether the expected outcome actually occurred.

Verification should compare:

- Expected result
- Observed result
- Relevant evidence

A successful execution does not prove that the underlying problem has been resolved.

---

# 14. Remediation Failure

When remediation fails:

1. Preserve the failure information.
2. Review the original finding.
3. Review the recommendation.
4. Review execution information.
5. Review available logs.
6. Review verification information.
7. Determine whether the original diagnosis remains valid.
8. Decide whether additional evidence is required.

Do not blindly retry the same remediation.

---

# 15. Problem Remains After Remediation

A remediation may execute successfully while the problem remains.

In that situation:

1. Review verification.
2. Collect new evidence.
3. Re-evaluate the original finding.
4. Determine whether another cause is now more plausible.
5. Start a new diagnostic investigation when appropriate.

Do not treat repeated execution of the same action as a substitute for diagnosis.

---

# 16. Recovery

Recovery exists to safely handle interrupted or failed operational workflows.

Recovery should use:

- Previous operational state
- Recovery context
- Case history
- Previous operation information
- Available evidence

Recovery is not blind retry.

A failed operation must not automatically execute again merely because the application was interrupted.

---

# 17. Technician Workflow State

The technician workflow should provide a controlled case lifecycle.

The technician should understand the current workflow state before performing the next operation.

Examples of workflow concerns include:

- Investigation
- Decision
- Remediation
- Verification
- Recovery
- Closure

Do not manually force lifecycle transitions simply to make an operation available.

---

# 18. Remote Diagnostics

Remote diagnostics use the same canonical diagnostic architecture.

The conceptual chain is:

**Technician → RemoteSession → RemoteMachine → Diagnostic → Case → Decision → Remediation → Verification**

Remote operation must not bypass:

**Eligibility → Decision → Authorization → Execution → Verification**

Remote execution should remain subject to the same safety boundaries as local execution.

---

# 19. Proactive Cases

Proactive monitoring may identify a condition before a user reports a problem.

A proactive condition should still become a canonical diagnostic case.

The proactive workflow should use the existing diagnostic and technician workflow rather than creating an independent lifecycle.

The technician should review:

- Alert origin
- Supporting evidence
- Baseline information
- Findings
- Recommendations
- Historical context

---

# 20. Multi-Machine Operations

When working with multiple machines, keep machine identity and case identity distinct.

A technician should always know:

- Which machine is being investigated.
- Which case belongs to that machine.
- Which evidence belongs to that case.
- Which remediation belongs to that machine.
- Which verification result belongs to that remediation.

Do not mix evidence between machines.

Fleet-level information should support reasoning without destroying machine-level context.

---

# 21. Historical Intelligence

Historical information can help establish whether a condition is:

- New
- Persistent
- Recurring
- Improving
- Worsening
- Resolved

Historical evidence should be interpreted in context.

A historical observation should not automatically be treated as a current fault.

---

# 22. Technician Evidence Review

Before making a remediation decision, review the available evidence.

At minimum consider:

- Current observations
- Related signals
- Correlations
- Findings
- Root-cause candidates
- Explanation
- Recommendation
- Historical information
- Previous remediation attempts
- Verification results

If the evidence is insufficient, collect more evidence.

---

# 23. Case Closure

A case should only be closed when the technician has enough evidence to establish the outcome.

Closure should account for:

- Diagnostic conclusion
- Remediation status
- Verification result
- Remaining problems
- Recovery status
- Technician notes where appropriate

A case should not be considered resolved merely because a remediation executed successfully.

---

# 24. Escalation

Escalate when:

- Evidence is insufficient.
- Evidence is contradictory.
- Hardware intervention is required.
- A remediation is unsafe to automate.
- Authorization cannot be established.
- Verification fails.
- The problem remains unresolved.
- The machine is unstable.
- Security or permission boundaries prevent safe action.

Escalation is part of safe technician operation, not a failure of the diagnostic system.

---

# 25. Safety Rules

Technicians should follow these rules:

1. Preserve evidence.
2. Do not bypass authorization.
3. Do not execute unverified remediation.
4. Do not blindly retry failed actions.
5. Do not mix evidence between machines or cases.
6. Do not treat recommendations as authorization.
7. Do not treat execution as verification.
8. Do not force lifecycle transitions.
9. Prefer additional evidence when uncertainty is high.
10. Escalate when safe automation boundaries are exceeded.

The fundamental principle is:

**Understand before acting. Verify after acting.**

---

# 26. Technician Diagnostic Checklist

Before remediation:

- [ ] Correct machine identified.
- [ ] Correct case identified.
- [ ] Evidence reviewed.
- [ ] Finding understood.
- [ ] Root-cause reasoning reviewed.
- [ ] Recommendation understood.
- [ ] Eligibility established.
- [ ] Decision made.
- [ ] Authorization obtained.

After remediation:

- [ ] Execution result recorded.
- [ ] Verification performed.
- [ ] Expected result compared with observed result.
- [ ] Remaining problem evaluated.
- [ ] New evidence reviewed.
- [ ] Case state updated.
- [ ] Escalation performed if required.

---

# 27. Technician Boundary

The technician interface presents and operates on the canonical technician workflow.

The presentation layer must not independently:

- Diagnose
- Reason about root causes
- Create recommendations
- Authorize remediation
- Execute remediation
- Retry operations
- Verify remediation

Those responsibilities belong to the appropriate application services and domain architecture.

The technician UI should expose the system's decisions and evidence without creating a second diagnostic architecture.
