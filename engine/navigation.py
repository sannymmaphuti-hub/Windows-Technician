class NavigationModel:
    """
    Canonical navigation state for the application shell.

    Navigation identifies pages and the currently selected page.
    It does not perform page actions or application operations.
    """

    _PAGES = (
        "DASHBOARD",
        "MACHINES",
        "DIAGNOSTICS",
        "CASES",
        "REMEDIATION",
        "INTELLIGENCE",
        "SETTINGS",
    )

    def __init__(self, initial_page="DASHBOARD"):
        self.current_page = self._normalize_page(
            initial_page
        )

    @classmethod
    def pages(cls):
        return tuple(cls._PAGES)

    @classmethod
    def _normalize_page(cls, page):
        if not isinstance(page, str):
            raise ValueError(
                "page must be a supported string value."
            )

        normalized = page.strip().upper()

        if normalized not in cls._PAGES:
            raise ValueError(
                f"Unsupported page: {page!r}."
            )

        return normalized

    def navigate(self, page):
        self.current_page = self._normalize_page(
            page
        )

        return self.current_page

    def is_current(self, page):
        return (
            self.current_page
            == self._normalize_page(page)
        )

    def to_dict(self):
        return {
            "pages": list(self._PAGES),
            "current_page": self.current_page,
        }


class MainWindowController:
    """
    Application-shell controller.

    Coordinates application state and navigation without
    performing diagnostics, remediation, or execution.
    """

    def __init__(
        self,
        application_state,
        navigation=None,
    ):
        if application_state is None:
            raise ValueError(
                "application_state is required."
            )

        self.application_state = application_state
        self.navigation = (
            navigation
            if navigation is not None
            else NavigationModel()
        )

        self.visible = False

    def show(self):
        self.visible = True
        return self.visible

    def hide(self):
        self.visible = False
        return self.visible

    def navigate(self, page):
        return self.navigation.navigate(page)

    @property
    def current_page(self):
        return self.navigation.current_page

    def to_dict(self):
        return {
            "visible": self.visible,
            "current_page": self.current_page,
            "application": (
                self.application_state.to_dict()
            ),
        }
