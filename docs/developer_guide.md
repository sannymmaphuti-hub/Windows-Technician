# Windows Technician V1.0 — Developer Guide

## Repository map
- main.py: application entry point.
- engine/: diagnostic, reasoning, workflow, fleet, remote and reliability logic.
- ui/: user-interface components.
- packaging/: release pipeline, runtime paths and packaged logging.
- tests/: unit, integration, negative, safety and release tests.
- docs/: architecture, operational and release documentation.
- artifacts/: generated release outputs; follow repository release policy.

## Environment and tests
Use the project's configured Python environment and dependencies. Inspect the
current project configuration rather than assuming every Python installation
is equivalent.

Run focused tests while developing, for example:

    py -m pytest .\tests\test_release_build_pipeline.py -q --tb=short

Choose tests relevant to the component being changed. Run related integration
tests for boundary changes and the broader regression suite at meaningful
milestones. Report actual results; never claim unrun tests passed.

## Canonical architecture
The V1.0 reasoning and operation pipeline is:

Evidence -> Reasoning -> Recommendation -> Eligibility -> Decision ->
Authorization -> Execution -> Verification -> Recovery and History

Preserve each stage's responsibility. UI components must not bypass approved
operation boundaries. Remote and fleet integrations must preserve case,
workflow, authorization and verification contracts.

DiagnosticCase is the central diagnostic case model. Integrate new capabilities
with canonical models instead of creating duplicate case lifecycles or
representations of findings, recommendations and history.

## Safety and reliability
- Require eligibility and a decision before execution.
- Enforce authorization at the appropriate boundary.
- Verify observed outcomes.
- Avoid blind retries.
- Preserve failure and recovery history.
- Test denied, incomplete, unsupported and failure scenarios.
- Do not treat mocked behavior as proof of real Windows behavior.

## Runtime and packaging
Keep presentation separate from business decisions and privileged operations.
Use established runtime lifecycle, configuration, path and logging boundaries.
Source-relative paths must not be assumed to work in a frozen executable.

The release pipeline produces an executable and a SHA-256 manifest. Follow
docs/v1.0_packaging_release_contract.md. Hash integrity is not equivalent to
trusted publisher authentication.

## Change discipline
1. Read the implementation and related tests.
2. Identify canonical APIs and lifecycle boundaries.
3. Make a coherent, focused change.
4. Add meaningful positive, negative and integration coverage.
5. Run relevant tests.
6. Update documentation when contracts change.

Preserve unrelated working-tree changes. Do not reset, clean or overwrite
unrelated work during routine development.

## Documentation maintenance
Keep documentation aligned with verified implementation. Do not promise
unsupported functionality or document assumptions as established behavior.
