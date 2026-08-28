# Windows Technician v0.2

Windows Technician is a Python-based Windows system diagnostic and troubleshooting engine designed to collect system evidence, identify potential problems, analyze diagnostic relationships, prioritize issues, identify probable root causes, and provide actionable recommendations.

## Features

* CPU diagnostics
* Memory diagnostics
* GPU diagnostics
* Network diagnostics
* Storage diagnostics
* Process analysis
* Process intelligence
* Process temporal analysis
* Memory intelligence
* Memory trend analysis
* Memory temporal analysis
* Memory diagnostic intelligence
* Evidence collection and building
* Confidence scoring
* Cross-diagnostic correlation
* Root-cause analysis
* Issue prioritization
* Recommendation generation
* Diagnostic report generation
* Diagnostic logging
* Automated test suite
* Production diagnostic pipeline

## Diagnostic Architecture

Windows Technician v0.2 follows a layered diagnostic architecture:

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
Issue Prioritization
   |
Recommendations
   |
Diagnostic Report
```

## v0.2 Intelligence

Version 0.2 extends the diagnostic foundation of the project by introducing higher-level diagnostic intelligence.

The system can analyze relationships between system-level resource pressure and process behavior rather than relying only on individual threshold checks.

Examples include:

* Identifying processes associated with elevated memory usage
* Tracking memory usage history
* Detecting memory usage trends
* Performing temporal memory analysis
* Evaluating memory diagnostic conditions
* Analyzing abnormal process behavior
* Correlating memory pressure with CPU process activity
* Producing probable root-cause candidates
* Selecting a primary root-cause candidate
* Assigning diagnostic severity and priority
* Generating recommendations based on diagnostic findings

## Project Structure

```text
Windows Technician V0.2 Project/
|
+-- application/
+-- diagnostics/
+-- engine/
|   +-- collectors/
|   +-- intelligence/
|   +-- rules/
+-- reports/
+-- logs/
+-- tests/
+-- .gitignore
+-- requirements.txt
+-- SECURITY.md
+-- README.md
```

## Testing

The project uses Pytest for automated testing.

Current validation:

```text
346 passed
0 failed
0 errors
```

The complete automated test suite covers the diagnostic components, intelligence systems, integrations, root-cause analysis, recommendation generation, reporting, and application layer.

## Project Status

**Windows Technician v0.2 - Development Complete**

The v0.2 diagnostic and intelligence architecture has successfully passed the complete automated test suite.

Future versions may introduce additional diagnostic intelligence, user-interface capabilities, expanded Windows diagnostics, and other production-oriented features.
