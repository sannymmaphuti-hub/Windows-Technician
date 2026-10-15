import pytest
import main


class FakeBootstrap:
    def __init__(self):
        self.started = False
        self.stop_calls = 0
        self.state = object()

    def start(self):
        self.started = True
        return object()

    def stop(self):
        self.stop_calls += 1


def test_start_application_stops_bootstrap_when_window_creation_fails(
    monkeypatch,
):
    qt_application = object()
    bootstrap = FakeBootstrap()

    monkeypatch.setattr(
        main,
        "create_application",
        lambda: (qt_application, bootstrap),
    )

    def fail_window_creation(application_state):
        raise RuntimeError("window creation failed")

    monkeypatch.setattr(
        main,
        "create_main_window",
        fail_window_creation,
    )

    with pytest.raises(
        RuntimeError,
        match="window creation failed",
    ):
        main.start_application()

    assert bootstrap.started is True
    assert bootstrap.stop_calls == 1


def test_start_application_stops_bootstrap_when_window_show_fails(
    monkeypatch,
):
    qt_application = object()
    bootstrap = FakeBootstrap()

    class FakeWindow:
        def show(self):
            raise RuntimeError("window display failed")

    monkeypatch.setattr(
        main,
        "create_application",
        lambda: (qt_application, bootstrap),
    )
    monkeypatch.setattr(
        main,
        "create_main_window",
        lambda application_state: FakeWindow(),
    )

    with pytest.raises(
        RuntimeError,
        match="window display failed",
    ):
        main.start_application()

    assert bootstrap.started is True
    assert bootstrap.stop_calls == 1