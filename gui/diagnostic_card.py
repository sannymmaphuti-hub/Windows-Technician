from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
)


class DiagnosticCard(QFrame):
    def __init__(
        self,
        title,
        content,
        severity="info",
    ):
        super().__init__()

        self.title = QLabel(title)
        self.content = QLabel(content)
        self.severity = severity

        self.setObjectName("DiagnosticCard")

        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        self.title.setFont(title_font)

        content_font = QFont()
        content_font.setPointSize(13)
        content_font.setBold(True)
        self.content.setFont(content_font)

        self.setStyleSheet(
            """
            QFrame#DiagnosticCard {
                border-radius: 12px;
                padding: 16px;
            }
            """
        )

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.content)

        self.setLayout(layout)

        self.set_status_severity(severity)

    def set_status_severity(self, severity):
        self.severity = severity

        self.setProperty(
            "statusSeverity",
            severity
        )

        self.style().unpolish(self)
        self.style().polish(self)