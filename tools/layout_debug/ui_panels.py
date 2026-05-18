from __future__ import annotations

from dataclasses import dataclass

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


def build_section_title(
    manager: pygame_gui.UIManager,
    metrics: ShellLayoutMetrics,
    container: UIPanel,
    text: str,
    width: int,
) -> None:
    title_panel = UIPanel(
        relative_rect=metrics.section_title_panel_rect(width),
        manager=manager,
        container=container,
        object_id="#win95_section_title",
    )
    UILabel(
        relative_rect=metrics.section_title_label_rect(width),
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
    build_section_title(manager, metrics, panel, "ПАНЕЛЬ КОНТЕКСТА", metrics.context_rect.width - 2)
    UILabel(
        relative_rect=metrics.context_screen_label_rect,
        text="Экран:",
        manager=manager,
        container=panel,
        object_id="#win95_label",
    )
    screen_dropdown = UIDropDownMenu(
        options_list=[screen_labels[screen_id] for screen_id in supported_screen_ids],
        starting_option=screen_labels[current_screen_id],
        relative_rect=metrics.context_screen_dropdown_rect,
        manager=manager,
    )
    status_label = UILabel(
        relative_rect=metrics.context_status_label_rect,
        text="Статус: saved",
        manager=manager,
        container=panel,
        object_id="#win95_label",
    )
    apply_button = UIButton(
        relative_rect=metrics.context_apply_button_rect,
        text="Apply",
        manager=manager,
        container=panel,
        object_id="#win95_button",
    )
    reset_button = UIButton(
        relative_rect=metrics.context_reset_button_rect,
        text="Reset session",
        manager=manager,
        container=panel,
        object_id="#win95_button",
    )
    help_button = UIButton(
        relative_rect=metrics.context_help_button_rect,
        text="Help",
        manager=manager,
        container=panel,
        object_id="#win95_button",
    )
    filter_buttons: dict[str, UIButton] = {}
    for index, (filter_id, label) in enumerate([
        ("visible", "visible"),
        ("panel", "panel"),
        ("button", "button"),
        ("helper", "helper"),
        ("changed", "changed"),
    ]):
        button = UIButton(
            relative_rect=metrics.context_filter_button_rect(index),
            text=filter_button_text(selected_filter_types, filter_id, label),
            manager=manager,
            container=panel,
            object_id="#win95_button",
        )
        filter_buttons[filter_id] = button
    preview_mode = UILabel(
        relative_rect=metrics.context_preview_mode_rect,
        text="Режим preview: Hover select",
        manager=manager,
        container=panel,
        object_id="#win95_label",
    )
    hitboxes_button = UIButton(
        relative_rect=metrics.context_hitboxes_button_rect,
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
    build_section_title(manager, metrics, panel, "НАВИГАТОР ОБЪЕКТОВ", metrics.navigator_rect.width - 2)
    body = UITextBox(
        html_text=html_text,
        relative_rect=metrics.navigator_body_rect,
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
    build_section_title(manager, metrics, panel, "PREVIEW AREA", metrics.preview_rect.width - 2)
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
        relative_rect=metrics.status_label_rect,
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
    build_section_title(manager, metrics, panel, "ИНСПЕКТОР", metrics.inspector_rect.width - 2)
    object_label = UILabel(
        metrics.inspector_object_label_rect,
        "Object:",
        manager,
        container=panel,
        object_id="#win95_object_label",
    )
    type_label = UILabel(
        metrics.inspector_type_label_rect,
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
        metrics.inspector_dismiss_button_rect,
        "Dismiss",
        manager,
        container=panel,
        object_id="#win95_button",
    )
    cancel_button = UIButton(
        metrics.inspector_cancel_button_rect,
        "Cancel",
        manager,
        container=panel,
        object_id="#win95_button",
    )
    copy_id_button = UIButton(
        metrics.inspector_copy_id_button_rect,
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
        relative_rect=metrics.inspector_group_rect(y, height),
        manager=manager,
        container=inspector_panel,
        object_id="#win95_sunken_panel",
    )
    UILabel(metrics.inspector_group_title_rect, title, manager, container=panel, object_id="#win95_label")
    row_y = 28
    for idx, (label, value) in enumerate(group_fields):
        px = 8 + (idx % 2) * 150
        py = row_y + (idx // 2) * 20
        label_width = 86 if len(label) > 6 else 50
        input_x = px + label_width
        input_w = 136 - label_width
        UILabel(
            metrics.inspector_field_label_rect(px, py, label_width),
            f"{label}:",
            manager,
            container=panel,
            object_id="#win95_small_label",
        )
        entry = UITextEntryLine(
            relative_rect=metrics.inspector_field_input_rect(input_x, py, input_w),
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
        relative_rect=metrics.inspector_group_rect(y, metrics.inspector_control_height),
        manager=manager,
        container=inspector_panel,
        object_id="#win95_sunken_panel",
    )
    UILabel(metrics.inspector_control_title_rect, "CONTROL", manager, container=panel, object_id="#win95_label")
    UILabel(metrics.inspector_step_label_rect, "Step:", manager, container=panel, object_id="#win95_label")
    step_field = UITextEntryLine(
        relative_rect=metrics.inspector_step_input_rect,
        manager=manager,
        container=panel,
        initial_text="10",
        object_id="#win95_input",
    )
    control_buttons: dict[UIButton, tuple[int, int, int, int]] = {}
    UILabel(metrics.inspector_move_label_rect, "Move:", manager, container=panel, object_id="#win95_label")
    for idx, (text, delta) in enumerate([("<-", (-1, 0, 0, 0)), ("^", (0, -1, 0, 0)), ("v", (0, 1, 0, 0)), ("->", (1, 0, 0, 0))]):
        button = UIButton(metrics.inspector_move_button_rect(idx), text, manager, container=panel, object_id="#win95_button")
        control_buttons[button] = delta
    UILabel(metrics.inspector_size_label_rect, "Size:", manager, container=panel, object_id="#win95_label")
    for idx, (text, delta) in enumerate([("-W", (0, 0, -1, 0)), ("+W", (0, 0, 1, 0)), ("-H", (0, 0, 0, -1)), ("+H", (0, 0, 0, 1))]):
        button = UIButton(metrics.inspector_size_button_rect(idx), text, manager, container=panel, object_id="#win95_button")
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
    build_section_title(manager, metrics, panel, "TO DO", metrics.todo_rect.width - 2)
    existing_panel = UIPanel(
        relative_rect=metrics.todo_existing_panel_rect,
        manager=manager,
        container=panel,
        object_id="#win95_sunken_panel",
    )
    new_panel = UIPanel(
        relative_rect=metrics.todo_new_panel_rect,
        manager=manager,
        container=panel,
        object_id="#win95_sunken_panel",
    )
    UILabel(metrics.todo_existing_title_rect, "ПРОСМОТР СОЗДАННЫХ ЗАДАЧ", manager, container=existing_panel, object_id="#win95_label")
    todo_list = UISelectionList(
        item_list=todo_items,
        relative_rect=metrics.todo_list_rect,
        manager=manager,
        container=existing_panel,
        object_id="#win95_selection_list",
    )
    UILabel(metrics.todo_selected_title_rect, "ВЫБРАННАЯ ЗАДАЧА", manager, container=existing_panel, object_id="#win95_label")
    todo_text = UITextBox(
        html_text=selected_todo_html,
        relative_rect=metrics.todo_selected_text_rect,
        manager=manager,
        container=existing_panel,
        object_id="#win95_textbox",
    )
    edit_button = UIButton(metrics.todo_existing_button_rect(0), "Edit", manager, container=existing_panel, object_id="#win95_button")
    copy_button = UIButton(metrics.todo_existing_button_rect(1), "Copy", manager, container=existing_panel, object_id="#win95_button")
    title_label = UILabel(metrics.todo_new_title_rect, "СОЗДАТЬ НОВУЮ ЗАДАЧУ", manager, container=new_panel, object_id="#win95_label")
    entry = UITextEntryBox(
        initial_text="",
        relative_rect=metrics.todo_new_entry_rect,
        manager=manager,
        container=new_panel,
        object_id="#win95_input",
    )
    add_button = UIButton(metrics.todo_add_button_rect, "Add task", manager, container=new_panel, object_id="#win95_button")
    clean_button = UIButton(metrics.todo_clean_button_rect, "Clean", manager, container=new_panel, object_id="#win95_button")
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
