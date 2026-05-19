from __future__ import annotations

import unittest

from tools.layout_debug.models import LayoutObject
from tools.layout_debug.navigator_tree import NavigatorTreeBuilder


class NavigatorTreeBuilderTests(unittest.TestCase):
    def test_builds_known_parent_child_group(self) -> None:
        tree = NavigatorTreeBuilder().build(
            "game_table",
            [
                _layout_object("card_zone", "deck_panel"),
                _layout_object("panel", "table_area"),
            ],
        )

        self.assertEqual([node.object_id for node in tree.roots], ["game_table"])
        self.assertEqual([node.object_id for node in tree.roots[0].children], ["table_area"])
        self.assertEqual([node.object_id for node in tree.roots[0].children[0].children], ["deck_panel"])
        self.assertIs(tree.nodes_by_object_id["deck_panel"].parent, tree.nodes_by_object_id["table_area"])
        self.assertEqual(tree.nodes_by_object_id["deck_panel"].level, 2)

    def test_flatten_keeps_visual_tree_order(self) -> None:
        tree = NavigatorTreeBuilder().build(
            "game_table",
            [
                _layout_object("button", "pass_button"),
                _layout_object("panel", "actions_panel"),
                _layout_object("panel", "table_area"),
                _layout_object("card_zone", "deck_panel"),
            ],
        )

        self.assertEqual(
            [(node.level, node.object_id) for node in tree.flatten()],
            [
                (0, "game_table"),
                (1, "table_area"),
                (2, "deck_panel"),
                (1, "actions_panel"),
                (2, "pass_button"),
            ],
        )

    def test_unknown_objects_become_sorted_fallback_roots(self) -> None:
        tree = NavigatorTreeBuilder().build(
            "game_table",
            [
                _layout_object("z_type", "z_unknown"),
                _layout_object("a_type", "a_unknown"),
            ],
        )

        self.assertEqual(
            [(node.level, node.object_id) for node in tree.flatten()],
            [
                (0, "game_table"),
                (1, "a_unknown"),
                (1, "z_unknown"),
            ],
        )

    def test_path_to_returns_root_to_object_chain(self) -> None:
        tree = NavigatorTreeBuilder().build(
            "game_table",
            [
                _layout_object("panel", "table_area"),
                _layout_object("card_zone", "deck_panel"),
            ],
        )

        self.assertEqual(
            [node.object_id for node in tree.path_to("deck_panel")],
            ["game_table", "table_area", "deck_panel"],
        )

    def test_path_to_returns_empty_list_for_unknown_object(self) -> None:
        tree = NavigatorTreeBuilder().build(
            "game_table",
            [
                _layout_object("panel", "table_area"),
            ],
        )

        self.assertEqual(tree.path_to("missing_object"), [])

    def test_descendants_of_returns_children_in_visual_order(self) -> None:
        tree = NavigatorTreeBuilder().build(
            "game_table",
            [
                _layout_object("panel", "actions_panel"),
                _layout_object("button", "pass_button"),
                _layout_object("button", "take_button"),
            ],
        )

        self.assertEqual(
            [node.object_id for node in tree.descendants_of("actions_panel")],
            ["pass_button", "take_button"],
        )

    def test_game_table_groups_game_ui_objects(self) -> None:
        tree = NavigatorTreeBuilder().build(
            "game_table",
            [
                _layout_object("panel", "table_area"),
                _layout_object("label", "title_label", layout_screen_id="game_ui"),
                _layout_object("label", "subtitle_label", layout_screen_id="game_ui"),
            ],
        )

        self.assertEqual([node.object_id for node in tree.roots], ["game_table", "game_ui"])
        self.assertTrue(tree.roots[0].is_group)
        self.assertTrue(tree.roots[1].is_group)
        self.assertEqual([node.object_id for node in tree.roots[1].children], ["title_label", "subtitle_label"])
        self.assertNotIn("game_ui", tree.nodes_by_object_id)
        self.assertEqual(tree.nodes_by_object_id["title_label"].layout_object.layout_screen_id, "game_ui")

    def test_descendants_of_leaf_returns_empty_list(self) -> None:
        tree = NavigatorTreeBuilder().build(
            "game_table",
            [
                _layout_object("panel", "actions_panel"),
                _layout_object("button", "pass_button"),
            ],
        )

        self.assertEqual(tree.descendants_of("pass_button"), [])

    def test_descendants_of_unknown_object_returns_empty_list(self) -> None:
        tree = NavigatorTreeBuilder().build(
            "game_table",
            [
                _layout_object("panel", "actions_panel"),
            ],
        )

        self.assertEqual(tree.descendants_of("missing_object"), [])


def _layout_object(object_type: str, object_id: str, layout_screen_id: str = "game_table") -> LayoutObject:
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
        delta_x=0,
        delta_y=0,
        width_delta=0,
        height_delta=0,
        color="",
        font="",
        font_size=0,
        todo_text="",
    )


if __name__ == "__main__":
    unittest.main()
