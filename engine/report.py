# ==========================================
# Windows Technician v0.6
# DIAGNOSTIC CASE REPORT
# ==========================================


def generate_case_report(case):

    report = []

    # ==========================================
    # REPORT HEADER
    # ==========================================

    report.append("==========================================")
    report.append("       Windows Technician v0.6")
    report.append("          DIAGNOSTIC REPORT")
    report.append("==========================================")
    report.append("")

    # ==========================================
    # DIAGNOSTIC CASE
    # ==========================================

    report.append("DIAGNOSTIC CASE")
    report.append("------------------------------------------")

    report.append(
        f"Status : {case.status}"
    )

    report.append("")

    # ==========================================
    # CASE STATUS
    # ==========================================

    report.append("DIAGNOSTIC STATUS")
    report.append("------------------------------------------")
    report.append(f"Status : {case.status}")
    # ==========================================
    # EVIDENCE
    # ==========================================

    report.append("DIAGNOSTIC EVIDENCE")
    report.append("------------------------------------------")

    if not case.evidence:

        report.append("No diagnostic evidence recorded.")

    else:

        _append_value(report, case.evidence)

    report.append("")

    # ==========================================
    # FINDINGS
    # ==========================================

    report.append("DIAGNOSTIC FINDINGS")
    report.append("------------------------------------------")

    if not case.findings:

        report.append("No diagnostic findings recorded.")

    else:

        for finding in case.findings:

            if isinstance(finding, dict):

                severity = finding.get("severity", "INFO")
                category = finding.get("category", "GENERAL")
                message = finding.get("message", str(finding))

                report.append(
                    f"[{severity}] {category} : {message}"
                )

            else:

                report.append(str(finding))

    report.append("")

    # ==========================================
    # CORRELATIONS
    # ==========================================

    report.append("CROSS-DIAGNOSTIC CORRELATIONS")
    report.append("------------------------------------------")

    if not case.correlations:

        report.append(
            "No cross-diagnostic relationships detected."
        )

    else:

        for correlation in case.correlations:

            if isinstance(correlation, dict):

                relationship = correlation.get(
                    "relationship",
                    "Unknown relationship"
                )

                message = correlation.get(
                    "message"
                )

                report.append(
                    f"Relationship : {relationship}"
                )

                if message is not None:

                    report.append(
                        f"Message : {message}"
                    )

            else:

                report.append(str(correlation))

    report.append("")

    # ==========================================
    # PROCESS INTELLIGENCE
    # ==========================================

    report.append("PROCESS INTELLIGENCE")
    report.append("------------------------------------------")

    if case.process_intelligence is None:

        report.append(
            "No process intelligence available."
        )

    else:

        _append_value(
            report,
            case.process_intelligence
        )

    report.append("")

    # ==========================================
    # MEMORY INTELLIGENCE
    # ==========================================

    report.append("MEMORY INTELLIGENCE")
    report.append("------------------------------------------")

    if case.memory_intelligence is None:

        report.append(
            "No memory intelligence available."
        )

    else:

        _append_value(
            report,
            case.memory_intelligence
        )

    report.append("")

    # ==========================================
    # MEMORY HISTORY
    # ==========================================

    report.append("MEMORY HISTORY")
    report.append("------------------------------------------")

    if not case.memory_history:

        report.append(
            "No memory history recorded."
        )

    else:

        report.append(
            "Samples : "
            + ", ".join(
                str(value)
                for value in case.memory_history
            )
        )

    report.append("")

    # ==========================================
    # MEMORY TREND INTELLIGENCE
    # ==========================================

    report.append("MEMORY TREND INTELLIGENCE")
    report.append("------------------------------------------")

    if case.memory_trend_intelligence is None:

        report.append(
            "No memory trend intelligence available."
        )

    else:

        _append_value(
            report,
            case.memory_trend_intelligence
        )

    report.append("")

    # ==========================================
    # MEMORY TEMPORAL INTELLIGENCE
    # ==========================================

    report.append("MEMORY TEMPORAL INTELLIGENCE")
    report.append("------------------------------------------")

    if case.memory_temporal_intelligence is None:

        report.append(
            "No memory temporal intelligence available."
        )

    else:

        _append_value(
            report,
            case.memory_temporal_intelligence
        )

    report.append("")

    # ==========================================
    # MEMORY DIAGNOSTIC INTELLIGENCE
    # ==========================================

    report.append("MEMORY DIAGNOSTIC INTELLIGENCE")
    report.append("------------------------------------------")

    if case.memory_diagnostic_intelligence is None:

        report.append(
            "No memory diagnostic intelligence available."
        )

    else:

        _append_value(
            report,
            case.memory_diagnostic_intelligence
        )

    report.append("")

    # ==========================================
    # ROOT CAUSES
    # ==========================================

    report.append("ROOT-CAUSE ANALYSIS")
    report.append("------------------------------------------")

    if not case.root_causes:

        report.append(
            "No root causes recorded."
        )

    else:

        for root_cause in case.root_causes:

            _append_value(
                report,
                root_cause
            )

            report.append("")

    # ==========================================
    # ROOT-CAUSE CANDIDATES
    # ==========================================

    report.append("ROOT-CAUSE CANDIDATES")
    report.append("------------------------------------------")

    if not case.root_cause_candidates:

        report.append(
            "No root-cause candidates identified."
        )

    else:

        for candidate in case.root_cause_candidates:

            _append_value(
                report,
                candidate
            )

            report.append("")

    # ==========================================
    # PRIMARY ROOT CAUSE
    # ==========================================

    report.append("PRIMARY ROOT CAUSE")
    report.append("------------------------------------------")

    if case.primary_root_cause is None:

        report.append(
            "No primary root cause identified."
        )

    else:

        _append_value(
            report,
            case.primary_root_cause
        )

    report.append("")

    # ==========================================
    # RECOMMENDATIONS
    # ==========================================

    report.append("SYSTEM RECOMMENDATIONS")
    report.append("------------------------------------------")

    if not case.recommendations:

        report.append(
            "No recommendations recorded."
        )

    else:

        for recommendation in case.recommendations:

            if isinstance(recommendation, dict):

                category = recommendation.get(
                    "category",
                    "GENERAL"
                )

                message = recommendation.get(
                    "recommendation",
                    str(recommendation)
                )

                report.append(
                    f"- [{category}] {message}"
                )

            else:

                report.append(
                    f"- {recommendation}"
                )

    report.append("")

    # ==========================================
    # REMEDIATION AUDIT
    # ==========================================

    report.append("REMEDIATION AUDIT")
    report.append("------------------------------------------")

    remediation_audit = getattr(
        case,
        "remediation_audit",
        None
    )

    if not remediation_audit:

        report.append(
            "No remediation audit records available."
        )

    else:

        for record in remediation_audit:

            if isinstance(record, dict):

                action_id = record.get(
                    "action_id",
                    "Unknown action"
                )

                execution_status = record.get(
                    "execution_status",
                    "UNKNOWN"
                )

                description = record.get(
                    "description"
                )

                authorization_status = record.get(
                    "authorization_status"
                )

                reason = record.get(
                    "reason"
                )

                verification_result = record.get(
                    "verification_result"
                )

                report.append(
                    f"Action : {action_id}"
                )

                report.append(
                    f"Execution : {execution_status}"
                )

                if description is not None:

                    report.append(
                        f"Description : {description}"
                    )

                if authorization_status is not None:

                    report.append(
                        f"Authorization : {authorization_status}"
                    )

                if reason is not None:

                    report.append(
                        f"Reason : {reason}"
                    )

                if verification_result is not None:

                    report.append(
                        "Verification :"
                    )

                    _append_value(
                        report,
                        verification_result
                    )

            else:

                report.append(
                    str(record)
                )

            report.append("")

    # ==========================================
    # REPORT FOOTER
    # ==========================================

    report.append("==========================================")
    report.append("END OF Windows Technician v0.6 REPORT")
    report.append("==========================================")

    return "\n".join(report)


def _append_value(report, value, prefix="    "):

    if isinstance(value, dict):

        for key, item in value.items():

            if isinstance(item, (dict, list, tuple)):

                report.append(
                    f"{prefix}{key} :"
                )

                _append_value(
                    report,
                    item,
                    prefix + "    "
                )

            else:

                report.append(
                    f"{prefix}{key} : {item}"
                )

    elif isinstance(value, (list, tuple)):

        for item in value:

            if isinstance(item, (dict, list, tuple)):

                _append_value(
                    report,
                    item,
                    prefix
                )

            else:

                report.append(
                    f"{prefix}{item}"
                )

    else:

        report.append(
            f"{prefix}{value}"
        )
