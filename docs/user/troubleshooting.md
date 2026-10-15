# Windows Technician Troubleshooting Guide

## Purpose

This guide helps users and technicians diagnose problems with Windows Technician itself.

It covers startup problems, crashes, recovery, configuration, diagnostics, remediation, logging, reports, installation, upgrades, uninstallation, and runtime problems.

This guide is intentionally separate from the Windows problems that Windows Technician diagnoses.

---

# 1. Troubleshooting Principle

Troubleshoot from the least destructive action to the most involved action.

The preferred sequence is:

**Observe → Collect Evidence → Understand → Act → Verify**

Do not immediately delete configuration, logs, reports, or application data.

---

# 2. Windows Technician Does Not Start

If `WindowsTechnician.exe` does not start:

1. Confirm that the executable exists.
2. Confirm that the `_internal` directory exists beside it.
3. Try starting the application again.
4. Check whether Windows reports a permission or security problem.
5. Check available application logs.
6. Check whether the application was recently upgraded.
7. If the problem began after an upgrade, investigate the upgrade before deleting persistent data.

Do not delete the application's persistent data as a first troubleshooting step.

---

# 3. Application Starts and Immediately Closes

An application that starts and immediately exits may have encountered a startup failure.

Check:

- Application logs
- Operational state
- Configuration
- Recent upgrade activity
- Runtime files
- Windows security or permission messages

If an abnormal previous shutdown is recorded, the next startup may enter a recovery-aware path.

Do not assume that reinstalling the application is the first or only solution.

---

# 4. Application Becomes Unresponsive

If Windows Technician stops responding:

1. Wait briefly to determine whether the operation completes.
2. Avoid repeatedly clicking the same action.
3. If the application remains unresponsive, close it using normal Windows controls.
4. Restart the application.
5. Check logs and operational state.
6. Determine whether the problem occurs consistently.

Repeatedly triggering an unresponsive operation can make diagnosis harder.

---

# 5. Unexpected Application Shutdown

If Windows Technician closes unexpectedly:

1. Restart the application.
2. Check whether recovery information is available.
3. Review application logs.
4. Check whether the shutdown occurred during diagnostics, remediation, packaging, or another operation.
5. Do not blindly repeat a remediation operation.

An unexpected shutdown is different from a normal application exit.

---

# 6. Recovery After an Interrupted Session

Windows Technician maintains operational state so that abnormal application termination can be detected.

When recovery is required, the application can use the previous operational state to establish a safe recovery context.

Recovery is not blind retry.

In particular:

> A failed operation must not automatically be executed again simply because it previously failed.

If remediation failed before the application stopped, investigate the previous operation before attempting another remediation.

---

# 7. Diagnostics Do Not Produce a Finding

A diagnostic investigation may not always produce a finding.

Possible reasons include:

- Insufficient evidence
- A condition that is not severe enough
- Observations that do not correlate into a meaningful problem
- A transient condition
- A problem requiring more information

Do not interpret the absence of a finding as proof that the computer has no possible problems.

Likewise, do not interpret an observation by itself as proof of a root cause.

---

# 8. A Finding Appears Unexpected

When a finding appears unexpected:

1. Read the explanation.
2. Review the supporting evidence.
3. Review related observations or signals if available.
4. Check the recommendation.
5. Determine whether the finding represents a current condition or historical evidence.
6. Seek technician assistance if the evidence is unclear.

The diagnostic chain is intended to connect evidence to conclusions rather than present unexplained warnings.

---

# 9. Recommendation Appears

A recommendation represents a proposed next step.

It is not automatically an authorization to modify the computer.

Before approving a remediation recommendation, confirm:

- What the action does.
- Why it is being proposed.
- What problem it is intended to address.
- Whether the action is reversible or has consequences.
- Whether technician assistance is appropriate.

---

# 10. Remediation Is Not Available

A recommendation may exist without an executable remediation.

This can happen when:

- The action is not eligible for automation.
- Authorization is unavailable.
- Additional evidence is required.
- The problem requires manual intervention.
- The action would be unsafe to automate.
- A technician is required.

This is expected behavior for some classes of Windows problems.

---

# 11. Remediation Fails

**Executed ≠ Verified:** A remediation operation is not considered successful until its outcome has been independently verified.

If remediation fails:

1. Read the failure information.
2. Check the diagnostic finding.
3. Check the recommendation.
4. Review available logs.
5. Check the verification result.
6. Determine whether the original problem remains.
7. Escalate to a technician if necessary.

Do not repeatedly execute the same remediation blindly.

The distinction between execution and verification is important:

**Executed ≠ Verified**

---

# 12. Remediation Executes but the Problem Remains

A remediation can execute successfully while the underlying problem remains.

This is why Windows Technician verifies remediation outcomes.

If the problem remains:

1. Review the verification result.
2. Review the new evidence.
3. Determine whether the original diagnosis is still supported.
4. Determine whether another cause has become more likely.
5. Do not assume that repeating the same action will solve the problem.

A new diagnostic investigation may be more appropriate.

---

# 13. Configuration Problems

If Windows Technician behaves unexpectedly:

1. Check whether configuration was recently changed.
2. Review the relevant settings.
3. Confirm that safety-related settings have not changed unexpectedly.
4. Check the application logs.
5. Restart the application after a deliberate configuration change.

Do not delete configuration files without first determining whether they contain important settings.

---

# 14. Configuration Is Missing After an Upgrade

Configuration is intended to survive application replacement.

If configuration appears missing:

1. Do not immediately recreate everything.
2. Confirm that the persistent configuration location exists.
3. Check whether the correct user environment is being used.
4. Review logs.
5. Check whether the upgrade completed successfully.

Persistent configuration should not be treated as disposable application files.

---

# 15. Logs Are Missing

If expected logs are unavailable:

1. Confirm that the application has started.
2. Check the runtime data location.
3. Check whether the application has permission to write there.
4. Check whether the problem occurred before logging was initialized.
5. Review Windows-level application information if necessary.

Do not create unrelated duplicate logging locations as a workaround.

---

# 16. Reports Are Missing

If a diagnostic report is unavailable:

1. Confirm that the relevant diagnostic operation completed.
2. Check the reports location.
3. Check application logs.
4. Check whether the application terminated before report persistence.
5. Repeat the diagnostic only when it is safe and appropriate.

---

# 17. Startup After an Unclean Shutdown

An unclean shutdown may leave operational state indicating that recovery is required.

This is different from ordinary startup.

The application should use the recovery context to determine how to safely resume operation.

Users should not attempt to manually edit operational state files unless instructed by a technician or support procedure.

---

# 18. Installation Problems

If installation fails:

1. Confirm that the installation package exists.
2. Confirm that the package is a valid Windows Technician package.
3. Confirm that the executable is present in the package.
4. Confirm that the `_internal` runtime directory is present.
5. Check Windows permissions.
6. Check available disk space.
7. Retry installation only after the underlying problem is understood.

Do not install files from an unverified or modified package.

---

# 19. Upgrade Problems

If an upgrade fails:

1. Do not repeatedly attempt the upgrade immediately.
2. Check whether the new package is valid.
3. Check application logs.
4. Check the existing installation.
5. Confirm that persistent configuration, logs, and reports remain intact.
6. Determine whether the failure occurred before or after application replacement.

An upgrade should validate its replacement package before replacing the existing application payload.

---

# 20. Application Works Before Upgrade but Not After Upgrade

If the application worked before an upgrade but fails afterward:

Check:

- New executable
- `_internal` runtime files
- Application logs
- Configuration
- Operational state
- Upgrade artifact
- Windows security restrictions

Do not delete persistent data simply because the upgraded application fails.

Persistent data may be required to diagnose the failure.

---

# 21. Uninstallation Problems

If uninstallation does not remove the application:

1. Confirm Windows Technician is not running.
2. Retry normal uninstallation.
3. Check whether application files are still in use.
4. Check whether shortcuts remain.
5. Review logs if available.

Normal uninstallation should remove the application payload and application shortcuts.

---

# 22. Configuration, Logs, or Reports Were Deleted Accidentally

Do not immediately reinstall or overwrite the application.

First determine:

- Which data was removed.
- Whether backups exist.
- Whether the application installation is still intact.
- Whether recovery information remains.
- Whether Windows recovery tools can restore the files.

Persistent operational data may contain information required for troubleshooting.

---rnrn## 23. Packaging Runtime Problems

The production Windows distribution uses an onedir structure.

The expected structure includes:

```text
WindowsTechnician/
â”œâ”€â”€ WindowsTechnician.exe
â””â”€â”€ _internal/

If the executable is present but _internal is missing or incomplete, the application package may be incomplete.

Do not copy arbitrary Python or Qt files into the distribution as a workaround. Use a validated production build.

24. When to Stop Troubleshooting

# 24. When to Stop Troubleshooting

Stop and escalate when:

The problem involves hardware.
Repeated remediation attempts would be unsafe.
Evidence is contradictory.
Configuration may be corrupted.
Persistent data may be at risk.
The application repeatedly crashes.
An upgrade leaves the application unusable.
A security or permission issue cannot be resolved safely.
You do not understand what an attempted remediation will change.

Stopping is a valid diagnostic decision.

25. Information to Give a Technician

When escalating a problem, provide as much useful evidence as possible:

What happened and what you expected.
When the problem began.
What action was being performed.
The displayed error or finding.
Relevant diagnostic information.
Application logs and diagnostic reports, after reviewing them for sensitive information.
Whether the application was recently installed or upgraded.
Whether the problem happens consistently.

Avoid deleting evidence before reporting the problem.

26. Troubleshooting Safety Rule

The most important rule is:

Do not destroy evidence while trying to diagnose the problem.

Prefer:

Observe → Collect Evidence → Understand → Act → Verify

over:

Delete → Reinstall → Retry → Hope

Windows Technician is designed around the first approach.
```

# 26. Troubleshooting Safety Rule

Follow the safe sequence: Observe ? Collect Evidence ? Understand ? Act ? Verify.

Never repeat remediation blindly or delete persistent data as a first response. Stop and escalate to a technician when the cause, risk, or outcome cannot be established. A remediation is complete only after its result has been independently verified.
