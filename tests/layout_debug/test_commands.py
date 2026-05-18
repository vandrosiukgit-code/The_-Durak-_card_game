from __future__ import annotations

import unittest
from typing import Callable

from tools.layout_debug.commands import LayoutDebugCommandTargets, LayoutDebugCommands


class LayoutDebugCommandsTests(unittest.TestCase):
    def test_handle_button_dispatches_regular_command(self) -> None:
        calls: list[str] = []
        buttons = _Buttons()
        commands = _commands(calls)
        targets = _targets(buttons, current_step=lambda: 10)

        handled = commands.handle_button(buttons.apply, targets)

        self.assertTrue(handled)
        self.assertEqual(calls, ["apply"])

    def test_handle_button_dispatches_control_command_with_current_step(self) -> None:
        calls: list[tuple[int, int, int, int]] = []
        buttons = _Buttons()
        commands = _commands([], nudge_calls=calls)
        targets = _targets(buttons, current_step=lambda: 7)

        handled = commands.handle_button(buttons.move_right, targets)

        self.assertTrue(handled)
        self.assertEqual(calls, [(7, 0, 0, 0)])

    def test_handle_button_dispatches_filter_with_button_ref(self) -> None:
        calls: list[tuple[str, object]] = []
        buttons = _Buttons()
        commands = _commands([], filter_calls=calls)
        targets = _targets(buttons, current_step=lambda: 10)

        handled = commands.handle_button(buttons.panel_filter, targets)

        self.assertTrue(handled)
        self.assertEqual(calls, [("panel", buttons.panel_filter)])

    def test_handle_button_returns_false_for_unknown_button(self) -> None:
        calls: list[str] = []
        buttons = _Buttons()
        commands = _commands(calls)
        targets = _targets(buttons, current_step=lambda: 10)

        handled = commands.handle_button(object(), targets)

        self.assertFalse(handled)
        self.assertEqual(calls, [])


class _Buttons:
    def __init__(self) -> None:
        self.apply = object()
        self.reset = object()
        self.copy_task = object()
        self.add_task = object()
        self.clean_task = object()
        self.dismiss = object()
        self.cancel = object()
        self.move_right = object()
        self.panel_filter = object()
        self.hitboxes = object()


def _commands(
    calls: list[str],
    nudge_calls: list[tuple[int, int, int, int]] | None = None,
    filter_calls: list[tuple[str, object]] | None = None,
) -> LayoutDebugCommands:
    def nudge(dx: int, dy: int, dw: int, dh: int) -> None:
        if nudge_calls is not None:
            nudge_calls.append((dx, dy, dw, dh))

    def toggle_filter(filter_id: str, button: object) -> None:
        if filter_calls is not None:
            filter_calls.append((filter_id, button))

    return LayoutDebugCommands(
        apply_session=lambda: calls.append("apply"),
        reset_session=lambda: calls.append("reset"),
        copy_task=lambda: calls.append("copy_task"),
        add_task=lambda: calls.append("add_task"),
        clean_task=lambda: calls.append("clean_task"),
        dismiss_object=lambda: calls.append("dismiss"),
        cancel_object=lambda: calls.append("cancel"),
        nudge_object=nudge,
        toggle_filter=toggle_filter,
        toggle_hitboxes=lambda: calls.append("hitboxes"),
    )


def _targets(buttons: _Buttons, current_step: Callable[[], int]) -> LayoutDebugCommandTargets:
    return LayoutDebugCommandTargets(
        apply_button=buttons.apply,
        reset_button=buttons.reset,
        copy_task_button=buttons.copy_task,
        add_task_button=buttons.add_task,
        clean_task_button=buttons.clean_task,
        dismiss_button=buttons.dismiss,
        cancel_button=buttons.cancel,
        control_buttons={buttons.move_right: (1, 0, 0, 0)},
        filter_buttons={"panel": buttons.panel_filter},
        hitboxes_button=buttons.hitboxes,
        current_step=current_step,
    )


if __name__ == "__main__":
    unittest.main()
