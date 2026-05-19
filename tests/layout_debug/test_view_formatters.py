from __future__ import annotations

import unittest

from tools.layout_debug.models import LayoutObject
from tools.layout_debug.view_formatters import NavigatorViewFormatter, TodoViewFormatter


class NavigatorViewFormatterTests(unittest.TestCase):
    def test_empty_navigator_html_keeps_screen_and_empty_message(self) -> None:
        html_text = NavigatorViewFormatter().html("game_table", [], None, None)

        self.assertIn("<b>game_table</b>", html_text)
        self.assertIn("Нет layout-объектов.", html_text)

    def test_navigator_html_marks_selected_hover_and_todo(self) -> None:
        layout_objects = [
            _layout_object("button", "pass_button", todo_text="Передвинуть"),
            _layout_object("panel", "player_left_panel", delta_x=4, delta_y=-2),
        ]

        html_text = NavigatorViewFormatter().html(
            "game_table",
            layout_objects,
            selected_object_id="pass_button",
            hover_object_id="player_left_panel",
        )

        self.assertIn("<b>button</b>", html_text)
        self.assertIn("pass_button SELECTED TODO", html_text)
        self.assertIn("player_left_panel HOVER", html_text)
        self.assertIn("dx:4 dy:-2 dw:0 dh:0", html_text)

    def test_navigator_html_escapes_object_id(self) -> None:
        html_text = NavigatorViewFormatter().html(
            "game_table",
            [_layout_object("label", "name<label>")],
            selected_object_id=None,
            hover_object_id=None,
        )

        self.assertIn("name&lt;label&gt;", html_text)
        self.assertNotIn("name<label>", html_text)

    def test_navigator_selection_items_keep_object_mapping(self) -> None:
        items, object_ids_by_label = NavigatorViewFormatter().selection_items(
            "game_table",
            [
                _layout_object("button", "pass_button", todo_text="todo"),
                _layout_object("panel", "player_left_panel"),
            ],
            selected_object_id="pass_button",
            hover_object_id="player_left_panel",
        )

        self.assertEqual(len(items), 3)
        self.assertIn(("game_table", "#navigator_group_item"), items)
        self.assertIn(("    player_left_panel", "#navigator_child_hover_item"), items)
        self.assertIn(("    pass_button todo", "#navigator_child_item"), items)
        self.assertEqual(object_ids_by_label["    pass_button todo"], "pass_button")

    def test_navigator_selection_items_follow_game_table_tree_order(self) -> None:
        items, _object_ids_by_label = NavigatorViewFormatter().selection_items(
            "game_table",
            [
                _layout_object("button", "pass_button"),
                _layout_object("panel", "table_area"),
                _layout_object("card_zone", "deck_panel"),
            ],
            selected_object_id=None,
            hover_object_id=None,
        )

        self.assertEqual(items, [
            ("game_table", "#navigator_group_item"),
            ("    table_area", "#navigator_child_item"),
            ("        - deck_panel", "#navigator_child_item"),
            ("    pass_button", "#navigator_child_item"),
        ])

    def test_navigator_selection_items_can_focus_on_tree_branch(self) -> None:
        items, object_ids_by_label = NavigatorViewFormatter().selection_items(
            "game_table",
            [
                _layout_object("panel", "table_area"),
                _layout_object("card_zone", "deck_panel"),
                _layout_object("card_zone", "trump_panel"),
                _layout_object("panel", "actions_panel"),
                _layout_object("button", "pass_button"),
            ],
            selected_object_id="deck_panel",
            hover_object_id="trump_panel",
            focus_object_id="table_area",
        )

        self.assertEqual(items, [
            ("Focus: table_area", "#navigator_focus_status_item"),
            ("game_table", "#navigator_group_item"),
            ("    table_area", "#navigator_child_item"),
            ("        - deck_panel", "#navigator_child_item"),
            ("        - trump_panel", "#navigator_child_hover_item"),
        ])
        self.assertNotIn("Focus: table_area", object_ids_by_label)
        self.assertNotIn("game_table", object_ids_by_label)
        self.assertEqual(object_ids_by_label["        - deck_panel"], "deck_panel")

    def test_navigator_selection_items_ignore_unknown_focus_object(self) -> None:
        items, _object_ids_by_label = NavigatorViewFormatter().selection_items(
            "game_table",
            [
                _layout_object("panel", "table_area"),
            ],
            selected_object_id=None,
            hover_object_id=None,
            focus_object_id="missing_object",
        )

        self.assertEqual(items, [
            ("game_table", "#navigator_group_item"),
            ("    table_area", "#navigator_child_item"),
        ])

    def test_navigator_selection_items_group_game_ui_objects(self) -> None:
        items, object_ids_by_label = NavigatorViewFormatter().selection_items(
            "game_table",
            [
                _layout_object("panel", "table_area"),
                _layout_object("label", "title_label", layout_screen_id="game_ui"),
                _layout_object("label", "subtitle_label", layout_screen_id="game_ui"),
            ],
            selected_object_id=None,
            hover_object_id="title_label",
        )

        self.assertEqual(items, [
            ("game_table", "#navigator_group_item"),
            ("    table_area", "#navigator_child_item"),
            ("game_ui", "#navigator_group_item"),
            ("    title_label", "#navigator_child_hover_item"),
            ("    subtitle_label", "#navigator_child_item"),
        ])
        self.assertNotIn("game_ui", object_ids_by_label)
        self.assertEqual(object_ids_by_label["    title_label"], "title_label")


class TodoViewFormatterTests(unittest.TestCase):
    def test_selected_html_keeps_russian_text_and_line_breaks(self) -> None:
        html_text = TodoViewFormatter().selected_html(
            _layout_object("hand_zone", "bottom_hand_area", todo_text="Это тестовая задача!\nПоднять выше.")
        )

        self.assertIn("<b>game_table.bottom_hand_area</b>", html_text)
        self.assertIn("Это тестовая задача!<br>Поднять выше.", html_text)

    def test_selected_html_escapes_task_text(self) -> None:
        html_text = TodoViewFormatter().selected_html(
            _layout_object("label", "name_label", todo_text="A < B")
        )

        self.assertIn("A &lt; B", html_text)
        self.assertNotIn("A < B", html_text)

    def test_selected_html_handles_empty_selection(self) -> None:
        html_text = TodoViewFormatter().selected_html(None)

        self.assertEqual(html_text, "<font face=consolas size=3>Задача не выбрана.</font>")


def _layout_object(
    object_type: str,
    object_id: str,
    delta_x: int = 0,
    delta_y: int = 0,
    todo_text: str = "",
    layout_screen_id: str = "game_table",
) -> LayoutObject:
    return LayoutObject(
        screen_id="game_table",
        object_id=object_id,
        path=f"{layout_screen_id}.{object_id}",
        layout_screen_id=layout_screen_id,
        layout_key=f"{layout_screen_id}.{object_id}",
        object_type=object_type,
        x=0,
        y=0,
        width=100,
        height=40,
        delta_x=delta_x,
        delta_y=delta_y,
        width_delta=0,
        height_delta=0,
        color="",
        font="",
        font_size=0,
        todo_text=todo_text,
    )


if __name__ == "__main__":
    unittest.main()
