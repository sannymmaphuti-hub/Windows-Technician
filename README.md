# Windows Technician v0.6

Windows Technician is a Python-based Windows system diagnostic and troubleshooting engine designed to help users and technicians understand what is happening inside a Windows system.

The system collects diagnostic evidence, analyzes system behavior, identifies potential problems, determines probable root causes, explains diagnostic outcomes, and provides structured recommendations.

Version 0.6 extends the diagnostic architecture into a structured intelligence and controlled-remediation system. The v0.6 architecture connects diagnostic evidence, observations, signals, correlations, findings, root-cause reasoning, explanations, recommendations, case-level decisions, remediation boundaries, verification, and technician-facing evidence.

---

## Features

### System Diagnostics

Windows Technician can collect and analyze information relating to:

* CPU
* Memory
* GPU
* Network
* Storage
* Processes
* Services
* General system information

### Diagnostic Intelligence

The diagnostic engine supports:

* Process intelligence
* Memory intelligence
* Memory temporal analysis
* Memory trend analysis
* Diagnostic findings
* Finding relationships
* Correlation analysis
* Confidence evaluation
* Root-cause candidate detection
* Root-cause evaluation
* Primary root-cause selection
* Issue prioritization
* Explanations
* Recommendations
* Audience-aware explanations and recommendations

### Diagnostic Architecture

The diagnostic architecture provides structured processing through:

* Diagnostic evidence
* Observations
* Signals
* Findings
* Correlations
* Root-cause candidates
* Root-cause analysis
* Confidence evaluation
* Explanations
* Recommendations
* Diagnostic cases
* Case decisions
* Diagnostic orchestration
* Application integration
* Reporting

### Remediation Architecture

Remediation is deliberately separated from diagnosis.

The remediation architecture provides:

* Recommendation eligibility
* Remediation decision boundaries
* Remediation action planning
* Authorization boundaries
* Operation catalog
* Operation selection
* Operation binding
* Execution state
* Failure handling
* Remediation results
* Verification
* Recovery and retry
* Audit trails
* Separation between diagnostic discovery and system modification

Diagnostic discovery does not automatically cause system changes.

---

## Architecture

The high-level v0.6 diagnostic intelligence flow is:

```text
Windows System
      ↓
Collectors
      ↓
Diagnostic Pipelines
      ↓
Evidence
      ↓
Observations
      ↓
Signals
      ↓
Correlations
      ↓
Findings
      ↓
Root-Cause Reasoning
      ↓
Explanations
      ↓
Recommendations
      ↓
Case Decision
      ↓
DiagnosticCase
      ↓
Technician / Application Surfaces
```

The remediation architecture is deliberately separated from diagnostic reasoning:

```text
Recommendation
      ↓
Remediation Decision Boundary
      ↓
Eligibility
      ↓
Remediation Adapter
      ↓
Action Planner
      ↓
Authorization
      ↓
Operation Binding
      ↓
Execution
      ↓
RemediationResult
      ↓
Verification
      ↓
Recovery / Retry when required
```

The architecture therefore separates:

1. Evidence collection
2. Diagnostic interpretation
3. Case construction
4. Explanation and recommendation
5. Remediation eligibility
6. Authorization
7. Execution
8. Verification
9. Recovery

---

## Project Structure

```text
Windows Technician v0.6/

│
├── application/
│   ├── app.py
│   ├── technician.py
│   ├── dashboard_view_model.py
│   └── diagnostic_view.py
│
├── gui/
│   ├── dashboard
│   ├── diagnostic cards
│   ├── diagnostic worker
│   ├── main window
│   ├── metric cards
│   ├── sidebar
│   └── styles
│
├── engine/
│   ├── diagnostic orchestration
│   ├── diagnostic cases and decisions
│   ├── evidence, findings, signals and correlations
│   ├── root-cause analysis and confidence
│   ├── recommendations and explanations
│   ├── observation and signal pipelines
│   ├── network diagnostic pipeline
│   ├── remediation architecture
│   ├── remediation verification
│   ├── reporting
│   ├── collectors/
│   │   ├── CPU
│   │   ├── GPU
│   │   ├── memory
│   │   ├── network
│   │   ├── process
│   │   └── storage
│   ├── intelligence/
│   │   ├── process intelligence
│   │   ├── memory intelligence
│   │   ├── memory temporal/trend intelligence
│   │   └── diagnostic intelligence
│   └── rules/
│       ├── CPU
│       ├── GPU
│       ├── memory
│       ├── network
│       ├── process
│       └── storage
│
├── diagnostics/
│   ├── CPU diagnostics
│   ├── memory diagnostics
│   ├── GPU diagnostics
│   ├── network diagnostics
│   ├── storage diagnostics
│   ├── process analysis
│   ├── system analysis
│   └── legacy diagnostic support
│
├── tests/
│   └── diagnostic, intelligence, network, remediation,
│       application, integration, recovery and regression tests
│
├── logs/
├── reports/
│
├── main.py
├── requirements.txt
├── requirements-dev.txt
├── SECURITY.md
├── README.md
└── .gitignore
```

---

## Diagnostic Case Architecture

The `DiagnosticCase` represents the structured result of a diagnostic run.

A case can contain:

* Evidence
* Findings
* Correlations
* Root causes
* Root-cause candidates
* Primary root cause
* Recommendations
* Diagnostic status
* Process intelligence
* Memory intelligence
* Memory history
* Memory trend intelligence
* Memory temporal intelligence
* Memory diagnostic intelligence

The case provides a stable boundary between diagnostic processing and higher application layers.

### Central Case Flow

`DiagnosticCase` is the central structured case boundary for v0.6 diagnostic intelligence.

The case allows higher-level reasoning and application surfaces to consume structured diagnostic information without reconstructing the diagnostic result from lower-level objects.

The case-level flow is:

```text
Evidence
    ↓
Observations
    ↓
Signals
    ↓
Correlations
    ↓
Findings
    ↓
Root-Cause Reasoning
    ↓
Explanations
    ↓
Recommendations
    ↓
Case Decision
    ↓
Technician / Application Surfaces
```

The case therefore acts as the structured hand-off point between diagnostic intelligence and application-level workflows.

---

## Diagnostic Orchestration

`DiagnosticOrchestrator` coordinates the diagnostic lifecycle.

It provides a boundary between the underlying diagnostic engine and the application layer.

The orchestrator:

1. Runs the diagnostic pipeline.
2. Receives the diagnostic result.
3. Constructs the diagnostic case.
4. Commits the successful result.
5. Preserves the previous successful case when a new diagnostic run fails.
6. Records failure state when execution fails.

This allows diagnostic execution and application-level case ownership to remain separated.

---

## Case Decision

`CaseDecision` evaluates the completed diagnostic case and determines the case-level diagnostic outcome.

The decision layer operates on the structured diagnostic case rather than directly controlling system operations.

Case decisions can therefore be consumed by application and technician workflows without giving the decision layer unrestricted authority over remediation execution.

---

## Observation and Signal Architecture

The observation and signal architecture provides the structured transition from collected evidence into diagnostic reasoning.

The flow is:

```text
Evidence
    ↓
Observation
    ↓
Signal
    ↓
Correlation
    ↓
Finding
    ↓
Root Cause
    ↓
Explanation
    ↓
Recommendation
```

### Observation

Observations represent structured information derived from collected system evidence.

### Signal

Signals represent meaningful diagnostic indicators derived from observations.

### Correlation

Correlations connect related observations, signals, evidence, or findings so that relationships between conditions can be represented explicitly.

### Finding

Findings represent structured diagnostic conclusions produced from the available evidence and relationships.

This separation allows diagnostic reasoning to operate on structured information instead of relying on unstructured text.

---

## Root-Cause Analysis

Root-cause analysis evaluates available diagnostic evidence to determine probable causes.

The system can:

* Identify root-cause candidates.
* Associate evidence with candidates.
* Evaluate candidates.
* Assign confidence.
* Rank candidates.
* Remove duplicate candidates.
* Select a primary root cause when sufficient evidence exists.
* Avoid unsupported root-cause conclusions when evidence is insufficient.

Root-cause reasoning remains evidence-based. The architecture does not require a root cause to be selected when the available evidence does not justify one.

---

## Explanation Architecture

The explanation layer translates structured diagnostic reasoning into understandable explanations.

The explanation layer operates after diagnostic reasoning rather than replacing it.

The architecture is:

```text
Diagnostic Evidence
      ↓
Findings
      ↓
Root-Cause Reasoning
      ↓
Explanation
      ↓
Recommendation
```

This keeps the distinction between:

* What the system observed
* What the system concluded
* Why the conclusion was reached
* What action is recommended

---

## Recommendation Intelligence

Recommendation generation is handled as a structured intelligence stage.

`RecommendationIntelligence` evaluates diagnostic findings and produces structured recommendation objects containing information such as:

* Recommendation type
* Category
* Priority
* Description
* Rationale

The recommendation layer connects diagnostic reasoning to controlled remediation without directly executing system-changing operations.

The v0.6 flow is:

```text
Finding
    ↓
RecommendationIntelligence
    ↓
Recommendation
    ↓
Case Decision / Explanation
    ↓
Remediation Decision Boundary
```

Recommendation generation does not itself:

* Authorize remediation
* Bind an operation
* Execute an operation
* Verify an operation

Those responsibilities belong to later remediation layers.

---

## Network Diagnostics

Windows Technician v0.6 includes a dedicated network diagnostic architecture.

The network diagnostic pipeline can evaluate conditions such as:

* Network adapter availability
* Adapter connectivity
* Gateway reachability
* DNS resolution
* Internet connectivity
* Local network failures
* Network-related correlations
* Network root-cause candidates
* Network recommendations
* Network diagnostic actions

The network diagnostic architecture maintains explicit boundaries between:

```text
Network Evidence
      ↓
Network Observations
      ↓
Network Signals
      ↓
Network Findings
      ↓
Network Correlations
      ↓
Network Root Cause
      ↓
Network Recommendation
      ↓
Controlled Remediation
```

---

## Remediation Architecture

Remediation is intentionally separated from diagnostic reasoning.

The system follows:

```text
Diagnostic Result
      ↓
Diagnostic Case
      ↓
Recommendation
      ↓
Decision Boundary
      ↓
Remediation Action
      ↓
Authorization
      ↓
Operation Binding
      ↓
Execution
      ↓
Verification
      ↓
Result / Audit Trail
```

A diagnostic recommendation does not automatically execute a system-changing operation.

The user or authorized technician remains responsible for approving corrective actions.

---

## Remediation Decision Boundary

Recommendation generation and remediation eligibility are separate responsibilities.

The remediation decision boundary determines whether a recommendation is eligible to enter remediation planning.

In the current v0.6 architecture, **HIGH-priority recommendations are eligible for the remediation path**.

MEDIUM and LOW recommendations remain diagnostic recommendations and do not automatically enter remediation planning.

The boundary is:

```text
Recommendation
      ↓
Remediation Decision Boundary
      ↓
Eligible / Ineligible
      ↓
Remediation Adapter
      ↓
Action Planner
      ↓
Authorization
      ↓
Execution
```

Eligibility does not authorize an operation.

This separation ensures that diagnostic intelligence cannot silently become system-changing authority.

---

## Remediation Execution

Eligible recommendations are adapted into the existing remediation architecture.

The remediation path separates:

* Recommendation
* Eligibility
* Action planning
* Authorization
* Operation binding
* Execution
* Result handling

Remediation actions begin in a non-executed state.

The system does not bind or execute remediation operations during ordinary diagnostic discovery.

Execution occurs only after the required authorization boundary has been satisfied.

---

## Remediation Verification

Remediation execution and verification use the structured `RemediationResult` contract.

The result carries information including:

* Action identifier
* Execution status
* Reason
* Verification information

The verification flow is:

```text
Remediation Action
      ↓
Execution
      ↓
RemediationResult
      ↓
Verification
      ↓
Verified / Not Verified
```

Verification compares the expected condition with the observed condition after execution.

A failed verification remains a failed verification. It is not silently converted into a successful remediation.

The verification result can then be consumed by the technician recovery workflow.

---

## Recovery and Retry

Recovery is represented as a controlled workflow cycle rather than an implicit retry.

The technician workflow can move through:

```text
Investigation
      ↓
Resolution Attempt
      ↓
Verification
      ↓
Resolved
```

or, when verification fails:

```text
Investigation
      ↓
Resolution Attempt
      ↓
Verification Failure
      ↓
Recovery / Reopen
      ↓
Re-investigation
      ↓
Remediation Attempt
      ↓
Verification
```

Recovery history remains available to the technician workflow and evidence surfaces.

This allows previous investigation, remediation, and verification attempts to remain part of the case history rather than being discarded when another attempt begins.

---

## Technician Architecture

`Technician` acts as the application service responsible for coordinating diagnostic and remediation workflows.

The technician architecture connects:

```text
DiagnosticCase
      ↓
Technician Workflow
      ↓
Case Summary
      ↓
Evidence
      ↓
Recommendations
      ↓
Remediation
      ↓
Verification
      ↓
Recovery History
```

The technician workflow maintains ownership of the operational lifecycle while the underlying engine remains responsible for diagnostic reasoning.

---

## Technician Case Summary

The technician case summary provides a structured overview of the current diagnostic case.

It can represent information such as:

* Case identity
* Diagnostic status
* Findings
* Root-cause information
* Recommendations
* Remediation state
* Verification state
* Recovery state

The summary provides a stable technician-facing representation without moving diagnostic reasoning into the GUI.

---

## Technician Evidence View

The technician evidence architecture provides a composed view of the diagnostic case.

`TechnicianEvidenceView` can expose:

* Case overview
* Evidence overview
* Findings summary
* Finding details
* Correlation details
* Root-cause details
* Recommendation details
* Recovery-cycle history
* Verification outcomes

The evidence view is read-oriented.

It presents structured diagnostic evidence and reasoning while preserving ownership boundaries between:

* Diagnostic intelligence
* Technician workflow
* Application services
* GUI presentation

The GUI therefore consumes technician-facing evidence instead of implementing the diagnostic reasoning itself.

---

## Recovery History

Recovery history preserves the sequence of technician workflow cycles.

A recovery cycle can contain information about:

* Previous investigation
* Resolution attempts
* Remediation attempts
* Verification outcomes
* Re-investigation
* Reopening
* Escalation where applicable

This provides historical context when a problem requires more than one diagnostic or remediation attempt.

---

## Compatibility Boundaries

v0.6 contains compatibility infrastructure for earlier architectural generations.

These boundaries are intentional. They allow the current architecture to coexist with existing contracts without forcing an unnecessary migration during the v0.6 release.

### RecommendationIntelligence and RecommendationEngine

`RecommendationIntelligence` is the current structured v0.6 recommendation layer.

`RecommendationEngine` remains as legacy compatibility infrastructure.

The two are intentionally not merged in v0.6 because they represent different architectural contracts.

The current intelligence layer produces structured recommendation objects suitable for the v0.6 case and decision architecture.

The legacy engine remains available where existing integrations depend on its earlier contract.

The compatibility boundary therefore looks like:

```text
Current v0.6 Architecture
        ↓
RecommendationIntelligence
        ↓
Structured Recommendation
        ↓
DiagnosticCase / Decision Boundary


Legacy Architecture
        ↓
RecommendationEngine
        ↓
Legacy Recommendation Contract
```

The presence of the legacy component does not mean that the current recommendation architecture is incomplete.

---

## Root-Cause Model Generations

The project also contains two root-cause model generations.

The newer model uses structured root-cause candidates containing explicit information such as:

* Cause type
* Category
* Explanation

The older model uses the earlier root-cause rule/analyzer architecture and can represent cause information through the legacy contract.

These models are intentionally not merged during v0.6.

The v0.6 architecture preserves the compatibility boundary instead of introducing an unnecessary migration that could destabilize already validated diagnostic and integration behavior.

The distinction is:

```text
Current Structured Root-Cause Model
        ↓
RootCauseCandidate
        ↓
Structured Cause Information


Legacy Root-Cause Model
        ↓
Legacy Rule / Analyzer Contract
        ↓
Earlier Cause Representation
```

The current user-facing language architecture does not depend on parsing legacy root-cause prose in order to function.

---

## Application Layer

The application layer provides the interface between the diagnostic engine and the user-facing application.

Important components include:

```text
application/

├── app.py
├── technician.py
├── dashboard_view_model.py
└── diagnostic_view.py
```

`Technician` acts as the application service responsible for coordinating diagnostic and remediation workflows.

The application layer communicates with the underlying diagnostic and remediation architecture without placing diagnostic reasoning inside the user interface.

---

## GUI Layer

The GUI layer provides the user-facing Windows application interface.

Important components include:

```text
gui/

├── dashboard.py
├── diagnostic_card.py
├── diagnostic_worker.py
├── main_window.py
├── metric_card.py
├── sidebar.py
└── styles.py
```

The GUI presents diagnostic information supplied by the application layer and does not contain the core diagnostic reasoning engine.

The separation allows the diagnostic engine and technician workflow to remain independently testable.

---

## Reporting

Windows Technician can generate structured diagnostic reports containing information such as:

* Diagnostic status
* Diagnostic case information
* Evidence
* Findings
* Correlations
* Root-cause analysis
* Root-cause candidates
* Primary root cause
* Explanations
* Recommendations
* Remediation information
* Verification information
* Audit information

The application layer can save diagnostic reports to the `reports/` directory.

Generated reports are treated as runtime artifacts and are excluded from source control.

---

## Engineering Principles

Windows Technician follows several architectural principles.

### Separation of Responsibilities

System collection, diagnostic reasoning, intelligence, orchestration, application integration, GUI presentation, technician workflow, and remediation execution are separated into distinct layers.

### Evidence-Based Diagnosis

Diagnostic conclusions should be based on collected evidence rather than unsupported assumptions.

### Structured Intelligence

Diagnostic reasoning is represented through structured objects rather than relying on unstructured text as the primary architecture.

### Controlled Remediation

Diagnostic recommendations do not automatically modify the user's system.

### Explicit Authorization

System-changing remediation operations require an explicit authorization boundary.

### Verification

A remediation operation is not considered successfully resolved merely because execution was attempted.

The resulting system condition must be evaluated through verification.

### Recovery Safety

Failed verification and unsuccessful remediation attempts remain explicit and can return the technician workflow to controlled investigation and recovery.

### Compatibility Preservation

Existing architectural generations are preserved where required rather than being merged solely for the purpose of architectural uniformity.

### Failure Safety

Failures during diagnostic or remediation processing should be represented explicitly and should not silently produce successful results.

### Test-Driven Development

Development follows a deliberate:

```text
TEST
  ↓
FAIL
  ↓
IMPLEMENT
  ↓
FOCUSED TEST
  ↓
PASS
  ↓
BROADER REGRESSION
```

workflow.

---

## Testing

The project contains a comprehensive automated test suite covering:

* Diagnostic collection
* Diagnostic pipelines
* Diagnostic cases
* Diagnostic decisions
* Diagnostic orchestration
* CPU diagnostics
* Memory diagnostics
* Process intelligence
* Storage diagnostics
* Network diagnostics
* Observation pipelines
* Signal processing
* Findings
* Correlations
* Root-cause analysis
* Confidence
* Recommendations
* Explanations
* Recommendation intelligence
* Remediation decision boundaries
* Remediation planning
* Authorization
* Operation binding
* Operation execution
* Remediation verification
* Recovery and retry
* Technician workflow
* Technician case summaries
* Technician evidence surfaces
* Application integration
* GUI integration
* Negative cases
* Performance and stability
* Full integration
* Regression testing

The current v0.6 full regression baseline is:

```text
4261 passed
```

The 4261-test baseline represents the validated state of the project entering the documentation stage.

The test architecture includes both isolated component coverage and cross-layer integration coverage.

### Negative Testing

Negative cases verify that invalid or unsafe transitions do not silently succeed.

Coverage includes areas such as:

* Invalid workflow transitions
* Invalid remediation states
* Ineligible remediation recommendations
* Failed verification
* Invalid recovery transitions
* Unsupported operations
* Missing or insufficient diagnostic evidence
* Compatibility boundary conditions

### Performance and Stability

Performance and stability validation is included as part of the v0.6 validation work.

The purpose is to ensure that the completed architecture remains usable under realistic diagnostic and integration execution rather than validating only isolated objects.

### Full Integration

The integration suite validates the movement of information through the major architecture boundaries:

```text
Diagnostic Engine
      ↓
DiagnosticCase
      ↓
Case Decision
      ↓
Technician
      ↓
Case Summary / Evidence
      ↓
Recommendation
      ↓
Remediation
      ↓
Verification
      ↓
Recovery
```

---

## Security

Windows Technician is designed as a diagnostic and troubleshooting system.

The system should not be treated as an unrestricted automated authority over the user's computer.

Diagnostic information should be reviewed before corrective actions are taken.

Remediation operations are separated from diagnostic discovery and are subject to authorization and execution boundaries.

A recommendation being generated does not by itself grant permission to modify the system.

See `SECURITY.md` for the project's security policy.

---

## Project Status

**Windows Technician v0.6 — Documentation**

The v0.6 architecture and validation work currently includes:

1. Architecture definition
2. Intelligence domain modelling
3. Observation and signal processing
4. Signal correlation
5. Finding construction
6. Root-cause reasoning
7. Explanation architecture
8. Diagnostic case integration
9. User-facing language
10. Technician evidence architecture
11. Recommendation intelligence
12. Remediation decision boundaries
13. Remediation verification
14. Intelligence negative testing
15. Performance and stability validation
16. Full integration validation
17. Code and test quality review
18. Documentation

The current full regression baseline is:

```text
4261 passed
```

The project is **not yet marked as a release candidate**.

The next stage is:

```text
Stage 54 — Release Candidate
```

followed by:

```text
Stage 55 — Release
```

Historical development remains preserved in Git history.

---

## Historical Development

Earlier development stages remain preserved in source control and Git history.

The project evolved through multiple diagnostic, intelligence, application, remediation, and integration stages before reaching the current v0.6 architecture.

Historical v0.5 work remains relevant to the project's development history and is not removed simply because the current architecture has advanced.

The current product identity is:

**Windows Technician v0.6**

The v0.6 documentation describes the architecture that currently exists rather than redesigning or replacing previously validated components.
