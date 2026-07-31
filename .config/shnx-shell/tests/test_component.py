from shnx_shell.components.component import Component


def test_component_can_start_and_stop() -> None:
    component = Component()

    component.start()
    component.stop()
