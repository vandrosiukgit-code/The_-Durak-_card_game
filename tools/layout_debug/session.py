from __future__ import annotations

import copy

from tools.layout_debug.models import safe_int


class LayoutSession:
    def __init__(self, layout: dict[str, dict]) -> None:
        self.layout = layout
        self.initial_layout = copy.deepcopy(layout)
        self.selected_object_snapshot: dict | None = None

    @property
    def dirty(self) -> bool:
        return self.layout != self.initial_layout

    def mark_applied(self) -> None:
        self.initial_layout = copy.deepcopy(self.layout)

    def entry(self, screen_id: str, object_id: str | None) -> dict | None:
        if object_id is None:
            return None
        screen_layout = self.layout.get(screen_id, {})
        if not isinstance(screen_layout, dict):
            return None
        entry = screen_layout.get(object_id)
        return entry if isinstance(entry, dict) else None

    def copy_entry(self, screen_id: str, object_id: str | None) -> dict | None:
        entry = self.entry(screen_id, object_id)
        return copy.deepcopy(entry) if entry is not None else None

    def snapshot_selected(self, screen_id: str, object_id: str | None) -> None:
        self.selected_object_snapshot = self.copy_entry(screen_id, object_id)

    def dismiss_selected(self, screen_id: str, object_id: str | None) -> None:
        self.snapshot_selected(screen_id, object_id)

    def cancel_selected(self, screen_id: str, object_id: str | None) -> bool:
        entry = self.entry(screen_id, object_id)
        if entry is None or self.selected_object_snapshot is None:
            return False
        entry.clear()
        entry.update(copy.deepcopy(self.selected_object_snapshot))
        return True

    def reset(self) -> None:
        self.layout.clear()
        self.layout.update(copy.deepcopy(self.initial_layout))

    def apply_field_change(
        self,
        screen_id: str,
        object_id: str | None,
        field_name: str,
        text: str,
        rect_x: int,
        rect_y: int,
        rect_width: int,
        rect_height: int,
    ) -> bool:
        entry = self.entry(screen_id, object_id)
        if entry is None:
            return False

        if field_name == "x":
            entry["delta_x"] = safe_int(entry.get("delta_x")) + safe_int(text, rect_x) - rect_x
        elif field_name == "y":
            entry["delta_y"] = safe_int(entry.get("delta_y")) + safe_int(text, rect_y) - rect_y
        elif field_name == "width":
            entry["width_delta"] = safe_int(entry.get("width_delta")) + safe_int(text, rect_width) - rect_width
        elif field_name == "height":
            entry["height_delta"] = safe_int(entry.get("height_delta")) + safe_int(text, rect_height) - rect_height
        elif field_name in {"delta_x", "delta_y", "width_delta", "height_delta", "font_size"}:
            entry[field_name] = safe_int(text)
        elif field_name in {"color", "font"}:
            entry[field_name] = text.strip()
        else:
            return False

        return True

    def nudge_selected(
        self,
        screen_id: str,
        object_id: str | None,
        dx: int = 0,
        dy: int = 0,
        dw: int = 0,
        dh: int = 0,
    ) -> bool:
        entry = self.entry(screen_id, object_id)
        if entry is None:
            return False
        if dx:
            entry["delta_x"] = safe_int(entry.get("delta_x")) + dx
        if dy:
            entry["delta_y"] = safe_int(entry.get("delta_y")) + dy
        if dw:
            entry["width_delta"] = safe_int(entry.get("width_delta")) + dw
        if dh:
            entry["height_delta"] = safe_int(entry.get("height_delta")) + dh
        return True

    def set_todo_text(self, screen_id: str, object_id: str | None, text: str) -> bool:
        entry = self.entry(screen_id, object_id)
        if entry is None:
            return False
        entry["todo_text"] = text
        return True
