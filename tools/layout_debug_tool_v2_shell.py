from __future__ import annotations

import copy
import html
import sys
from pathlib import Path

import pygame
import pygame_gui
import pygame.scrap
from pygame_gui.elements import (
    UIButton,
    UIDropDownMenu,
    UILabel,
    UIPanel,
    UISelectionList,
    UITextBox,
    UITextEntryBox,
    UITextEntryLine,
)

UI_TEXT_ENTRY_FINISHED = getattr(pygame_gui, "UI_TEXT_ENTRY_FINISHED", None)
UI_SELECTION_LIST_NEW_SELECTION = getattr(pygame_gui, "UI_SELECTION_LIST_NEW_SELECTION", None)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.layout_debug.config_repository import (  # noqa: E402
    LayoutConfigRepository,
    LayoutDataSource,
)
from tools.layout_debug.models import LayoutObject, safe_int  # noqa: E402
from tools.layout_debug.preview_geometry import (  # noqa: E402
    PreviewGeometryProvider,
    PreviewViewportMapper,
    object_at_canvas_pos,
)
from tools.layout_debug.session import LayoutSession  # noqa: E402
from tools.layout_debug.shell_layout import SHELL_LAYOUT, ShellLayoutMetrics  # noqa: E402
from tools.layout_debug.todo import TodoClipboardFormatter, TodoService  # noqa: E402
from tools.layout_debug.ui_panels import (  # noqa: E402
    build_context_panel,
    build_inspector_panel,
    build_navigator_panel,
    build_preview_panel,
    build_status_bar,
    build_todo_panel,
    filter_button_text,
)

THEME_PATH = PROJECT_ROOT / "ui_theme" / "layout_debug_tool_win95.json"
APP_CONFIG_PATH = PROJECT_ROOT / "app_config.json"

SUPPORTED_SCREEN_IDS = ("game_table", "main_menu", "modal_intro", "modal_endgame")
DEFAULT_SCREEN_ID = "game_table"
SCREEN_LABELS = {
    "game_table": "Игровой стол",
    "main_menu": "Главное меню",
    "modal_intro": "Стартовая модалка",
    "modal_endgame": "Финальная модалка",
}
SCREEN_IDS_BY_LABEL = {label: screen_id for screen_id, label in SCREEN_LABELS.items()}

WIN95_FACE = pygame.Color(192, 192, 192)
WIN95_DARK = pygame.Color(128, 128, 128)
WIN95_DARKER = pygame.Color(64, 64, 64)
WIN95_LIGHT = pygame.Color(255, 255, 255)
PREVIEW_BG = pygame.Color(18, 70, 44)
PREVIEW_FELT = pygame.Color(24, 104, 62)
HOVER_COLOR = pygame.Color(255, 255, 170)
SELECTED_COLOR = pygame.Color(255, 210, 80)


def clipboard_text_bytes(text: str) -> bytes:
    if sys.platform == "win32":
        return text.encode("mbcs", errors="replace")
    return text.encode("utf-8")


def draw_sunken_rect(surface: pygame.Surface, rect: pygame.Rect, fill: pygame.Color) -> None:
    pygame.draw.rect(surface, fill, rect)
    pygame.draw.line(surface, WIN95_DARKER, rect.topleft, rect.topright)
    pygame.draw.line(surface, WIN95_DARKER, rect.topleft, rect.bottomleft)
    pygame.draw.line(surface, WIN95_LIGHT, rect.bottomleft, rect.bottomright)
    pygame.draw.line(surface, WIN95_LIGHT, rect.topright, rect.bottomright)


class LayoutDebugToolV2Shell:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Layout Debug Tool v2 Shell")
        self.layout_metrics: ShellLayoutMetrics = SHELL_LAYOUT
        self.window = pygame.display.set_mode(self.layout_metrics.window_size)
        self.clock = pygame.time.Clock()
        self.manager = pygame_gui.UIManager(self.layout_metrics.window_size, str(THEME_PATH))

        self.font = pygame.font.SysFont("consolas", 16)
        self.small_font = pygame.font.SysFont("consolas", 14)
        self.running = True
        self.selected_filter_types = {"visible", "panel", "button"}
        self.show_hitboxes = False
        self.hover_object = "game_table.players.left.panel"
        self.selected_object = "game_table.players.left.name"
        self.layout_data = LayoutDataSource(APP_CONFIG_PATH, SUPPORTED_SCREEN_IDS)
        self.config_repository = LayoutConfigRepository(APP_CONFIG_PATH)
        self.layout_data.load()
        self.session = LayoutSession(self.layout_data.layout)
        self.todo_service = TodoService(self.layout_data, SUPPORTED_SCREEN_IDS)
        self.todo_clipboard_formatter = TodoClipboardFormatter()
        self.session_dirty = False
        self.current_screen_id = DEFAULT_SCREEN_ID
        self.layout_objects = self.layout_data.objects_for_screen(self.current_screen_id)
        self.selected_layout_object_id = self.layout_objects[0].object_id if self.layout_objects else None
        self.hover_layout_object_id: str | None = None
        self.preview_geometry = PreviewGeometryProvider()
        self.preview_mapper = PreviewViewportMapper(self.layout_metrics.game_canvas_size)
        self.preview_rects = self.preview_geometry.build_preview_rects(self.current_screen_id, self.layout_objects)
        self.layout_summary = self._layout_status_text()
        self.control_buttons: dict[UIButton, tuple[int, int, int, int]] = {}
        self.step_field: UITextEntryLine | None = None
        self.session.snapshot_selected(self.current_screen_id, self.selected_layout_object_id)
        self.selected_todo_path: str | None = None
        self.todo_paths_by_label: dict[str, str] = {}
        self.new_todo_entry_active = False

        self._build_ui()

    def _layout_status_text(self) -> str:
        hover = self.hover_layout_object_id or "-"
        selected = self.selected_layout_object_id or "-"
        session = "UNSAVED" if self.session.dirty else "saved"
        return (
            f"{self.layout_data.summary_text()} | "
            f"model: {self.current_screen_id}={len(self.layout_objects)} objects | "
            f"session: {session} | hover: {hover} | selected: {selected}"
        )

    def _update_session_status(self) -> None:
        self.session_dirty = self.session.dirty
        self.layout_summary = self._layout_status_text()
        if hasattr(self, "status_label"):
            status_text = "Статус: UNSAVED" if self.session_dirty else "Статус: saved"
            self.status_label.set_text(status_text)
        if hasattr(self, "status_bar_label"):
            self.status_bar_label.set_text(self.layout_summary)

    def _set_status_message(self, message: str) -> None:
        if hasattr(self, "status_bar_label"):
            self.status_bar_label.set_text(message)

    def _apply_session_to_config(self) -> None:
        if self.layout_data.load_error:
            self._set_status_message(f"Apply failed: {self.layout_data.load_error}")
            return

        try:
            config_data = self.config_repository.save_layout(
                copy.deepcopy(self.layout_data.data),
                copy.deepcopy(self.session.layout),
            )
        except OSError as exc:
            self._set_status_message(f"Apply failed: {type(exc).__name__}: {exc}")
            return

        self.layout_data.data = config_data
        self.session.mark_applied()
        self.session.snapshot_selected(self.current_screen_id, self.selected_layout_object_id)
        self._update_session_status()

    def set_current_screen(self, screen_id: str) -> None:
        if screen_id not in SUPPORTED_SCREEN_IDS:
            return
        self.current_screen_id = screen_id
        self.layout_objects = self.layout_data.objects_for_screen(self.current_screen_id)
        self.selected_layout_object_id = self.layout_objects[0].object_id if self.layout_objects else None
        self.hover_layout_object_id = None
        self.session.snapshot_selected(self.current_screen_id, self.selected_layout_object_id)
        self.preview_rects = self.preview_geometry.build_preview_rects(self.current_screen_id, self.layout_objects)
        self.navigator_body.set_text(self._navigator_html())
        self._update_inspector()
        self._sync_selected_todo_with_object()
        self._update_todo_view()
        self._update_session_status()

    def _navigator_html(self) -> str:
        if not self.layout_objects:
            return (
                "<font face=consolas size=3>"
                f"<b>{html.escape(self.current_screen_id)}</b><br><br>"
                "Нет layout-объектов."
                "</font>"
            )

        lines = [
            "<font face=consolas size=3>",
            f"<b>{html.escape(self.current_screen_id)}</b>",
            f"{len(self.layout_objects)} objects",
            f"Selected: {html.escape(self.selected_layout_object_id or '-')}",
            f"Hover: {html.escape(self.hover_layout_object_id or '-')}",
            "",
        ]
        current_type: str | None = None
        for layout_object in self.layout_objects:
            if layout_object.object_type != current_type:
                current_type = layout_object.object_type
                lines.append(f"<b>{html.escape(current_type)}</b>")

            selected_mark = " SELECTED" if layout_object.object_id == self.selected_layout_object_id else ""
            hover_mark = " HOVER" if layout_object.object_id == self.hover_layout_object_id else ""
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

    def _layout_object_by_id(self, object_id: str) -> LayoutObject | None:
        for layout_object in self.layout_objects:
            if layout_object.object_id == object_id:
                return layout_object
        return None

    def _selected_layout_object(self) -> LayoutObject | None:
        if self.selected_layout_object_id is None:
            return None
        return self._layout_object_by_id(self.selected_layout_object_id)

    def _selected_preview_rect(self) -> pygame.Rect:
        if self.selected_layout_object_id is None:
            return pygame.Rect(0, 0, 0, 0)
        return self.preview_rects.get(self.selected_layout_object_id, pygame.Rect(0, 0, 0, 0))

    def _dismiss_selected_object_changes(self) -> None:
        self.session.dismiss_selected(self.current_screen_id, self.selected_layout_object_id)
        self._update_session_status()

    def _cancel_selected_object_changes(self) -> None:
        if self.session.cancel_selected(self.current_screen_id, self.selected_layout_object_id):
            self._refresh_layout_session_view()

    def _reset_session_changes(self) -> None:
        self.session.reset()
        self.session.snapshot_selected(self.current_screen_id, self.selected_layout_object_id)
        self._refresh_layout_session_view()

    def _refresh_layout_session_view(self) -> None:
        self.layout_objects = self.layout_data.objects_for_screen(self.current_screen_id)
        if self.selected_layout_object_id and self._layout_object_by_id(self.selected_layout_object_id) is None:
            self.selected_layout_object_id = self.layout_objects[0].object_id if self.layout_objects else None
        self.preview_rects = self.preview_geometry.build_preview_rects(self.current_screen_id, self.layout_objects)
        self.navigator_body.set_text(self._navigator_html())
        self._update_inspector()
        self._sync_selected_todo_with_object()
        self._update_todo_view()
        self._update_session_status()

    def _selected_todo_item(self) -> LayoutObject | None:
        return self.todo_service.selected_item(self.selected_todo_path)

    def _sync_selected_todo_with_object(self) -> None:
        self.selected_todo_path = self.todo_service.sync_selected_path(
            self._selected_layout_object(),
            self.selected_todo_path,
        )

    def _todo_selection_items(self) -> list[str]:
        items, self.todo_paths_by_label = self.todo_service.selection_items()
        return items

    def _selected_todo_html(self) -> str:
        selected_todo = self._selected_todo_item()
        if selected_todo is None:
            return "<font face=consolas size=3>Задача не выбрана.</font>"
        return (
            "<font face=consolas size=3>"
            f"<b>{html.escape(selected_todo.path)}</b><br><br>"
            f"{html.escape(selected_todo.todo_text).replace(chr(10), '<br>')}"
            "</font>"
        )

    def _update_todo_view(self) -> None:
        if not hasattr(self, "todo_list"):
            return
        items = self._todo_selection_items()
        try:
            self.todo_list.set_item_list(items)
        except AttributeError:
            self.todo_list.kill()
            self.todo_list = UISelectionList(
                item_list=items,
                relative_rect=pygame.Rect(8, 36, 286, 116),
                manager=self.manager,
                container=self.todo_existing_panel,
                object_id="#win95_selection_list",
            )
        selected_todo = self._selected_todo_item()
        if selected_todo is not None:
            for label, path in self.todo_paths_by_label.items():
                if path == selected_todo.path:
                    if hasattr(self.todo_list, "set_default_selection"):
                        self.todo_list.set_default_selection(label)
                    break
        self.todo_text.set_text(self._selected_todo_html())

    def _select_todo_by_label(self, label: str) -> None:
        selected_path = self.todo_service.selected_path_by_label(label, self.todo_paths_by_label)
        if selected_path is None:
            return
        self.selected_todo_path = selected_path
        self._update_todo_view()

    def _add_task_for_selected_object(self) -> None:
        if not hasattr(self, "new_todo_entry"):
            return
        task_text = self.new_todo_entry.get_text().strip()
        if not task_text:
            return
        if not self.session.set_todo_text(self.current_screen_id, self.selected_layout_object_id, task_text):
            return
        selected_object = self._selected_layout_object()
        self.selected_todo_path = selected_object.path if selected_object is not None else None
        self._refresh_layout_session_view()

    def _clean_new_task_form(self) -> None:
        if hasattr(self, "new_todo_entry"):
            self.new_todo_entry.set_text("")

    def _selected_todo_structured_text(self) -> str | None:
        return self.todo_clipboard_formatter.structured_text(self._selected_todo_item())

    def _copy_selected_todo_to_clipboard(self) -> None:
        task_text = self._selected_todo_structured_text()
        if not task_text:
            self._set_status_message("Copy failed: task is not selected")
            return
        try:
            pygame.scrap.init()
            pygame.scrap.put(pygame.SCRAP_TEXT, clipboard_text_bytes(task_text))
        except pygame.error as exc:
            self._set_status_message(f"Copy failed: {exc}")
            return
        self._set_status_message("Copied selected task to clipboard")

    def _update_new_task_focus_indicator(self) -> None:
        if not hasattr(self, "new_task_title_label"):
            return
        suffix = "  ACTIVE" if self.new_todo_entry_active else ""
        self.new_task_title_label.set_text(f"СОЗДАТЬ НОВУЮ ЗАДАЧУ{suffix}")

    def _set_new_task_entry_active_from_mouse(self, pos: tuple[int, int]) -> None:
        if not hasattr(self, "new_todo_entry"):
            return
        was_active = self.new_todo_entry_active
        self.new_todo_entry_active = self.new_todo_entry.get_abs_rect().collidepoint(pos)
        if self.new_todo_entry_active != was_active:
            self._update_new_task_focus_indicator()

    def _apply_inspector_field_change(self, field_name: str, text: str) -> None:
        rect = self._selected_preview_rect()
        if self.session.apply_field_change(
            self.current_screen_id,
            self.selected_layout_object_id,
            field_name,
            text,
            rect.x,
            rect.y,
            rect.width,
            rect.height,
        ):
            self._refresh_layout_session_view()

    def _current_step(self) -> int:
        if self.step_field is None:
            return 10
        return max(1, safe_int(self.step_field.get_text(), 10))

    def _nudge_selected_object(self, dx: int = 0, dy: int = 0, dw: int = 0, dh: int = 0) -> None:
        if self.session.nudge_selected(self.current_screen_id, self.selected_layout_object_id, dx, dy, dw, dh):
            self._refresh_layout_session_view()

    def _build_ui(self) -> None:
        context = build_context_panel(
            self.manager,
            self.layout_metrics,
            SCREEN_LABELS,
            SUPPORTED_SCREEN_IDS,
            self.current_screen_id,
            self.selected_filter_types,
        )
        self.context_panel = context.panel
        self.screen_dropdown = context.screen_dropdown
        self.status_label = context.status_label
        self.apply_button = context.apply_button
        self.reset_button = context.reset_button
        self.help_button = context.help_button
        self.filter_buttons = context.filter_buttons
        self.preview_mode = context.preview_mode
        self.hitboxes_button = context.hitboxes_button

        navigator = build_navigator_panel(self.manager, self.layout_metrics, self._navigator_html())
        self.navigator_panel = navigator.panel
        self.navigator_body = navigator.body

        inspector = build_inspector_panel(self.manager, self.layout_metrics)
        self.inspector_panel = inspector.panel
        self.inspector_object_label = inspector.object_label
        self.inspector_type_label = inspector.type_label
        self.inspector_fields = inspector.fields
        self.inspector_field_names_by_element = inspector.field_names_by_element
        self.dismiss_button = inspector.dismiss_button
        self.cancel_button = inspector.cancel_button
        self.step_field = inspector.step_field
        self.control_buttons = inspector.control_buttons
        self._update_inspector()

        preview = build_preview_panel(self.manager, self.layout_metrics)
        self.preview_panel = preview.panel

        todo = build_todo_panel(
            manager=self.manager,
            metrics=self.layout_metrics,
            todo_items=self._todo_selection_items(),
            selected_todo_html=self._selected_todo_html(),
        )
        self.todo_panel = todo.panel
        self.todo_existing_panel = todo.existing_panel
        self.todo_list = todo.list_widget
        self.todo_text = todo.text
        self.edit_task_button = todo.edit_button
        self.copy_task_button = todo.copy_button
        self.new_task_title_label = todo.title_label
        self.new_todo_entry = todo.entry
        self.add_task_button = todo.add_button
        self.clean_task_button = todo.clean_button
        self._update_new_task_focus_indicator()

        status = build_status_bar(self.manager, self.layout_metrics, self.layout_summary)
        self.status_bar = status.panel
        self.status_bar_label = status.label

    def _update_inspector(self) -> None:
        if not hasattr(self, "inspector_fields"):
            return
        layout_object = self._selected_layout_object()
        rect = self._selected_preview_rect()

        if layout_object is None:
            self.inspector_object_label.set_text("Object: -")
            self.inspector_type_label.set_text("Type: -")
            values = {
                "x": "0",
                "y": "0",
                "width": "0",
                "height": "0",
                "delta_x": "0",
                "delta_y": "0",
                "width_delta": "0",
                "height_delta": "0",
                "color": "",
                "font": "",
                "font_size": "0",
            }
        else:
            self.inspector_object_label.set_text(f"Object: {layout_object.object_id}")
            self.inspector_type_label.set_text(f"Type: {layout_object.object_type}")
            values = {
                "x": str(rect.x),
                "y": str(rect.y),
                "width": str(rect.width),
                "height": str(rect.height),
                "delta_x": str(layout_object.delta_x),
                "delta_y": str(layout_object.delta_y),
                "width_delta": str(layout_object.width_delta),
                "height_delta": str(layout_object.height_delta),
                "color": layout_object.color or "#c0c0c0",
                "font": layout_object.font or "Arial",
                "font_size": str(layout_object.font_size or 14),
            }

        for field_name, value in values.items():
            field = self.inspector_fields.get(field_name)
            if field is not None:
                field.set_text(value)

    def _filter_text(self, filter_id: str, label: str) -> str:
        return filter_button_text(self.selected_filter_types, filter_id, label)

    def _layout_preview_viewport(self) -> pygame.Rect:
        return self.preview_mapper.viewport_for_panel(self.preview_panel.get_abs_rect())

    def _canvas_to_viewport_rect(self, rect: pygame.Rect, viewport: pygame.Rect) -> pygame.Rect:
        return self.preview_mapper.canvas_to_viewport_rect(rect, viewport)

    def _viewport_to_canvas_pos(self, pos: tuple[int, int], viewport: pygame.Rect) -> tuple[int, int] | None:
        return self.preview_mapper.viewport_to_canvas_pos(pos, viewport)

    def _object_at_canvas_pos(self, pos: tuple[int, int]) -> str | None:
        return object_at_canvas_pos(pos, self.preview_rects)

    def _set_hover_from_mouse(self, pos: tuple[int, int]) -> None:
        canvas_pos = self._viewport_to_canvas_pos(pos, self._layout_preview_viewport())
        next_hover = self._object_at_canvas_pos(canvas_pos) if canvas_pos is not None else None
        if next_hover == self.hover_layout_object_id:
            return
        self.hover_layout_object_id = next_hover
        self.navigator_body.set_text(self._navigator_html())
        self._update_session_status()

    def _select_hovered_object(self) -> None:
        if self.hover_layout_object_id is None:
            return
        self.selected_layout_object_id = self.hover_layout_object_id
        self.session.snapshot_selected(self.current_screen_id, self.selected_layout_object_id)
        self.navigator_body.set_text(self._navigator_html())
        self._update_inspector()
        self._sync_selected_todo_with_object()
        self._update_todo_view()
        self._update_session_status()

    def _event_targets_text_entry(self, event: pygame.event.Event) -> bool:
        return getattr(event, "ui_element", None) in self.inspector_field_names_by_element or getattr(event, "ui_element", None) == self.step_field

    def _handle_keyboard_control(self, event: pygame.event.Event) -> bool:
        if event.type != pygame.KEYDOWN:
            return False
        if any(getattr(field, "is_focused", False) for field in self.inspector_fields.values()):
            return False
        if self.step_field is not None and getattr(self.step_field, "is_focused", False):
            return False

        step = self._current_step()
        if event.key == pygame.K_LEFT:
            self._nudge_selected_object(dx=-step)
        elif event.key == pygame.K_RIGHT:
            self._nudge_selected_object(dx=step)
        elif event.key == pygame.K_UP:
            self._nudge_selected_object(dy=-step)
        elif event.key == pygame.K_DOWN:
            self._nudge_selected_object(dy=step)
        else:
            return False
        return True

    def _draw_background(self) -> None:
        self.window.fill(WIN95_FACE)

    def _draw_preview_placeholder(self) -> None:
        panel_rect = self.preview_panel.get_abs_rect()

        viewport = self._layout_preview_viewport()
        draw_sunken_rect(self.window, viewport, PREVIEW_BG)
        felt = viewport.inflate(-80, -70)
        pygame.draw.rect(self.window, PREVIEW_FELT, felt, border_radius=18)
        pygame.draw.rect(self.window, pygame.Color(220, 220, 220), felt, 2, border_radius=18)

        center_lines = [
            "GAME CANVAS 1600 x 900",
            "aspect ratio 16:9",
            "",
            "hover -> подсветка объекта",
            "ЛКМ -> выбор объекта",
            "",
            "только выбор объекта",
            "без drag / resize мышью",
        ]
        y = viewport.y + viewport.height // 2 - 78
        for line in center_lines:
            surface = self.font.render(line, True, WIN95_LIGHT)
            self.window.blit(surface, surface.get_rect(center=(viewport.centerx, y)))
            y += 22

        for object_id, rect in self.preview_rects.items():
            if not self.show_hitboxes and object_id not in {self.hover_layout_object_id, self.selected_layout_object_id}:
                continue
            preview_rect = self._canvas_to_viewport_rect(rect, viewport)
            if object_id == self.selected_layout_object_id:
                color = SELECTED_COLOR
                width = 3
            elif object_id == self.hover_layout_object_id:
                color = HOVER_COLOR
                width = 3
            else:
                color = WIN95_LIGHT
                width = 1
            pygame.draw.rect(self.window, color, preview_rect, width)

        for object_id, label, color in [
            (self.hover_layout_object_id, "hover", HOVER_COLOR),
            (self.selected_layout_object_id, "selected", SELECTED_COLOR),
        ]:
            if object_id is None or object_id not in self.preview_rects:
                continue
            preview_rect = self._canvas_to_viewport_rect(self.preview_rects[object_id], viewport)
            surface = self.small_font.render(label, True, color)
            self.window.blit(surface, (preview_rect.x, max(viewport.y + 4, preview_rect.y - 20)))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
            return
        self.manager.process_events(event)
        if self._handle_keyboard_control(event):
            return
        if event.type == pygame.MOUSEMOTION:
            self._set_hover_from_mouse(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._set_new_task_entry_active_from_mouse(event.pos)
            self._set_hover_from_mouse(event.pos)
            self._select_hovered_object()
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.ui_element == self.screen_dropdown:
            selected_screen_id = SCREEN_IDS_BY_LABEL.get(event.text)
            if selected_screen_id is not None:
                self.set_current_screen(selected_screen_id)
            return
        if UI_TEXT_ENTRY_FINISHED is not None and event.type == UI_TEXT_ENTRY_FINISHED:
            field_name = self.inspector_field_names_by_element.get(event.ui_element)
            if field_name is not None:
                self._apply_inspector_field_change(field_name, getattr(event, "text", ""))
            return
        if UI_SELECTION_LIST_NEW_SELECTION is not None and event.type == UI_SELECTION_LIST_NEW_SELECTION:
            if event.ui_element == self.todo_list:
                self._select_todo_by_label(getattr(event, "text", ""))
            return
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.apply_button:
                self._apply_session_to_config()
                return
            if event.ui_element == self.reset_button:
                self._reset_session_changes()
                return
            if event.ui_element == self.copy_task_button:
                self._copy_selected_todo_to_clipboard()
                return
            if event.ui_element == self.add_task_button:
                self._add_task_for_selected_object()
                return
            if event.ui_element == self.clean_task_button:
                self._clean_new_task_form()
                return
            if event.ui_element == self.dismiss_button:
                self._dismiss_selected_object_changes()
                return
            if event.ui_element == self.cancel_button:
                self._cancel_selected_object_changes()
                return
            if event.ui_element in self.control_buttons:
                step = self._current_step()
                dx, dy, dw, dh = self.control_buttons[event.ui_element]
                self._nudge_selected_object(dx * step, dy * step, dw * step, dh * step)
                return
            for filter_id, button in self.filter_buttons.items():
                if event.ui_element == button:
                    if filter_id in self.selected_filter_types:
                        self.selected_filter_types.remove(filter_id)
                    else:
                        self.selected_filter_types.add(filter_id)
                    button.set_text(self._filter_text(filter_id, filter_id))
                    return
            if event.ui_element == self.hitboxes_button:
                self.show_hitboxes = not self.show_hitboxes
                self.hitboxes_button.set_text(("[x]" if self.show_hitboxes else "[ ]") + " Show hitboxes")
                return

    def run(self) -> None:
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                self.handle_event(event)

            self.manager.update(time_delta)
            self._draw_background()
            self.manager.draw_ui(self.window)
            self._draw_preview_placeholder()

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    LayoutDebugToolV2Shell().run()
