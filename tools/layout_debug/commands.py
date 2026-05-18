from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class LayoutDebugCommands:
    apply_session: Callable[[], None]
    reset_session: Callable[[], None]
    copy_task: Callable[[], None]
    add_task: Callable[[], None]
    clean_task: Callable[[], None]
    dismiss_object: Callable[[], None]
    cancel_object: Callable[[], None]
    nudge_object: Callable[[int, int, int, int], None]
    toggle_filter: Callable[[str, object], None]
    toggle_hitboxes: Callable[[], None]

    def handle_button(self, ui_element: object, shell: object) -> bool:
        if ui_element == shell.apply_button:
            self.apply_session()
            return True
        if ui_element == shell.reset_button:
            self.reset_session()
            return True
        if ui_element == shell.copy_task_button:
            self.copy_task()
            return True
        if ui_element == shell.add_task_button:
            self.add_task()
            return True
        if ui_element == shell.clean_task_button:
            self.clean_task()
            return True
        if ui_element == shell.dismiss_button:
            self.dismiss_object()
            return True
        if ui_element == shell.cancel_button:
            self.cancel_object()
            return True
        if ui_element in shell.control_buttons:
            step = shell._current_step()
            dx, dy, dw, dh = shell.control_buttons[ui_element]
            self.nudge_object(dx * step, dy * step, dw * step, dh * step)
            return True
        for filter_id, button in shell.filter_buttons.items():
            if ui_element == button:
                self.toggle_filter(filter_id, button)
                return True
        if ui_element == shell.hitboxes_button:
            self.toggle_hitboxes()
            return True
        return False
