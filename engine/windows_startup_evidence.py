# ==========================================
# Windows Technician v0.9
# WINDOWS STARTUP EVIDENCE
# ==========================================

from copy import deepcopy


class WindowsStartupEvidence:
    def __init__(self, items=None):
        if items is None:
            items = []

        if not isinstance(items, list):
            raise ValueError(
                "items must be a list."
            )

        self.items = deepcopy(items)

    @property
    def item_count(self):
        return len(self.items)

    def get_item(self, name):
        if not isinstance(name, str):
            return None

        normalized_name = name.strip()

        if not normalized_name:
            return None

        for item in self.items:
            if not isinstance(item, dict):
                continue

            item_name = item.get("name")

            if not isinstance(item_name, str):
                continue

            if (
                item_name.strip().lower()
                == normalized_name.lower()
            ):
                return deepcopy(item)

        return None