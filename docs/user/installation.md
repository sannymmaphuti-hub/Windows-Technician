# Windows Technician Installation, Upgrade and Uninstall Guide

## Purpose

This guide explains the supported Windows Technician v0.9 application lifecycle:

**Install → Run → Upgrade → Run → Uninstall**

It also explains what application data is preserved during upgrades and normal uninstallation.

---

# 1. Before Installation

Windows Technician v0.9 is distributed as a Windows application package.

The production package contains the application executable and its runtime dependencies.

The primary executable is:

`WindowsTechnician.exe`

The application distribution uses an onedir layout.

The executable is accompanied by an `_internal` directory containing required runtime components.

---

# 2. Installation

Installation places the Windows Technician application payload into the configured installation location.

The installation payload includes:

- `WindowsTechnician.exe`
- `_internal`
- Required application runtime components
- Required application resources

Installation does not treat the user's configuration, logs, or reports as part of the replaceable application payload.

---

# 3. Application Data

Windows Technician maintains persistent operational information separately from the application installation payload.

Important persistent information includes:

- Configuration
- Logs
- Reports
- Operational state
- Recovery information

This separation allows the application itself to be replaced without unnecessarily destroying user or operational data.

---

# 4. First Startup

After installation, launch:

`WindowsTechnician.exe`

The application initializes its production runtime and services before presenting the main interface.

Startup establishes the runtime environment required for:

- Configuration
- Diagnostics
- Intelligence
- Logging
- User interface
- Operational state
- Recovery

---

# 5. Configuration Preservation

Configuration is treated as persistent user/application data rather than replaceable application files.

A normal installation or upgrade must not overwrite existing user configuration unnecessarily.

This is especially important for settings controlling application behavior and safety.

For example, remediation authorization must not silently become enabled because the application was upgraded.

---

# 6. Upgrading Windows Technician

An upgrade replaces the application payload with the newer version.

The upgrade process is conceptually:

**Validate → Replace Application → Preserve Data → Start New Version**

The existing application files are replaced.

Persistent user data is preserved.

The supported upgrade boundary includes:

- Configuration preservation
- Log preservation
- Report preservation
- Application replacement
- New-version startup

---

# 7. Version Direction

Windows Technician does not treat downgrading as an ordinary upgrade.

An upgrade must move from an older application version to a newer application version.

A lower version must not silently replace a newer installed version through the normal upgrade path.

---

# 8. Upgrade Safety

The upgrade process should validate the replacement package before replacing the existing application payload.

This prevents an invalid package from unnecessarily destroying the currently installed application.

The application payload and persistent data are deliberately treated as separate concerns.

---

# 9. Running After an Upgrade

After an upgrade, launch:

`WindowsTechnician.exe`

The new application version should initialize normally while retaining the persistent information that existed before the upgrade.

Operational state and recovery information allow the runtime to identify abnormal previous application termination where applicable.

---

# 10. Uninstallation

Normal uninstallation removes the Windows Technician application.

This includes the application installation payload and application shortcuts.

Normal uninstallation does **not** remove persistent user/application data.

The default relationship is:

**Remove Application ≠ Remove User Data**

---

# 11. Data Preserved During Normal Uninstallation

The following information is preserved during normal uninstallation:

- Configuration
- Logs
- Reports

This allows a user or technician to retain important information even after the application itself has been removed.

---

# 12. User Data Protection

Windows Technician uses a conservative uninstall boundary.

Normal uninstallation must not silently delete user data.

If a future operation is designed to intentionally remove persistent data, that must be treated as a separate and explicit operation rather than being hidden inside ordinary uninstallation.

---

# 13. Shortcuts

Application shortcuts belong to the application installation.

Normal uninstallation removes application shortcuts associated with Windows Technician.

Persistent user data is not treated as shortcut data and remains protected.

---

# 14. Complete Lifecycle

The verified packaging lifecycle is:

**Build → Package → Validate → Install → Run → Upgrade → Run → Uninstall**

Each stage has a distinct responsibility.

### Build

Creates the production executable distribution.

### Package

Creates the distributable installation artifact.

### Validate

Checks that the generated package has the required structure and executable.

### Install

Places the application payload into an installation location.

### Run

Starts the installed application.

### Upgrade

Replaces the application payload while preserving persistent data.

### Run Again

Confirms that the upgraded application can start.

### Uninstall

Removes the application while preserving configuration, logs, and reports.

---

# 15. Troubleshooting Installation

## The executable does not start

Check that:

- `WindowsTechnician.exe` exists.
- The `_internal` directory exists beside the executable.
- The installation was completed successfully.
- The application logs are available.

Do not manually delete runtime files from the installation directory while troubleshooting.

## The application fails after an upgrade

Check:

1. Application logs.
2. Operational state.
3. Recovery information.
4. Configuration.
5. Whether the upgrade package was valid.

If the problem persists, reinstalling the application may be appropriate while preserving the persistent data.

## Configuration appears missing

Verify that the persistent configuration location still exists.

Do not immediately delete configuration files.

Configuration can contain important application settings and safety preferences.

---

# 16. Troubleshooting Uninstallation

If application files remain after an uninstall attempt:

1. Confirm Windows Technician is no longer running.
2. Check whether the application installation directory is still present.
3. Check application logs if available.
4. Do not delete configuration, logs, or reports simply to force the application directory to disappear.

Persistent data is deliberately protected from normal uninstallation.

---

# 17. Technician Notes

Technicians should distinguish between:

### Application payload

Files required to execute Windows Technician.

### Persistent operational data

Information that should survive application replacement.

### User configuration

Settings that influence application behavior.

### Diagnostic/reporting data

Information useful for understanding application and system behavior.

These categories must not be treated as one undifferentiated directory.

---

# 18. Safety Principle

The installation system follows a simple rule:

> Replace what belongs to the application. Preserve what belongs to the user and operational history.

This principle applies across installation, upgrade, and normal uninstallation.
