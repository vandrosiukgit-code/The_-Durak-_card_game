from __future__ import annotations

import html

from tools.layout_debug.models import LayoutObject


class NavigatorViewFormatter:
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
