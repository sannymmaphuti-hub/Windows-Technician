from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget


class KeyboardNavigation:
    """
    Presentation-only keyboard navigation helper.

    This component establishes predictable keyboard focus order
    between existing interactive widgets.

    It does not diagnose, reason, recommend, authorize, remediate,
    execute, retry, or verify.
    """

    @staticmethod
    def interactive_widgets(root):
        """
        Return interactive descendants in their current Qt hierarchy order.

        Disabled widgets are excluded because they cannot currently
        participate in keyboard interaction.
        """
        if root is None:
            raise ValueError("root is required.")

        widgets = []

        for widget in root.findChildren(QWidget):
            if not widget.isEnabled():
                continue

            policy = widget.focusPolicy()

            if policy in (
                Qt.FocusPolicy.TabFocus,
                Qt.FocusPolicy.StrongFocus,
            ):
                widgets.append(widget)

        return widgets

    @staticmethod
    def set_tab_order(widgets):
        """
        Establish an explicit sequential tab order.

        Returns the number of links established.
        """
        if widgets is None:
            raise ValueError("widgets is required.")

        widgets = list(widgets)

        if not widgets:
            return 0

        for widget in widgets:
            if widget is None:
                raise ValueError("widgets cannot contain None.")

        for current, next_widget in zip(
            widgets,
            widgets[1:],
        ):
            QWidget.setTabOrder(
                current,
                next_widget,
            )

        return max(0, len(widgets) - 1)

    @staticmethod
    def focus_first(widgets):
        """
        Give keyboard focus to the first enabled widget.
        """
        if widgets is None:
            raise ValueError("widgets is required.")

        for widget in widgets:
            if widget is not None and widget.isEnabled():
                window = widget.window()

                if window is not None:
                    window.activateWindow()

                widget.setFocus(Qt.FocusReason.OtherFocusReason)

                return widget

        return None

    @staticmethod
    def configure(root, widgets=None):
        """
        Configure keyboard navigation for a root widget.

        If widgets are omitted, eligible interactive descendants
        are discovered automatically.
        """
        if root is None:
            raise ValueError("root is required.")

        if widgets is None:
            widgets = KeyboardNavigation.interactive_widgets(root)

        widgets = list(widgets)

        KeyboardNavigation.set_tab_order(widgets)

        return widgets
