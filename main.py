import sys

from PySide6.QtWidgets import QApplication

from application.app import TechnicianApp
from gui.main_window import TechnicianMainWindow


def main():
    application = QApplication(sys.argv)

    technician_app = TechnicianApp()

    window = TechnicianMainWindow(
        technician_app
    )

    window.show()

    return application.exec()


if __name__ == "__main__":
    sys.exit(main())
