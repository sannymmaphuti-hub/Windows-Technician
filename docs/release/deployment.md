# Deployment Guide

## Purpose

Describe the verified Windows Technician v0.9 production packaging lifecycle.

## Verified lifecycle

Build → Package → Validate → Install → Run → Upgrade → Run → Uninstall

## Packaging

Windows Technician v0.9 currently produces a Windows executable distribution using PyInstaller.

The production distribution uses an onedir layout containing:

- WindowsTechnician.exe
- `_internal`
- PySide6 runtime components
- required application dependencies

## Data preservation

Configuration, logs, and reports are outside the application payload and must survive application replacement and normal uninstallation.

## Upgrade

Upgrades replace the application payload while preserving user data.

Downgrades are rejected.

## Uninstallation

Normal uninstallation removes the application payload and application shortcuts.

Configuration, logs, and reports are preserved.

## Release rule

Only packaging behavior verified by the production test suite may be documented as supported release behavior.
