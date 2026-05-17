from __future__ import annotations

from dataclasses import dataclass


def safe_int(value: object, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def safe_str(value: object, fallback: str = "") -> str:
    return value if isinstance(value, str) else fallback


@dataclass(frozen=True)
class LayoutObject:
    screen_id: str
    object_id: str
    path: str
    object_type: str
    x: int
    y: int
    width: int
    height: int
    delta_x: int
    delta_y: int
    width_delta: int
    height_delta: int
    color: str
    font: str
    font_size: int
    todo_text: str

    @classmethod
    def from_config_entry(cls, screen_id: str, object_id: str, entry: object) -> "LayoutObject":
        safe_entry = entry if isinstance(entry, dict) else {}
        return cls(
            screen_id=screen_id,
            object_id=object_id,
            path=f"{screen_id}.{object_id}",
            object_type=safe_str(safe_entry.get("type"), "block"),
            x=safe_int(safe_entry.get("x")),
            y=safe_int(safe_entry.get("y")),
            width=safe_int(safe_entry.get("width")),
            height=safe_int(safe_entry.get("height")),
            delta_x=safe_int(safe_entry.get("delta_x")),
            delta_y=safe_int(safe_entry.get("delta_y")),
            width_delta=safe_int(safe_entry.get("width_delta")),
            height_delta=safe_int(safe_entry.get("height_delta")),
            color=safe_str(safe_entry.get("color"), ""),
            font=safe_str(safe_entry.get("font"), ""),
            font_size=safe_int(safe_entry.get("font_size")),
            todo_text=safe_str(safe_entry.get("todo_text"), ""),
        )


@dataclass(frozen=True)
class TodoTask:
    screen_id: str
    object_id: str
    path: str
    object_type: str
    text: str

    @classmethod
    def from_layout_object(cls, layout_object: LayoutObject) -> "TodoTask":
        return cls(
            screen_id=layout_object.screen_id,
            object_id=layout_object.object_id,
            path=layout_object.path,
            object_type=layout_object.object_type,
            text=layout_object.todo_text,
        )


@dataclass
class SelectionState:
    current_screen_id: str
    selected_object_id: str | None = None
    hover_object_id: str | None = None
    selected_todo_path: str | None = None
