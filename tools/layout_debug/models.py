from __future__ import annotations

from dataclasses import dataclass


LayoutEntryData = dict[str, object]
ScreenLayoutData = dict[str, LayoutEntryData]
LayoutConfigData = dict[str, ScreenLayoutData]


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
    layout_screen_id: str
    layout_key: str
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
    def from_config_entry(
        cls,
        screen_id: str,
        object_id: str,
        entry: object,
        layout_screen_id: str | None = None,
    ) -> "LayoutObject":
        safe_entry = entry if isinstance(entry, dict) else {}
        resolved_layout_screen_id = layout_screen_id or screen_id
        return cls(
            screen_id=screen_id,
            object_id=object_id,
            path=f"{resolved_layout_screen_id}.{object_id}",
            layout_screen_id=resolved_layout_screen_id,
            layout_key=f"{resolved_layout_screen_id}.{object_id}",
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


@dataclass(frozen=True)
class ScreenLayoutModel:
    screen_id: str
    entries: ScreenLayoutData

    @classmethod
    def from_config_layout(cls, screen_id: str, screen_layout: object) -> "ScreenLayoutModel":
        entries: ScreenLayoutData = {}
        if isinstance(screen_layout, dict):
            for object_id, entry in screen_layout.items():
                entries[str(object_id)] = entry if isinstance(entry, dict) else {}
        return cls(screen_id=screen_id, entries=entries)

    def object_count(self) -> int:
        return len(self.entries)

    def objects(self, preview_screen_id: str | None = None) -> list[LayoutObject]:
        resolved_preview_screen_id = preview_screen_id or self.screen_id
        objects = [
            LayoutObject.from_config_entry(
                resolved_preview_screen_id,
                object_id,
                entry,
                layout_screen_id=self.screen_id,
            )
            for object_id, entry in self.entries.items()
        ]
        objects.sort(key=lambda item: (item.object_type, item.object_id))
        return objects


@dataclass
class SelectionState:
    current_screen_id: str
    selected_object_id: str | None = None
    hover_object_id: str | None = None
    selected_todo_path: str | None = None
