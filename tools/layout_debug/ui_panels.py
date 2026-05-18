from __future__ import annotations

from dataclasses import dataclass

import pygame
import pygame_gui
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

from tools.layout_debug.shell_layout import ShellLayoutMetrics


@dataclass
class ContextPanelRefs:
    panel: UIPanel
    screen_dropdown: UIDropDownMenu
    status_label: UILabel
    apply_button: UIButton
    reset_button: UIButton
    help_button: UIButton
    filter_buttons: dict[str, UIButton]
    preview_mode: UILabel
    hitboxes_button: UIButton


@dataclass
class NavigatorPanelRefs:
    panel: UIPanel
    body: UITextBox


@dataclass
class InspectorPanelRefs:
    panel: UIPanel
    object_label: UILabel
    type_label: UILabel
    fields: dict[str, UITextEntryLine]
    field_names_by_element: dict[UITextEntryLine, str]
    dismiss_button: UIButton
    cancel_button: UIButton
    copy_id_button: UIButton
    step_field: UITextEntryLine
    control_buttons: dict[UIButton, tuple[int, int, int, int]]


@dataclass
class PreviewPanelRefs:
    panel: UIPanel


@dataclass
class TodoPanelRefs:
    panel: UIPanel
    existing_panel: UIPanel
    list_widget: UISelectionList
    text: UITextBox
    edit_button: UIButton
    copy_button: UIButton
    title_label: UILabel
    entry: UITextEntryBox
    add_button: UIButton
    clean_button: UIButton


@dataclass
class StatusBarRefs:
    panel: UIPanel
    label: UILabel


def filter_button_text(selected_filter_types: set[str], filter_id: str, label: str) -> str:
    mark = "x" if filter_id in selected_filter_types else " "
    return f"[{mark}] {label}"


def build_section_title(manager: pygame_gui.UIManager, container: UIPanel, text: str, width: int) -> None:
    title_panel = UIPanel(
        relative_rect=pygame.Rect(1, 1, width, 22),
        manager=manager,
        container=container,
        object_id="#win95_section_title",
    )
    UILabel(
        relative_rect=pygame.Rect(8, 1, width - 16, 18),
        text=text,
        manager=manager,
        container=title_panel,
        object_id="#win95_title_label",
    )


def build_context_panel(
    manager: pygame_gui.UIManager,
    metrics: ShellLayoutMetrics,
    screen_labels: dict[str, str],
    supported_screen_ids: tuple[str, ...],
    current_screen_id: str,
    selected_filter_types: set[str],
) -> ContextPanelRefs:
    panel = UIPanel(
        relative_rect=metrics.context_rect,
        manager=manager,
        object_id="#win95_panel",
    )
    build_section_title(manager, panel, "ПАНЕЛЬ КОНТЕКСТА", metrics.context_rect.width - 2)
    UILabel(
        relative_rect=pygame.Rect(12, 34, 58, 24),
        text="Экран:",
        manager=manager,
        container=panel,
        object_id="#win95_label",
    )
    screen_dropdown = UIDropDownMenu(
        options_list=[screen_labels[screen_id] for screen_id in supported_screen_ids],
        starting_option=screen_labels[current_screen_id],
        relative_rect=pygame.Rect(metrics.context_rect.x + 72, metrics.context_rect.y + 32, 220, 28),
        manager=manager,
    )
    status_label = UILabel(
        relative_rect=pygame.Rect(312, 34, 210, 24),
        text="Статус: saved",
        manager=manager,
        container=panel,
        object_id="#win95_label",
    )
    apply_button = UIButton(
        relative_rect=pygame.Rect(1198, 32, 108, 28),
        text="Apply",
        manager=manager,
        container=panel,
        object_id="#win95_button",
    )
    reset_button = UIButton(
        relative_rect=pygame.Rect(1316, 32, 138, 28),
        text="Reset session",
        manager=manager,
        container=panel,
        object_id="#win95_button",
    )
    help_button = UIButton(
        relative_rect=pygame.Rect(1464, 32, 92, 28),
        text="Help",
        manager=manager,
        container=panel,
        object_id="#win95_button",
    )
    filter_buttons: dict[str, UIButton] = {}
    x = 12
    for filter_id, label in [
        ("visible", "visible"),
        ("panel", "panel"),
        ("button", "button"),
        ("helper", "helper"),
        ("changed", "changed"),
    ]:
        button = UIButton(
            relative_rect=pygame.Rect(x, 68, 112, 24),
            text=filter_button_text(selected_filter_types, filter_id, label),
            manager=manager,
            container=panel,
            object_id="#win95_button",
        )
        filter_buttons[filter_id] = button
        x += 120
    preview_mode = UILabel(
        relative_rect=pygame.Rect(748, 70, 230, 22),
        text="Режим preview: Hover select",
        manager=manager,
        container=panel,
        object_id="#win95_label",
    )
    hitboxes_button = UIButton(
        relative_rect=pygame.Rect(990, 66, 160, 28),
        text="[ ] Show hitboxes",
        manager=manager,
        container=panel,
        object_id="#win95_button",
    )
    return ContextPanelRefs(
        panel,
        screen_dropdown,
        status_label,
        apply_button,
        reset_button,
        help_button,
        filter_buttons,
        preview_mode,
        hitboxes_button,
    )


def build_navigator_panel(
    manager: pygame_gui.UIManager,
    metrics: ShellLayoutMetrics,
    html_text: str,
) -> NavigatorPanelRefs:
    panel = UIPanel(
        relative_rect=metrics.navigator_rect,
        manager=manager,
        object_id="#win95_panel",
    )
    build_section_title(manager, panel, "НАВИГАТОР ОБЪЕКТОВ", metrics.navigator_rect.width - 2)
    body = UITextBox(
        html_text=html_text,
        relative_rect=pygame.Rect(10, 34, metrics.navigator_rect.width - 42, metrics.navigator_rect.height - 66),
        manager=manager,
        container=panel,
        object_id="#win95_textbox",
    )
    return NavigatorPanelRefs(panel, body)


def build_preview_panel(manager: pygame_gui.UIManager, metrics: ShellLayoutMetrics) -> PreviewPanelRefs:
    panel = UIPanel(
        relative_rect=metrics.preview_rect,
        manager=manager,
        object_id="#win95_panel",
    )
    build_section_title(manager, panel, "PREVIEW AREA", metrics.preview_rect.width - 2)
    return PreviewPanelRefs(panel)


def build_status_bar(
    manager: pygame_gui.UIManager,
    metrics: ShellLayoutMetrics,
    status_text: str,
) -> StatusBarRefs:
    panel = UIPanel(
        relative_rect=metrics.status_rect,
        manager=manager,
        object_id="#win95_panel",
    )
    label = UILabel(
        relative_rect=pygame.Rect(8, 2, metrics.window_size[0] - 32, 20),
        text=status_text,
        manager=manager,
        container=panel,
        object_id="#win95_label",
    )
    return StatusBarRefs(panel, label)


def build_inspector_panel(manager: pygame_gui.UIManager, metrics: ShellLayoutMetrics) -> InspectorPanelRefs:
    panel = UIPanel(
        relative_rect=metrics.inspector_rect,
        manager=manager,
        object_id="#win95_panel",
    )
    build_section_title(manager, panel, "ИНСПЕКТОР", metrics.inspector_rect.width - 2)
    object_label = UILabel(
        pygame.Rect(metrics.inspector_content_x, 34, 300, 22),
        "Object:",
        manager,
        container=panel,
        object_id="#win95_object_label",
    )
    type_label = UILabel(
        pygame.Rect(metrics.inspector_content_x, 60, 300, 22),
        "Type:",
        manager,
        container=panel,
        object_id="#win95_object_label",
    )
    fields: dict[str, UITextEntryLine] = {}
    field_names_by_element: dict[UITextEntryLine, str] = {}
    _build_inspector_group(
        manager,
        metrics,
        panel,
        fields,
        field_names_by_element,
        "GEOMETRY",
        96,
        metrics.inspector_group_height,
        [("x", "0"), ("y", "0"), ("width", "0"), ("height", "0")],
    )
    _build_inspector_group(
        manager,
        metrics,
        panel,
        fields,
        field_names_by_element,
        "LAYOUT DELTAS",
        184,
        metrics.inspector_group_height,
        [("delta_x", "0"), ("delta_y", "0"), ("width_delta", "0"), ("height_delta", "0")],
    )
    _build_inspector_group(
        manager,
        metrics,
        panel,
        fields,
        field_names_by_element,
        "VISUAL",
        272,
        metrics.inspector_group_height,
        [("color", "#c0c0c0"), ("font", "Arial"), ("font_size", "14")],
    )
    step_field, control_buttons = _build_inspector_controls(manager, metrics, panel, 360)
    dismiss_button = UIButton(
        pygame.Rect(10, metrics.inspector_action_y, 94, 24),
        "Dismiss",
        manager,
        container=panel,
        object_id="#win95_button",
    )
    cancel_button = UIButton(
        pygame.Rect(114, metrics.inspector_action_y, 86, 24),
        "Cancel",
        manager,
        container=panel,
        object_id="#win95_button",
    )
    copy_id_button = UIButton(
        pygame.Rect(210, metrics.inspector_action_y, 106, 24),
        "Copy id",
        manager,
        container=panel,
        object_id="#win95_button",
    )
    return InspectorPanelRefs(
        panel,
        object_label,
        type_label,
        fields,
        field_names_by_element,
        dismiss_button,
        cancel_button,
        copy_id_button,
        step_field,
        control_buttons,
    )


def _build_inspector_group(
    manager: pygame_gui.UIManager,
    metrics: ShellLayoutMetrics,
    inspector_panel: UIPanel,
    fields: dict[str, UITextEntryLine],
    field_names_by_element: dict[UITextEntryLine, str],
    title: str,
    y: int,
    height: int,
    group_fields: list[tuple[str, str]],
) -> None:
    panel = UIPanel(
        relative_rect=pygame.Rect(metrics.inspector_group_x, y, metrics.inspector_group_width, height),
        manager=manager,
        container=inspector_panel,
        object_id="#win95_sunken_panel",
    )
    UILabel(pygame.Rect(8, 6, 140, 16), title, manager, container=panel, object_id="#win95_label")
    row_y = 28
    for idx, (label, value) in enumerate(group_fields):
        px = 8 + (idx % 2) * 150
        py = row_y + (idx // 2) * 20
        label_width = 86 if len(label) > 6 else 50
        input_x = px + label_width
        input_w = 136 - label_width
        UILabel(
            pygame.Rect(px, py, label_width - 4, 16),
            f"{label}:",
            manager,
            container=panel,
            object_id="#win95_small_label",
        )
        entry = UITextEntryLine(
            relative_rect=pygame.Rect(input_x, py, input_w, 16),
            manager=manager,
            container=panel,
            initial_text=value,
            object_id="#win95_input",
        )
        fields[label] = entry
        field_names_by_element[entry] = label


def _build_inspector_controls(
    manager: pygame_gui.UIManager,
    metrics: ShellLayoutMetrics,
    inspector_panel: UIPanel,
    y: int,
) -> tuple[UITextEntryLine, dict[UIButton, tuple[int, int, int, int]]]:
    panel = UIPanel(
        relative_rect=pygame.Rect(
            metrics.inspector_group_x,
            y,
            metrics.inspector_group_width,
            metrics.inspector_control_height,
        ),
        manager=manager,
        container=inspector_panel,
        object_id="#win95_sunken_panel",
    )
    UILabel(pygame.Rect(8, 8, 120, 16), "CONTROL", manager, container=panel, object_id="#win95_label")
    UILabel(pygame.Rect(8, 32, 42, 16), "Step:", manager, container=panel, object_id="#win95_label")
    step_field = UITextEntryLine(
        relative_rect=pygame.Rect(56, 30, 58, 20),
        manager=manager,
        container=panel,
        initial_text="10",
        object_id="#win95_input",
    )
    control_buttons: dict[UIButton, tuple[int, int, int, int]] = {}
    UILabel(pygame.Rect(8, 62, 50, 16), "Move:", manager, container=panel, object_id="#win95_label")
    for idx, (text, delta) in enumerate([("<-", (-1, 0, 0, 0)), ("^", (0, -1, 0, 0)), ("v", (0, 1, 0, 0)), ("->", (1, 0, 0, 0))]):
        button = UIButton(pygame.Rect(62 + idx * 42, 58, 36, 24), text, manager, container=panel, object_id="#win95_button")
        control_buttons[button] = delta
    UILabel(pygame.Rect(8, 96, 42, 16), "Size:", manager, container=panel, object_id="#win95_label")
    for idx, (text, delta) in enumerate([("-W", (0, 0, -1, 0)), ("+W", (0, 0, 1, 0)), ("-H", (0, 0, 0, -1)), ("+H", (0, 0, 0, 1))]):
        button = UIButton(pygame.Rect(62 + idx * 42, 92, 36, 24), text, manager, container=panel, object_id="#win95_button")
        control_buttons[button] = delta
    return step_field, control_buttons


def build_todo_panel(
    manager: pygame_gui.UIManager,
    metrics: ShellLayoutMetrics,
    todo_items: list[str],
    selected_todo_html: str,
) -> TodoPanelRefs:
    panel = UIPanel(
        relative_rect=metrics.todo_rect,
        manager=manager,
        object_id="#win95_panel",
    )
    build_section_title(manager, panel, "TO DO", metrics.todo_rect.width - 2)
    existing_panel = UIPanel(
        relative_rect=pygame.Rect(8, 34, 760, 188),
        manager=manager,
        container=panel,
        object_id="#win95_sunken_panel",
    )
    new_panel = UIPanel(
        relative_rect=pygame.Rect(778, 34, 790, 188),
        manager=manager,
        container=panel,
        object_id="#win95_sunken_panel",
    )
    UILabel(pygame.Rect(8, 12, 300, 18), "ПРОСМОТР СОЗДАННЫХ ЗАДАЧ", manager, container=existing_panel, object_id="#win95_label")
    todo_list = UISelectionList(
        item_list=todo_items,
        relative_rect=pygame.Rect(8, 36, 286, 116),
        manager=manager,
        container=existing_panel,
        object_id="#win95_selection_list",
    )
    UILabel(pygame.Rect(330, 12, 386, 18), "ВЫБРАННАЯ ЗАДАЧА", manager, container=existing_panel, object_id="#win95_label")
    todo_text = UITextBox(
        html_text=selected_todo_html,
        relative_rect=pygame.Rect(330, 36, 386, 116),
        manager=manager,
        container=existing_panel,
        object_id="#win95_textbox",
    )
    edit_button = UIButton(pygame.Rect(407 + 0 * 124, 160, 112, 22), "Edit", manager, container=existing_panel, object_id="#win95_button")
    copy_button = UIButton(pygame.Rect(407 + 1 * 124, 160, 112, 22), "Copy", manager, container=existing_panel, object_id="#win95_button")
    title_label = UILabel(pygame.Rect(8, 12, 360, 18), "СОЗДАТЬ НОВУЮ ЗАДАЧУ", manager, container=new_panel, object_id="#win95_label")
    entry = UITextEntryBox(
        initial_text="",
        relative_rect=pygame.Rect(8, 36, 600, 138),
        manager=manager,
        container=new_panel,
        object_id="#win95_input",
    )
    add_button = UIButton(pygame.Rect(628, 68, 128, 30), "Add task", manager, container=new_panel, object_id="#win95_button")
    clean_button = UIButton(pygame.Rect(628, 112, 128, 30), "Clean", manager, container=new_panel, object_id="#win95_button")
    return TodoPanelRefs(
        panel,
        existing_panel,
        todo_list,
        todo_text,
        edit_button,
        copy_button,
        title_label,
        entry,
        add_button,
        clean_button,
    )
