# Windows Technician v0.5

Windows Technician is a Python-based Windows system diagnostic and troubleshooting engine designed to help users and technicians understand what is happening inside a Windows system.

The system collects diagnostic evidence, analyzes system behavior, identifies potential problems, determines probable root causes, and provides structured recommendations.

Version 0.5 extends the diagnostic architecture with structured cases, orchestration, application integration, observation pipelines, network diagnostics, diagnostic intelligence, and controlled remediation boundaries.

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
* Recommendations
* Diagnostic cases
* Case decisions
* Diagnostic orchestration
* Application integration
* Reporting

### Remediation Architecture

Remediation is deliberately separated from diagnosis.

The remediation architecture provides:

* Remediation action planning
* Authorization boundaries
* Eligibility checks
* Operation catalog
* Operation selection
* Operation binding
* Execution state
* Failure handling
* Remediation results
* Verification
* Audit trails
* Separation between diagnostic discovery and system modification

Diagnostic discovery does not automatically cause system changes.

---

## Architecture

The high-level diagnostic flow is:

```text
Windows System
      ↓
Collectors
      ↓
Diagnostic Pipelines
      ↓
Rules
      ↓
Observations
      ↓
Signals
      ↓
Evidence
      ↓
Findings
      ↓
Intelligence
      ↓
Correlation
      ↓
Root-Cause Analysis
      ↓
Confidence
      ↓
Case Decision
      ↓
DiagnosticCase
      ↓
DiagnosticOrchestrator
      ↓
Technician
      ↓
TechnicianApp
      ↓
Diagnostic Report
```

The remediation boundary is:

```text
Diagnosis
    ↓
Diagnostic Case
    ↓
Remediation Actions
    ↓
Authorization
    ↓
Operation Selection
    ↓
Operation Binding
    ↓
Execution
    ↓
Verification
    ↓
Result / Audit Trail
```

---

## Project Structure

```text
Windows Technician v0.5/
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
│       application, integration and regression tests
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

---

## Case Decision

`CaseDecision` evaluates the completed diagnostic case and determines the case-level diagnostic outcome.

The decision layer operates on the structured diagnostic case rather than directly controlling system operations.

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

---

## Observation Pipeline

The observation pipeline provides a structured path from collected system evidence toward higher-level diagnostic reasoning.

The pipeline supports:

```text
Evidence
   ↓
Observation
   ↓
Signal
   ↓
Finding
   ↓
Correlation
   ↓
Root Cause
   ↓
Recommendation
```

Observation builders translate collected system information into structured observations that can be processed by downstream diagnostic intelligence.

---

## Network Diagnostics

Windows Technician v0.5 includes a dedicated network diagnostic architecture.

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

The network diagnostic architecture maintains explicit boundaries between evidence collection, diagnosis, decision-making, recommendations, and remediation operations.

---

## Remediation Architecture

Remediation is intentionally separated from diagnostic reasoning.

The system follows:

```text
Diagnostic Result
      ↓
Diagnostic Case
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
Audit Trail
```

A diagnostic recommendation does not automatically execute a system-changing operation.

The user or authorized technician remains responsible for approving corrective actions.

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
* Recommendations
* Remediation information
* Audit information

The application layer can save diagnostic reports to the `reports/` directory.

Generated reports are treated as runtime artifacts and are excluded from source control.

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

---

## Engineering Principles

Windows Technician follows several architectural principles:

### Separation of Responsibilities

System collection, diagnostic reasoning, intelligence, orchestration, application integration, GUI presentation, and remediation execution are separated into distinct layers.

### Evidence-Based Diagnosis

Diagnostic conclusions should be based on collected evidence rather than unsupported assumptions.

### Controlled Remediation

Diagnostic recommendations do not automatically modify the user's system.

### Explicit Authorization

System-changing remediation operations require an explicit authorization boundary.

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
* Remediation
* Authorization
* Operation binding
* Operation execution
* Audit trails
* Application integration
* GUI integration
* Regression testing

The v0.5 release verification suite currently contains **2337 passing tests**.

---

## Security

Windows Technician is designed as a diagnostic and troubleshooting system.

The system should not be treated as an unrestricted automated authority over the user's computer.

Diagnostic information should be reviewed before corrective actions are taken.

Remediation operations are separated from diagnostic discovery and are subject to authorization and execution boundaries.

See `SECURITY.md` for the project's security policy.

---

## Project Status

**Windows Technician v0.5 — Released**

The v0.5 implementation and validation work includes:

1. Source and documentation cleanup
2. Duplicate and obsolete-code review
3. Architecture review
4. Diagnostic architecture validation
5. Network diagnostic validation
6. Remediation boundary validation
7. Test-suite validation
8. Repository and working-tree review
9. Documentation review
10. Release verification
11. Final project-directory rename
12. v0.5 release commit
13. v0.5 release tagging
14. GitHub synchronization

Historical development remains preserved in Git history.

---

## Historical Development

Earlier development stages remain preserved in source control and Git history.

The current product identity is **Windows Technician v0.5**.
