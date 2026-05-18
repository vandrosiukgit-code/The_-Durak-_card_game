from __future__ import annotations

from dataclasses import dataclass, field

import pygame


@dataclass(frozen=True)
class ShellLayoutMetrics:
    window_size: tuple[int, int] = (1600, 940)
    game_canvas_size: tuple[int, int] = (1600, 900)

    context_rect: pygame.Rect = field(default_factory=lambda: pygame.Rect(12, 8, 1576, 104))
    navigator_rect: pygame.Rect = field(default_factory=lambda: pygame.Rect(12, 122, 264, 540))
    inspector_rect: pygame.Rect = field(default_factory=lambda: pygame.Rect(284, 122, 330, 540))
    preview_rect: pygame.Rect = field(default_factory=lambda: pygame.Rect(622, 122, 966, 540))
    todo_rect: pygame.Rect = field(default_factory=lambda: pygame.Rect(12, 672, 1576, 232))

    inspector_content_x: int = 10
    inspector_group_x: int = 8
    inspector_group_width: int = 314
    inspector_action_y: int = 506
    inspector_group_height: int = 78
    inspector_control_height: int = 130

    @property
    def status_rect(self) -> pygame.Rect:
        return pygame.Rect(4, self.window_size[1] - 28, self.window_size[0] - 8, 24)


SHELL_LAYOUT = ShellLayoutMetrics()
