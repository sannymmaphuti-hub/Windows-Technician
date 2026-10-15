# Windows Technician V1.0 — Beta Testing Guide

## Purpose
Evaluate usability, reliability, compatibility and safety across representative
Windows environments. A successful test on one computer does not prove
universal compatibility.

## Record each test environment
Record Windows edition/version/build, application version, artifact SHA-256,
CPU architecture, available memory, account permissions, test date, scenario
and outcome. Avoid unnecessary personal or device-identifying information.

## Core acceptance scenarios

### Installation and launch
- Verify the executable and release manifest.
- Compare the artifact hash with a trusted expected value.
- Launch the application and confirm the interface appears.
- Confirm normal shutdown and expected runtime log entries.

### Runtime paths and logging
- Test the configured user-data location.
- Test executable relocation where supported.
- Verify log creation and access.
- Exercise inaccessible-directory handling where safe.

### Diagnostic quality
- Test normal, warning and incomplete-data conditions where reproducible.
- Check that findings have supporting evidence.
- Confirm missing information is not presented as certainty.
- Review explanation clarity and severity presentation.

### Operation safety
- Test ineligible and denied operations.
- Test missing authorization.
- Test execution and verification failures.
- Check recovery boundaries and retry limits.
- Use controlled fixtures or disposable test environments for risky scenarios.

### UI and accessibility
- Test different window sizes and display scaling.
- Inspect navigation, readability, progress, errors and confirmation prompts.
- Check keyboard access and visible focus where supported.

### Remote and fleet capabilities
- Test only capabilities available in the build.
- Verify target identity, case association and authorization.
- Exercise denied, failed and unavailable-target scenarios.
- Confirm fleet summaries do not themselves authorize remediation.

## Compatibility matrix
Use multiple representative environments where available:
- Standard-user account.
- Administrator account for supported privileged scenarios.
- Lower-resource computer.
- Different display scaling or window size.
- Relocated executable.
- Restricted diagnostic data source.
- Controlled failure and recovery environment.

Record the actual Windows versions tested. Do not claim support for an environment
merely because it resembles an environment that passed.

## Defect severity guidance
- Critical: security boundary bypass, unauthorized consequential operation,
  data loss or serious release-blocking failure.
- High: repeatable crash, major workflow failure or materially incorrect result.
- Medium: degraded functionality with a workaround.
- Low: cosmetic, minor usability or documentation issue.

Use impact and reproducible evidence to support severity.

## Beta report template
### Summary
One-sentence description.

### Environment
Windows version, application version and artifact hash.

### Preconditions and reproduction
Configuration, permissions and ordered reproduction steps.

### Expected and actual result
State the difference and include the exact error if available.

### Evidence and impact
Provide sanitized logs, relevant test output, severity and reproducibility.

## Exit criteria
- Required scenarios have recorded outcomes.
- Release-blocking safety and reliability defects are resolved.
- Supported environments are based on actual test evidence.
- Relevant regression tests pass.
- Known limitations and remaining risks are documented.
- Release integrity checks succeed.

Beta completion alone does not establish code-signature verification or universal
Windows compatibility.
