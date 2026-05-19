from __future__ import annotations

from pathlib import Path

import pygame

from durak_app.app import DurakApp
from durak_app.config import APP_CONFIG_PATH, HEIGHT, WIDTH
from tools.layout_debug.models import LayoutConfigData


class GamePreviewRenderer:
    def __init__(self, shell_window_size: tuple[int, int]) -> None:
        config_text_before_startup = self._read_config_text(APP_CONFIG_PATH)
        self.app = DurakApp(create_display=False)
        config_text_after_startup = self._read_config_text(APP_CONFIG_PATH)
        if config_text_before_startup is not None and config_text_after_startup != config_text_before_startup:
            APP_CONFIG_PATH.write_text(config_text_before_startup, encoding="utf-8")
        self.source_surface = pygame.Surface((WIDTH, HEIGHT))
        self.current_screen_id: str | None = None

    @staticmethod
    def _read_config_text(path: Path) -> str | None:
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            return None

    def configure_screen(self, screen_id: str) -> None:
        self.current_screen_id = screen_id
        self.app.menu_visible = screen_id == "main_menu"
        self.app.reset_game()
        self.app.bot_autoplay_pending = False

        if screen_id == "modal_endgame":
            self._prepare_endgame_preview()
        else:
            self.app.intro_visible = screen_id == "modal_intro"
            self.app.endgame_visible = False

    def _prepare_endgame_preview(self) -> None:
        assert self.app.state is not None
        self.app.intro_visible = False
        self.app.endgame_visible = True
        self.app.current_game_number = 2
        self.app.losses_to_finish = 3
        self.app.durak_counts = {"left": 1, "top": 0, "right": 2, "bottom": 1}
        self.app.match_complete = False
        self.app.state.phase = "game_over"
        self.app.state.turn_number = 8
        self.app.state.discard_count = 22
        self.app.state.loser_seat = "right"
        self.app.state.winner_seats = ["bottom", "left", "top"]
        self.app.state.last_result = "Bot Right is the durak."

    def render(
        self,
        target_surface: pygame.Surface,
        target_rect: pygame.Rect,
        screen_id: str,
        layout: LayoutConfigData,
        canvas_mouse_pos: tuple[int, int],
        source_rect: pygame.Rect | None = None,
    ) -> None:
        if self.current_screen_id != screen_id:
            self.configure_screen(screen_id)

        self.app.app_config.data["layout"] = layout
        self.app.render_frame(
            self.source_surface,
            canvas_mouse_pos,
            time_delta=0.0,
            advance_animations=False,
            update_display=False,
        )

        source_surface = self.source_surface.subsurface(source_rect) if source_rect is not None else self.source_surface
        scaled = pygame.transform.smoothscale(source_surface, target_rect.size)
        target_surface.blit(scaled, target_rect)
