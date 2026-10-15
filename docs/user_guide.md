# Windows Technician V1.0 — End-User Guide

## Purpose
Windows Technician helps users understand their Windows computer through
diagnostic evidence, findings, explanations and recommendations.

Its goal is to make technology easier to understand while protecting the
computer and preserving the user's authority over changes.

## Before you begin
- Run the application from a trusted location.
- Save important work before approving a system change.
- Read Windows security and permission prompts carefully.
- Do not disable security protections to make a diagnostic succeed.
- Use administrator privileges only when a supported operation requires them.

## Understanding diagnostics
A diagnostic result describes evidence available at a particular time.
A warning does not automatically prove a component is failing.

The intended reasoning flow is:

Evidence -> Signals -> Correlations -> Findings -> Root Causes ->
Explanations -> Recommendations

Evidence may be incomplete because of permissions, timing or system limitations.
Missing evidence must not be interpreted as proof that a component is healthy.

## Recommendations and remediation
A recommendation is not authorization to change the computer.

Before approving an operation:
1. Read what it proposes to do.
2. Understand its expected outcome and risks.
3. Confirm that it concerns the correct computer.
4. Save important work.
5. Decline changes you do not understand.

Operations must respect eligibility, decision, authorization, execution and
verification boundaries. A successful execution does not automatically prove
that the intended result was achieved.

## If something goes wrong
Record the exact error, when the problem began, recent system changes and
the steps already attempted. Consult the troubleshooting guide when the
application itself is not working.

Seek qualified assistance when the cause is uncertain or a proposed change
could damage data or interrupt important services.

## Privacy and logs
The packaged application's expected default log location is:

%LOCALAPPDATA%\WindowsTechnician\logs\application.log

Actual paths may depend on runtime configuration. Review logs before sharing
them because they may contain usernames, file paths, device details or other
sensitive information.

Do not assume that remote connectivity, cloud synchronization or centralized
storage is available unless the installed build explicitly supports it.

## Limitations
Diagnostics can be incomplete. Recommendations may require human judgment.
A finding is not necessarily a definitive root cause, and resolving one finding
does not prove that every computer problem has been resolved.

## When requesting support
Include the application version, Windows version, error message, reproduction
steps and relevant sanitized logs. Never share passwords, tokens or private keys.
