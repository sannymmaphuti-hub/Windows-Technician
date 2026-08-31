# Windows Technician v0.3

Windows Technician is a Python-based Windows system diagnostic and troubleshooting engine designed to collect system evidence, analyze system health, identify diagnostic findings, evaluate relationships between findings, determine probable root causes, prioritize issues, provide actionable recommendations, and produce structured diagnostic reports.

Version 0.3 builds on the diagnostic and intelligence foundation established in v0.2 by introducing a structured diagnostic case architecture and orchestration layer.

## Features

### System Diagnostics

* CPU diagnostics
* Memory diagnostics
* GPU diagnostics
* Network diagnostics
* Storage diagnostics
* Process analysis
* Service and system analysis

### Diagnostic Intelligence

* Process intelligence
* Process temporal analysis
* Memory intelligence
* Memory trend analysis
* Memory temporal analysis
* Memory diagnostic intelligence
* Cross-diagnostic correlation
* Confidence scoring
* Root-cause analysis
* Root-cause candidate evaluation
* Primary root-cause selection
* Issue prioritization
* Recommendation generation

### v0.3 Diagnostic Architecture

* Structured diagnostic cases
* Diagnostic orchestration
* Case decision evaluation
* Evidence management
* Finding management
* Correlation management
* Root-cause candidate management
* Recommendation management
* Diagnostic status tracking
* Application-layer integration
* Structured case reporting

### Engineering

* Automated test suite
* Production diagnostic pipeline
* Diagnostic logging
* Modular architecture
* Separation between diagnostic collection, analysis, intelligence, orchestration, and application layers

## Diagnostic Architecture

Windows Technician v0.3 uses a layered diagnostic architecture in which the existing diagnostic systems feed into a structured diagnostic case.

```text
System
   |
Collectors
   |
Diagnostic Pipelines
   |
Rules
   |
Evidence
   |
Intelligence
   |
Analysis
   |
Confidence
   |
Correlation
   |
Root-Cause Analysis
   |
Case Decision
   |
DiagnosticCase
   |
DiagnosticOrchestrator
   |
Technician
   |
TechnicianApp
   |
Diagnostic Report
```

## v0.3 Diagnostic Case Architecture

The central architectural addition in v0.3 is the `DiagnosticCase`.

A diagnostic case provides a structured representation of the information produced during a diagnostic run.

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

This provides a consistent structure for passing diagnostic information between the diagnostic engine, orchestration layer, application layer, and reporting system.

## Diagnostic Orchestration

`DiagnosticOrchestrator` coordinates the diagnostic pipeline and converts the resulting diagnostic information into a structured `DiagnosticCase`.

The orchestrator provides a boundary between the underlying diagnostic engine and the application layer.

```text
Diagnostic Engine
       |
       v
DiagnosticOrchestrator
       |
       v
DiagnosticCase
       |
       v
CaseDecision
       |
       v
Technician
       |
       v
TechnicianApp
```

This allows the diagnostic engine to remain focused on collecting and analyzing system information while the application layer works with a structured diagnostic case.

## Case Decision

`CaseDecision` evaluates the completed diagnostic case and determines the appropriate case-level decision based on the available diagnostic evidence and findings.

The decision layer helps prevent the application from relying only on individual diagnostic results when determining the overall state of a case.

## Root-Cause Analysis

Windows Technician evaluates relationships between diagnostic findings to produce probable root-cause candidates.

The system can:

* Identify candidate causes
* Associate evidence with candidates
* Assign confidence
* Assign confidence levels
* Rank candidates
* Remove duplicate candidates
* Select a primary root cause when sufficient evidence exists

The system is designed to avoid presenting an unsupported root cause when the available evidence is insufficient.

## Diagnostic Reporting

Version 0.3 includes structured diagnostic case reporting.

Reports can contain:

* Diagnostic status
* Findings
* Correlations
* Root-cause analysis
* Root-cause candidates
* Primary root cause
* Recommendations
* Diagnostic case information

The application can save the generated diagnostic report to the `reports/` directory.

## Application Layer

The application layer provides a higher-level interface to the diagnostic system.

```text
application/
â”œâ”€â”€ app.py
â””â”€â”€ technician.py
```

`Technician` provides the application service interface to the diagnostic orchestration system.

`TechnicianApp` provides the application entry point and exposes operations for:

* Running diagnostics
* Retrieving diagnostic status
* Retrieving the primary issue
* Generating reports
* Saving reports

## Project Structure

```text
Windows Technician v0.3 Project/
|
+-- application/
|   +-- app.py
|   +-- technician.py
|
+-- diagnostics/
|   +-- CPU diagnostics
|   +-- Memory diagnostics
|   +-- GPU diagnostics
|   +-- Network diagnostics
|   +-- Storage diagnostics
|   +-- Process analysis
|   +-- System analysis
|   +-- Correlation analysis
|   +-- Reporting
|
+-- engine/
|   +-- diagnostic_engine.py
|   +-- diagnostic_orchestrator.py
|   +-- diagnostic_case.py
|   +-- case_decision.py
|   +-- analyzer.py
|   +-- evidence.py
|   +-- evidence_builder.py
|   +-- confidence.py
|   +-- correlation_engine.py
|   +-- correlation_adapter.py
|   +-- root_cause.py
|   +-- root_cause_analyzer.py
|   +-- root_cause_engine.py
|   +-- recommendation_engine.py
|   +-- report.py
|   +-- production.py
|   |
|   +-- collectors/
|   +-- intelligence/
|   +-- rules/
|
+-- logs/
+-- reports/
+-- tests/
+-- .gitignore
+-- requirements.txt
+-- SECURITY.md
+-- README.md
```

## Testing

The project uses Pytest for automated validation.

The complete v0.3 test suite covers:

* Diagnostic components
* Diagnostic collectors
* Diagnostic pipelines
* Diagnostic rules
* Evidence construction
* Confidence evaluation
* Diagnostic intelligence
* Temporal intelligence
* Cross-diagnostic correlations
* Root-cause analysis
* Root-cause engine
* Diagnostic case behavior
* Diagnostic orchestration
* Case decisions
* Engine integration
* Application integration
* Diagnostic reporting
* Production behavior

The final validated test count will be recorded here after the v0.3 release validation is complete.

## Version 0.2

Version 0.2 established the diagnostic intelligence foundation of Windows Technician.

The v0.2 release remains preserved in source control and serves as the foundation from which v0.3 was developed.

Version 0.3 extends that foundation without replacing the underlying diagnostic capabilities.

## Project Status

**Windows Technician v0.3 â€” Release Preparation**

The v0.3 implementation is feature-complete and is currently undergoing final release cleanup and validation.

The final release process includes:

1. Source and documentation cleanup
2. Duplicate and obsolete-code review
3. Test-suite validation
4. Git history and working-tree review
5. v0.3 commit creation
6. v0.3 release tagging
7. GitHub synchronization
8. Project directory rename from `Windows Technician V0.2 Project` to `Windows Technician V0.3 Project`

No v0.4 development is part of this release process.
