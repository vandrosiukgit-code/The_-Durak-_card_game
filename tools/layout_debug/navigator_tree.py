from __future__ import annotations

from dataclasses import dataclass, field

from tools.layout_debug.models import LayoutObject


TREE_ORDER: dict[str, tuple[tuple[str, ...], ...]] = {
    "game_table": (
        ("table_area", "table_cards_area", "deck_panel", "trump_panel"),
        ("player_left_panel", "left_hand_area", "left_name_label", "left_role_label", "left_loss_label"),
        ("player_top_panel", "top_hand_area", "top_name_label", "top_role_label", "top_loss_label"),
        ("player_right_panel", "right_hand_area", "right_name_label", "right_role_label", "right_loss_label"),
        ("player_bottom_panel", "bottom_hand_area", "bottom_name_label", "bottom_role_label", "bottom_loss_label"),
        ("actions_panel", "pass_button", "take_button", "restart_button", "surrender_button"),
    ),
    "game_ui": (
        ("title_label",),
        ("subtitle_label",),
        ("attacker_label",),
        ("meta_label",),
        ("party_meta_label",),
    ),
    "main_menu": (
        ("menu_root", "deck_panel", "game_settings_panel", "start_button", "exit_button"),
    ),
    "modal_intro": (
        ("overlay", "panel", "title", "trump_label", "tips_section", "continue_button"),
    ),
    "modal_endgame": (
        ("overlay", "panel", "title", "loser_name", "score_panel", "continue_button", "end_button"),
    ),
}


@dataclass
class NavigatorTreeNode:
    object_id: str
    level: int
    layout_object: LayoutObject | None = None
    parent: "NavigatorTreeNode | None" = None
    children: list["NavigatorTreeNode"] = field(default_factory=list)

    @property
    def is_group(self) -> bool:
        return self.layout_object is None


class NavigatorTree:
    def __init__(self, roots: list[NavigatorTreeNode]) -> None:
        self.roots = roots
        self.nodes_by_object_id: dict[str, NavigatorTreeNode] = {}
        for node in self.flatten():
            if not node.is_group:
                self.nodes_by_object_id[node.object_id] = node

    def flatten(self) -> list[NavigatorTreeNode]:
        ordered: list[NavigatorTreeNode] = []
        for root in self.roots:
            self._append_subtree(root, ordered)
        return ordered

    def _append_subtree(self, node: NavigatorTreeNode, ordered: list[NavigatorTreeNode]) -> None:
        ordered.append(node)
        for child in node.children:
            self._append_subtree(child, ordered)

    def path_to(self, object_id: str) -> list[NavigatorTreeNode]:
        node = self.nodes_by_object_id.get(object_id)
        if node is None:
            return []
        path: list[NavigatorTreeNode] = []
        current: NavigatorTreeNode | None = node
        while current is not None:
            path.append(current)
            current = current.parent
        path.reverse()
        return path

    def descendants_of(self, object_id: str) -> list[NavigatorTreeNode]:
        node = self.nodes_by_object_id.get(object_id)
        if node is None:
            return []
        descendants: list[NavigatorTreeNode] = []
        for child in node.children:
            self._append_subtree(child, descendants)
        return descendants


class NavigatorTreeBuilder:
    def build(self, screen_id: str, layout_objects: list[LayoutObject]) -> NavigatorTree:
        if screen_id == "game_table":
            return self._build_game_table_tree(layout_objects)
        return self._build_single_screen_tree(screen_id, layout_objects)

    def _build_game_table_tree(self, layout_objects: list[LayoutObject]) -> NavigatorTree:
        table_objects = [
            layout_object
            for layout_object in layout_objects
            if layout_object.layout_screen_id == "game_table"
        ]
        ui_objects = [
            layout_object
            for layout_object in layout_objects
            if layout_object.layout_screen_id == "game_ui"
        ]
        roots: list[NavigatorTreeNode] = []
        table_group = self._build_group_node("game_table", table_objects, TREE_ORDER["game_table"])
        if table_group is not None:
            roots.append(table_group)
        ui_group = self._build_group_node("game_ui", ui_objects, TREE_ORDER["game_ui"])
        if ui_group is not None:
            roots.append(ui_group)
        other_roots = self._fallback_roots(
            [
                layout_object
                for layout_object in layout_objects
                if layout_object.layout_screen_id not in {"game_table", "game_ui"}
            ],
            set(),
            level=0,
        )
        roots.extend(other_roots)
        return NavigatorTree(roots)

    def _build_single_screen_tree(self, screen_id: str, layout_objects: list[LayoutObject]) -> NavigatorTree:
        objects_by_id = {layout_object.object_id: layout_object for layout_object in layout_objects}
        roots: list[NavigatorTreeNode] = []
        used_object_ids: set[str] = set()
        for group in TREE_ORDER.get(screen_id, ()):
            root = self._build_known_group(group, objects_by_id, used_object_ids, level=0, parent=None)
            if root is not None:
                roots.append(root)

        roots.extend(self._fallback_roots(layout_objects, used_object_ids, level=0))
        return NavigatorTree(roots)

    def _build_group_node(
        self,
        group_id: str,
        layout_objects: list[LayoutObject],
        tree_order: tuple[tuple[str, ...], ...],
    ) -> NavigatorTreeNode | None:
        if not layout_objects:
            return None
        group_node = NavigatorTreeNode(object_id=group_id, level=0)
        objects_by_id = {layout_object.object_id: layout_object for layout_object in layout_objects}
        used_object_ids: set[str] = set()
        for group in tree_order:
            root = self._build_known_group(group, objects_by_id, used_object_ids, level=1, parent=group_node)
            if root is not None:
                group_node.children.append(root)
        group_node.children.extend(self._fallback_roots(layout_objects, used_object_ids, level=1, parent=group_node))
        return group_node

    def _build_known_group(
        self,
        group: tuple[str, ...],
        objects_by_id: dict[str, LayoutObject],
        used_object_ids: set[str],
        level: int,
        parent: NavigatorTreeNode | None,
    ) -> NavigatorTreeNode | None:
        root: NavigatorTreeNode | None = None
        for index, object_id in enumerate(group):
            layout_object = objects_by_id.get(object_id)
            if layout_object is None:
                continue
            if root is None:
                root = NavigatorTreeNode(
                    object_id=object_id,
                    level=level,
                    layout_object=layout_object,
                    parent=parent,
                )
                used_object_ids.add(object_id)
                continue
            child = NavigatorTreeNode(
                object_id=object_id,
                level=level + 1,
                layout_object=layout_object,
                parent=root,
            )
            root.children.append(child)
            used_object_ids.add(object_id)
        return root

    def _fallback_roots(
        self,
        layout_objects: list[LayoutObject],
        used_object_ids: set[str],
        level: int,
        parent: NavigatorTreeNode | None = None,
    ) -> list[NavigatorTreeNode]:
        fallback_objects = [
            layout_object
            for layout_object in layout_objects
            if layout_object.object_id not in used_object_ids
        ]
        fallback_objects.sort(key=lambda item: (item.object_type, item.object_id))
        return [
            NavigatorTreeNode(
                object_id=layout_object.object_id,
                level=level,
                layout_object=layout_object,
                parent=parent,
            )
            for layout_object in fallback_objects
        ]
