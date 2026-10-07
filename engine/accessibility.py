from PySide6.QtCore import Qt


class AccessibilityHelper:
    """
    Presentation-only accessibility helpers for Windows Technician.

    This component configures accessible metadata, keyboard focus,
    and dynamic accessible state for UI controls.

    It does not diagnose, reason, recommend, authorize, remediate,
    execute, retry, or verify.
    """

    @staticmethod
    def describe(widget, name, description=None):
        if widget is None:
            raise ValueError("widget is required.")

        if name is None or not str(name).strip():
            raise ValueError("accessible name is required.")

        widget.setAccessibleName(str(name))

        if description is not None:
            widget.setAccessibleDescription(str(description))

        return widget

    @staticmethod
    def make_focusable(widget):
        if widget is None:
            raise ValueError("widget is required.")

        widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        return widget

    @staticmethod
    def describe_and_focus(widget, name, description=None):
        AccessibilityHelper.describe(
            widget,
            name,
            description,
        )
        AccessibilityHelper.make_focusable(widget)
        return widget

    @staticmethod
    def set_dynamic_description(widget, description):
        if widget is None:
            raise ValueError("widget is required.")

        if description is None:
            raise ValueError("description is required.")

        widget.setAccessibleDescription(str(description))

        return widget

    @staticmethod
    def set_state(widget, name, description):
        if widget is None:
            raise ValueError("widget is required.")

        if name is None or not str(name).strip():
            raise ValueError("accessible name is required.")

        if description is None:
            raise ValueError("description is required.")

        widget.setAccessibleName(str(name))
        widget.setAccessibleDescription(str(description))

        return widget
