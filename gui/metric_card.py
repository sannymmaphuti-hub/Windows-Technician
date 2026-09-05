from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
)


class MetricCard(QFrame):
    def __init__(
        self,
        title,
        value,
        status,
        detail
    ):
        super().__init__()

        self.title = QLabel(title)
        self.value = QLabel(value)
        self.status = QLabel(status)
        self.detail = QLabel(detail)

        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        self.title.setFont(title_font)

        value_font = QFont()
        value_font.setPointSize(22)
        value_font.setBold(True)
        self.value.setFont(value_font)

        status_font = QFont()
        status_font.setPointSize(10)
        status_font.setBold(True)
        self.status.setFont(status_font)


        detail_font = QFont()
        detail_font.setPointSize(9)
        self.detail.setFont(detail_font)

        self.status_severity = None

        self.setObjectName("MetricCard")

        self.setStyleSheet(
            """
            QFrame#MetricCard {
                border-radius: 12px;
                padding: 16px;
            }
            """
        )

        layout = QVBoxLayout()

        layout.addWidget(self.title)
        layout.addWidget(self.value)
        layout.addWidget(self.status)
        layout.addWidget(self.detail)

        self.setLayout(layout)

    def set_data(
        self,
        title,
        value,
        status,
        detail,
        status_severity=None
    ):
        self.title.setText(title)
        self.value.setText(value)
        self.status.setText(status)
        self.detail.setText(detail)

        if status_severity is not None:
            self.set_status_severity(status_severity)

    def set_status_severity(self, severity):
        self.status_severity = severity

        self.setProperty(
            "statusSeverity",
            severity
        )

        self.style().unpolish(self)
        self.style().polish(self)