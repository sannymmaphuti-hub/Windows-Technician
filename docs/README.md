# Windows Technician Documentation

## Purpose

This documentation set describes Windows Technician v0.9 as a production Windows application.

The documentation is divided by audience so that user-facing guidance, technician workflows, system architecture, development guidance, and release operations remain clearly separated.

## Documentation map

| Area | Audience | Purpose |
|---|---|---|
| User | End users | Understand, install, use, and troubleshoot Windows Technician |
| Technician | Technicians | Operate diagnostics, intelligence, recommendations, remediation, and technician workflows |
| Architecture | Engineers and maintainers | Understand system boundaries, lifecycle, intelligence, packaging, and production architecture |
| Developer | Developers | Build, test, extend, and maintain the project |
| Release | Maintainers and release engineers | Build, validate, install, upgrade, uninstall, and distribute releases |

## Canonical documents

### User

- [User Guide](user/user_guide.md)
- [Installation](user/installation.md)
- [Troubleshooting](user/troubleshooting.md)

### Technician

- [Technician Guide](technician/technician_guide.md)

### Architecture

- [v0.9 Architecture](architecture/v0.9_architecture.md)

### Developer

- [Developer Guide](developer/developer_guide.md)

### Release

- [Deployment Guide](release/deployment.md)

## Documentation ownership

Documentation must follow the existing architecture rather than inventing parallel concepts.

The canonical system flow is:

Observation → Signal → Correlation → Finding → Root Cause → Explanation → Recommendation → Diagnostic Case

Remediation follows:

Eligibility → Decision → Authorization → Execution → Verification

Remote and proactive operations use the same canonical diagnostic and workflow boundaries.

## Versioning

This documentation describes Windows Technician v0.9.

Version-specific architectural changes must be recorded in the architecture documentation and reflected in the appropriate operational guides.

## Documentation rules

1. Do not duplicate architectural definitions across documents.
2. Link to the canonical definition instead.
3. User documentation must avoid implementation details unless they are necessary for safe operation.
4. Technician documentation may explain operational behavior and evidence.
5. Developer documentation may describe implementation boundaries and tests.
6. Release documentation must describe only verified packaging and deployment behavior.
7. Security and authorization behavior must never be described as optional when the implementation requires it.
