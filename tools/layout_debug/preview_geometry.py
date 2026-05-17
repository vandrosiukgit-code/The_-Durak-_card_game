from __future__ import annotations

import pygame

from durak_app.config import (
    BOT_CARD_HEIGHT,
    BOT_CARD_WIDTH,
    BOTTOM_ZONE_HEIGHT,
    BOTTOM_ZONE_TOP,
    CARD_HEIGHT,
    CARD_WIDTH,
    HEIGHT,
    SIDE_ZONE_TOP,
    TABLE_RECT,
    WIDTH,
)
from tools.layout_debug.models import LayoutObject


class PreviewGeometryProvider:
    def build_preview_rects(
        self,
        screen_id: str,
        layout_objects: list[LayoutObject],
    ) -> dict[str, pygame.Rect]:
        objects_by_id = {layout_object.object_id: layout_object for layout_object in layout_objects}
        if screen_id == "game_table":
            return self._game_table_preview_rects(objects_by_id)
        if screen_id == "main_menu":
            return self._main_menu_preview_rects(objects_by_id)
        if screen_id == "modal_intro":
            return self._modal_intro_preview_rects(objects_by_id)
        if screen_id == "modal_endgame":
            return self._modal_endgame_preview_rects(objects_by_id)
        return {}

    def layout_rect(
        self,
        objects_by_id: dict[str, LayoutObject],
        object_id: str,
        rect: pygame.Rect,
    ) -> pygame.Rect:
        layout_object = objects_by_id.get(object_id)
        moved = rect.copy()
        if layout_object is None:
            return moved
        moved.x += layout_object.delta_x
        moved.y += layout_object.delta_y
        moved.width = max(12, moved.width + layout_object.width_delta)
        moved.height = max(12, moved.height + layout_object.height_delta)
        return moved

    def _game_table_preview_rects(self, objects_by_id: dict[str, LayoutObject]) -> dict[str, pygame.Rect]:
        table_rect = self.layout_rect(objects_by_id, "table_area", TABLE_RECT)
        left_rect = self.layout_rect(objects_by_id, "player_left_panel", pygame.Rect(32, SIDE_ZONE_TOP, 170, 620))
        top_rect = self.layout_rect(objects_by_id, "player_top_panel", pygame.Rect(WIDTH // 2 - 420, 20, 800, 160))
        right_rect = self.layout_rect(objects_by_id, "player_right_panel", pygame.Rect(WIDTH - 202, SIDE_ZONE_TOP, 170, 620))
        bottom_rect = self.layout_rect(
            objects_by_id,
            "player_bottom_panel",
            pygame.Rect(WIDTH // 2 - 546, BOTTOM_ZONE_TOP + 82, 1092, BOTTOM_ZONE_HEIGHT - 96),
        )
        deck_rect = self.layout_rect(objects_by_id, "deck_panel", pygame.Rect(TABLE_RECT.right - CARD_WIDTH - 80, 190, CARD_WIDTH, CARD_HEIGHT))
        trump_rect = self.layout_rect(objects_by_id, "trump_panel", pygame.Rect(deck_rect.x, deck_rect.y + 40, CARD_HEIGHT, CARD_WIDTH))

        panel_width = 170
        panel_height = 300
        gap_width = deck_rect.x - table_rect.right - panel_width
        panel_x = table_rect.right + max(0, gap_width // 2)
        actions_rect = self.layout_rect(objects_by_id, "actions_panel", pygame.Rect(panel_x, deck_rect.y, panel_width, panel_height))
        table_cards_rect = self.layout_rect(objects_by_id, "table_cards_area", pygame.Rect(WIDTH // 2 - 500, 190, 560, 310))

        left_hand_rect = self.layout_rect(
            objects_by_id,
            "left_hand_area",
            pygame.Rect(left_rect.x + 12, left_rect.y + 224, BOT_CARD_WIDTH + 52, 9 * 25 + BOT_CARD_HEIGHT),
        )
        top_hand_rect = self.layout_rect(objects_by_id, "top_hand_area", pygame.Rect(top_rect.x + 250, top_rect.y + 20, 260, 118))
        right_hand_rect = self.layout_rect(
            objects_by_id,
            "right_hand_area",
            pygame.Rect(right_rect.x + 12, right_rect.y + 224, BOT_CARD_WIDTH + 52, 9 * 25 + BOT_CARD_HEIGHT),
        )
        bottom_hand_rect = self.layout_rect(
            objects_by_id,
            "bottom_hand_area",
            pygame.Rect(bottom_rect.x + 190, bottom_rect.bottom - CARD_HEIGHT - 35, bottom_rect.width - 230, CARD_HEIGHT + 55),
        )
        return {
            "table_area": table_rect,
            "table_cards_area": table_cards_rect,
            "player_left_panel": left_rect,
            "player_top_panel": top_rect,
            "player_right_panel": right_rect,
            "player_bottom_panel": bottom_rect,
            "left_hand_area": left_hand_rect,
            "top_hand_area": top_hand_rect,
            "right_hand_area": right_hand_rect,
            "bottom_hand_area": bottom_hand_rect,
            "deck_panel": deck_rect,
            "trump_panel": trump_rect,
            "actions_panel": actions_rect,
        }

    def _main_menu_preview_rects(self, objects_by_id: dict[str, LayoutObject]) -> dict[str, pygame.Rect]:
        root_w, root_h = 1024, 840
        root_x, root_y = (WIDTH - root_w) // 2, (HEIGHT - root_h) // 2
        root_rect = self.layout_rect(objects_by_id, "menu_root", pygame.Rect(root_x, root_y, root_w, root_h))
        deck_rect = self.layout_rect(objects_by_id, "deck_panel", pygame.Rect(root_rect.x + 32, root_rect.y + 80, 960, 360))
        game_rect = self.layout_rect(objects_by_id, "game_settings_panel", pygame.Rect(root_rect.x + 32, deck_rect.bottom + 20, 960, 270))
        start_rect = self.layout_rect(objects_by_id, "start_button", pygame.Rect(root_rect.x + (root_rect.width - 240) // 2, game_rect.bottom + 25, 240, 50))
        exit_rect = self.layout_rect(objects_by_id, "exit_button", pygame.Rect(start_rect.right + 20, start_rect.y, 180, 50))
        return {
            "menu_root": root_rect,
            "deck_panel": deck_rect,
            "game_settings_panel": game_rect,
            "start_button": start_rect,
            "exit_button": exit_rect,
        }

    def _modal_intro_preview_rects(self, objects_by_id: dict[str, LayoutObject]) -> dict[str, pygame.Rect]:
        panel_rect = self.layout_rect(objects_by_id, "panel", pygame.Rect(WIDTH // 2 - 290, HEIGHT // 2 - 190, 580, 380))
        return {
            "overlay": self.layout_rect(objects_by_id, "overlay", pygame.Rect(0, 0, WIDTH, HEIGHT)),
            "panel": panel_rect,
            "title": self.layout_rect(objects_by_id, "title", pygame.Rect(panel_rect.x + 34, panel_rect.y + 24, 500, 40)),
            "trump_label": self.layout_rect(objects_by_id, "trump_label", pygame.Rect(panel_rect.x + 36, panel_rect.y + 82, 500, 24)),
            "tips_section": self.layout_rect(objects_by_id, "tips_section", pygame.Rect(panel_rect.x + 36, panel_rect.y + 184, 200, 28)),
            "continue_button": self.layout_rect(objects_by_id, "continue_button", pygame.Rect(panel_rect.x + (panel_rect.width - 140) // 2, panel_rect.y + panel_rect.height - 70, 140, 42)),
        }

    def _modal_endgame_preview_rects(self, objects_by_id: dict[str, LayoutObject]) -> dict[str, pygame.Rect]:
        panel_rect = self.layout_rect(objects_by_id, "panel", pygame.Rect(WIDTH // 2 - 330, HEIGHT // 2 - 250, 660, 500))
        return {
            "overlay": self.layout_rect(objects_by_id, "overlay", pygame.Rect(0, 0, WIDTH, HEIGHT)),
            "panel": panel_rect,
            "title": self.layout_rect(objects_by_id, "title", pygame.Rect(panel_rect.x + 34, panel_rect.y + 24, 560, 42)),
            "loser_name": self.layout_rect(objects_by_id, "loser_name", pygame.Rect(panel_rect.x + 36, panel_rect.y + 132, 320, 30)),
            "score_panel": self.layout_rect(objects_by_id, "score_panel", pygame.Rect(panel_rect.x + 36, panel_rect.y + 258, panel_rect.width - 72, 134)),
            "continue_button": self.layout_rect(objects_by_id, "continue_button", pygame.Rect(panel_rect.x + panel_rect.width // 2 - 220, panel_rect.y + panel_rect.height - 72, 180, 42)),
            "end_button": self.layout_rect(objects_by_id, "end_button", pygame.Rect(panel_rect.x + panel_rect.width // 2 + 40, panel_rect.y + panel_rect.height - 72, 180, 42)),
        }


class PreviewViewportMapper:
    def __init__(self, canvas_size: tuple[int, int]) -> None:
        self.canvas_size = canvas_size

    def viewport_for_panel(self, panel_rect: pygame.Rect) -> pygame.Rect:
        panel_rect = panel_rect.inflate(-24, -56)
        panel_rect.y += 22
        ratio = self.canvas_size[0] / self.canvas_size[1]
        if panel_rect.width / panel_rect.height > ratio:
            height = panel_rect.height
            width = int(height * ratio)
        else:
            width = panel_rect.width
            height = int(width / ratio)
        return pygame.Rect(
            panel_rect.x + (panel_rect.width - width) // 2,
            panel_rect.y + (panel_rect.height - height) // 2,
            width,
            height,
        )

    def canvas_to_viewport_rect(self, rect: pygame.Rect, viewport: pygame.Rect) -> pygame.Rect:
        scale_x = viewport.width / self.canvas_size[0]
        scale_y = viewport.height / self.canvas_size[1]
        return pygame.Rect(
            viewport.x + int(rect.x * scale_x),
            viewport.y + int(rect.y * scale_y),
            max(1, int(rect.width * scale_x)),
            max(1, int(rect.height * scale_y)),
        )

    def viewport_to_canvas_pos(self, pos: tuple[int, int], viewport: pygame.Rect) -> tuple[int, int] | None:
        if not viewport.collidepoint(pos):
            return None
        scale_x = self.canvas_size[0] / viewport.width
        scale_y = self.canvas_size[1] / viewport.height
        return int((pos[0] - viewport.x) * scale_x), int((pos[1] - viewport.y) * scale_y)


def object_at_canvas_pos(
    pos: tuple[int, int],
    preview_rects: dict[str, pygame.Rect],
) -> str | None:
    hit_items = [
        (object_id, rect)
        for object_id, rect in preview_rects.items()
        if rect.collidepoint(pos)
    ]
    if not hit_items:
        return None
    hit_items.sort(key=lambda item: item[1].width * item[1].height)
    return hit_items[0][0]
