from copy import deepcopy


class WindowsSystemEvidence:
    def __init__(
        self,
        computer_name="",
        operating_system="",
        os_version="",
        architecture="",
        processor="",
    ):
        values = {
            "computer_name": computer_name,
            "operating_system": operating_system,
            "os_version": os_version,
            "architecture": architecture,
            "processor": processor,
        }

        for field, value in values.items():
            if not isinstance(value, str):
                raise ValueError(
                    f"{field} must be a string."
                )

        self._values = deepcopy(values)

    @property
    def computer_name(self):
        return self._values["computer_name"]

    @property
    def operating_system(self):
        return self._values["operating_system"]

    @property
    def os_version(self):
        return self._values["os_version"]

    @property
    def architecture(self):
        return self._values["architecture"]

    @property
    def processor(self):
        return self._values["processor"]