from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QSizePolicy,
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

        self.setObjectName("DiagnosticCard")
        self.severity = severity

        # ----------------------------------------------------------
        # Card sizing
        # ----------------------------------------------------------

        self.setMinimumHeight(110)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        # ----------------------------------------------------------
        # Title
        # ----------------------------------------------------------

        self.title = QLabel(title)

        self.title.setWordWrap(True)
        self.title.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        self.title.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignTop
        )

        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        self.title.setFont(title_font)

        # ----------------------------------------------------------
        # Content
        # ----------------------------------------------------------

        self.content = QLabel(content)

        self.content.setWordWrap(True)
        self.content.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.content.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignTop
        )

        content_font = QFont()
        content_font.setPointSize(13)
        content_font.setBold(True)
        self.content.setFont(content_font)

        # ----------------------------------------------------------
        # Appearance
        # ----------------------------------------------------------

        self.setStyleSheet(
            """
            QFrame#DiagnosticCard {
                border-radius: 12px;
                padding: 16px;
            }
            """
        )

        # ----------------------------------------------------------
        # Layout
        # ----------------------------------------------------------

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            16,
            16,
            16,
        )

        layout.setSpacing(8)

        layout.addWidget(self.title)
        layout.addWidget(self.content, 1)

        # ----------------------------------------------------------
        # Severity
        # ----------------------------------------------------------

        self.set_status_severity(severity)

    def set_status_severity(self, severity):
        self.severity = severity

        self.setProperty(
            "statusSeverity",
            severity,
        )

        self.style().unpolish(self)
        self.style().polish(self)