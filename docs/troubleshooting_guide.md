# Windows Technician V1.0 — Troubleshooting Guide

## Safe initial checks
1. Record the exact error and when it occurred.
2. Determine whether Windows or Windows Technician is affected.
3. Check whether the application is still running.
4. Inspect recent application logs.
5. Avoid repeated launches if the application repeatedly crashes.
6. Do not delete logs or application data as an initial troubleshooting step.

## Application does not start
Check that the executable exists, came from a trusted source, and is accessible
to your account. Check free disk space, Windows security notifications and
available logs. Do not disable security software to force startup.

## Application closes unexpectedly
Inspect the log for startup failures, exceptions and shutdown events. Record
the approximate failure time and reproduction steps.

A clean shutdown entry records a normal stop; it does not prove every feature
worked correctly.

## Application becomes unresponsive
Allow an active operation reasonable time to finish. Avoid terminating the
application while a consequential operation may be running unless continuing
poses a greater risk. If termination is necessary, record the circumstances
and check system state afterward.

## Diagnostic results are incomplete
Possible causes include unavailable data, permissions, timing, collector failure
or unsupported configurations. Missing observations do not establish that
the corresponding components are healthy.

## Recommendation is unavailable or denied
Eligibility failure, policy denial, missing authorization and unsupported
operations are different outcomes. Inspect the recorded explanation.
Never bypass eligibility or authorization controls.

## Remediation fails
Record the operation, failure and verification outcome. Assess possible partial
changes before recovery. Follow the applicable recovery policy and avoid
blindly repeating the operation.

## Logs cannot be found
The expected default packaged log path is:

%LOCALAPPDATA%\WindowsTechnician\logs\application.log

Runtime configuration may change the actual path. Inspect the resolved
user-data location before concluding that logging has failed.

## Relocation or deployment problems
Compare the executable's SHA-256 hash with the expected release manifest.
Launch from the intended location and verify startup, logging and normal
shutdown.

A matching hash establishes integrity against the manifest, not publisher
identity. Publisher authenticity requires an appropriate trusted signature.

## Bug reports
Include the application and Windows versions, reproduction steps, expected
and actual results, error details and sanitized logs. Do not include credentials,
tokens, private keys or unrelated personal information.
