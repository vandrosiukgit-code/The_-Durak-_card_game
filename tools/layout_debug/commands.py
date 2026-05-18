from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class LayoutDebugCommandTargets:
    apply_button: object
    reset_button: object
    copy_task_button: object
    add_task_button: object
    clean_task_button: object
    dismiss_button: object
    cancel_button: object
    control_buttons: dict[object, tuple[int, int, int, int]]
    filter_buttons: dict[str, object]
    hitboxes_button: object
    current_step: Callable[[], int]


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

    def handle_button(self, ui_element: object, targets: LayoutDebugCommandTargets) -> bool:
        if ui_element == targets.apply_button:
            self.apply_session()
            return True
        if ui_element == targets.reset_button:
            self.reset_session()
            return True
        if ui_element == targets.copy_task_button:
            self.copy_task()
            return True
        if ui_element == targets.add_task_button:
            self.add_task()
            return True
        if ui_element == targets.clean_task_button:
            self.clean_task()
            return True
        if ui_element == targets.dismiss_button:
            self.dismiss_object()
            return True
        if ui_element == targets.cancel_button:
            self.cancel_object()
            return True
        if ui_element in targets.control_buttons:
            step = targets.current_step()
            dx, dy, dw, dh = targets.control_buttons[ui_element]
            self.nudge_object(dx * step, dy * step, dw * step, dh * step)
            return True
        for filter_id, button in targets.filter_buttons.items():
            if ui_element == button:
                self.toggle_filter(filter_id, button)
                return True
        if ui_element == targets.hitboxes_button:
            self.toggle_hitboxes()
            return True
        return False
