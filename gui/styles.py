APPLICATION_STYLE = """
QWidget {
    font-family: "Segoe UI";
}

QFrame[statusSeverity="healthy"] {
    border: 1px solid #22c55e;
}

QFrame[statusSeverity="warning"] {
    border: 1px solid #eab308;
}

QFrame[statusSeverity="critical"] {
    border: 1px solid #ef4444;
}

QFrame[statusSeverity="info"] {
    border: 1px solid #3b82f6;
}

QFrame#DashboardHeader {
    border-radius: 12px;
    padding: 16px;
}

QFrame#HealthSummary {
    border-radius: 12px;
    padding: 16px;
}

QFrame#DiagnosticContent {
    border-radius: 12px;
    padding: 16px;
}
"""