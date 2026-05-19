from __future__ import annotations

import html

from tools.layout_debug.models import LayoutObject
from tools.layout_debug.navigator_tree import NavigatorTree, NavigatorTreeBuilder, NavigatorTreeNode


class NavigatorViewFormatter:
    def __init__(self, tree_builder: NavigatorTreeBuilder | None = None) -> None:
        self.tree_builder = tree_builder or NavigatorTreeBuilder()

    def selection_items(
        self,
        screen_id: str,
        layout_objects: list[LayoutObject],
        selected_object_id: str | None,
        hover_object_id: str | None,
        focus_object_id: str | None = None,
    ) -> tuple[list[str | tuple[str, str]], dict[str, str]]:
        items: list[str | tuple[str, str]] = []
        object_ids_by_label: dict[str, str] = {}
        tree = self.tree_builder.build(screen_id, layout_objects)
        if focus_object_id is not None and focus_object_id in tree.nodes_by_object_id:
            items.append((f"Focus: {focus_object_id}", "#navigator_focus_status_item"))
            nodes = self._focus_nodes(tree, focus_object_id)
        else:
            nodes = tree.flatten()
        for node in nodes:
            layout_object = node.layout_object
            if layout_object is None:
                label = f"{'    ' * node.level}{node.object_id}"
                items.append((label, "#navigator_group_item"))
                continue
            status = ""
            if layout_object.todo_text:
                status += " todo"
            indent = "    " * node.level
            branch = "" if node.level == 0 or (node.parent is not None and node.parent.is_group) else "- "
            label = f"{indent}{branch}{layout_object.object_id}{status}"
            if layout_object.object_id == hover_object_id:
                item_object_id = "#navigator_root_hover_item" if node.level == 0 else "#navigator_child_hover_item"
            else:
                item_object_id = "#navigator_root_item" if node.level == 0 else "#navigator_child_item"
            items.append((label, item_object_id))
            object_ids_by_label[label] = layout_object.object_id
        return items, object_ids_by_label

    @staticmethod
    def _focus_nodes(tree: NavigatorTree, focus_object_id: str) -> list[NavigatorTreeNode]:
        path = tree.path_to(focus_object_id)
        descendants = tree.descendants_of(focus_object_id)
        return path + descendants

    def html(
        self,
        screen_id: str,
        layout_objects: list[LayoutObject],
        selected_object_id: str | None,
        hover_object_id: str | None,
    ) -> str:
        if not layout_objects:
            return (
                "<font face=consolas size=3>"
                f"<b>{html.escape(screen_id)}</b><br><br>"
                "Нет layout-объектов."
                "</font>"
            )

        lines = [
            "<font face=consolas size=3>",
            f"<b>{html.escape(screen_id)}</b>",
            f"{len(layout_objects)} objects",
            f"Selected: {html.escape(selected_object_id or '-')}",
            f"Hover: {html.escape(hover_object_id or '-')}",
            "",
        ]
        current_type: str | None = None
        for layout_object in layout_objects:
            if layout_object.object_type != current_type:
                current_type = layout_object.object_type
                lines.append(f"<b>{html.escape(current_type)}</b>")

            selected_mark = " SELECTED" if layout_object.object_id == selected_object_id else ""
            hover_mark = " HOVER" if layout_object.object_id == hover_object_id else ""
            todo_mark = " TODO" if layout_object.todo_text else ""
            delta_text = (
                f"dx:{layout_object.delta_x} dy:{layout_object.delta_y} "
                f"dw:{layout_object.width_delta} dh:{layout_object.height_delta}"
            )
            object_line = html.escape(f"  |- {layout_object.object_id}{selected_mark}{hover_mark}{todo_mark}")
            delta_line = html.escape(f"     {delta_text}")
            lines.append(object_line)
            lines.append(delta_line)
            lines.append("")

        lines.append("</font>")
        return "<br>".join(lines)


class TodoViewFormatter:
    def selected_html(self, selected_todo: LayoutObject | None) -> str:
        if selected_todo is None:
            return "<font face=consolas size=3>Задача не выбрана.</font>"
        return (
            "<font face=consolas size=3>"
            f"<b>{html.escape(selected_todo.path)}</b><br><br>"
            f"{html.escape(selected_todo.todo_text).replace(chr(10), '<br>')}"
            "</font>"
        )
