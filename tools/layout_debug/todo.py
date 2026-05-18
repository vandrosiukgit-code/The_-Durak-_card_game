from __future__ import annotations

from tools.layout_debug.models import LayoutObject


class TodoService:
    def __init__(self, layout_data: object, screen_ids: tuple[str, ...]) -> None:
        self.layout_data = layout_data
        self.screen_ids = screen_ids

    def items(self) -> list[LayoutObject]:
        items: list[LayoutObject] = []
        for screen_id in self.screen_ids:
            for layout_object in self.layout_data.objects_for_screen(screen_id):
                if layout_object.todo_text.strip():
                    items.append(layout_object)
        items.sort(key=lambda item: (item.screen_id, item.object_type, item.object_id))
        return items

    def selected_item(self, selected_path: str | None) -> LayoutObject | None:
        todo_items = self.items()
        if not todo_items:
            return None
        if selected_path is not None:
            for item in todo_items:
                if item.path == selected_path:
                    return item
        return todo_items[0]

    def sync_selected_path(
        self,
        selected_object: LayoutObject | None,
        selected_path: str | None,
    ) -> str | None:
        if selected_object is not None and selected_object.todo_text.strip():
            return selected_object.path
        selected_todo = self.selected_item(selected_path)
        return selected_todo.path if selected_todo is not None else None

    def selection_items(self) -> tuple[list[str], dict[str, str]]:
        todo_items = self.items()
        if not todo_items:
            return ["Нет созданных задач"], {}

        labels: list[str] = []
        paths_by_label: dict[str, str] = {}
        for item in todo_items:
            first_line = item.todo_text.strip().splitlines()[0] if item.todo_text.strip() else ""
            label = f"{item.path} | {first_line[:34]}"
            paths_by_label[label] = item.path
            labels.append(label)
        return labels, paths_by_label

    def selected_path_by_label(self, label: str, paths_by_label: dict[str, str]) -> str | None:
        return paths_by_label.get(label)


class TodoClipboardFormatter:
    def structured_text(self, todo_item: LayoutObject | None) -> str | None:
        if todo_item is None:
            return None
        return (
            "Layout Debug Tool task\n"
            f"Screen: {todo_item.screen_id}\n"
            f"Object: {todo_item.object_id}\n"
            f"Path: {todo_item.path}\n"
            f"Type: {todo_item.object_type}\n"
            "\n"
            "Task:\n"
            f"{todo_item.todo_text.strip()}"
        )
