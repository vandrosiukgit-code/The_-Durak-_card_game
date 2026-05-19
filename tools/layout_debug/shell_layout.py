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

    def section_title_panel_rect(self, width: int) -> pygame.Rect:
        return pygame.Rect(1, 1, width, 22)

    def section_title_label_rect(self, width: int) -> pygame.Rect:
        return pygame.Rect(8, 1, width - 16, 18)

    @property
    def context_screen_label_rect(self) -> pygame.Rect:
        return pygame.Rect(12, 34, 58, 24)

    @property
    def context_screen_dropdown_rect(self) -> pygame.Rect:
        return pygame.Rect(self.context_rect.x + 72, self.context_rect.y + 32, 220, 28)

    @property
    def context_status_label_rect(self) -> pygame.Rect:
        return pygame.Rect(312, 34, 210, 24)

    @property
    def context_apply_button_rect(self) -> pygame.Rect:
        return pygame.Rect(1198, 32, 108, 28)

    @property
    def context_reset_button_rect(self) -> pygame.Rect:
        return pygame.Rect(1316, 32, 138, 28)

    @property
    def context_help_button_rect(self) -> pygame.Rect:
        return pygame.Rect(1464, 32, 92, 28)

    @property
    def navigator_body_rect(self) -> pygame.Rect:
        return pygame.Rect(10, 34, self.navigator_rect.width - 42, self.navigator_rect.height - 66)

    @property
    def status_label_rect(self) -> pygame.Rect:
        return pygame.Rect(8, 2, self.window_size[0] - 32, 20)

    @property
    def inspector_object_label_rect(self) -> pygame.Rect:
        return pygame.Rect(self.inspector_content_x, 34, 300, 22)

    @property
    def inspector_type_label_rect(self) -> pygame.Rect:
        return pygame.Rect(self.inspector_content_x, 60, 300, 22)

    def inspector_group_rect(self, y: int, height: int) -> pygame.Rect:
        return pygame.Rect(self.inspector_group_x, y, self.inspector_group_width, height)

    @property
    def inspector_group_title_rect(self) -> pygame.Rect:
        return pygame.Rect(8, 6, 140, 16)

    def inspector_field_label_rect(self, x: int, y: int, width: int) -> pygame.Rect:
        return pygame.Rect(x, y, width - 4, 16)

    def inspector_field_input_rect(self, x: int, y: int, width: int) -> pygame.Rect:
        return pygame.Rect(x, y, width, 16)

    @property
    def inspector_control_title_rect(self) -> pygame.Rect:
        return pygame.Rect(8, 8, 120, 16)

    @property
    def inspector_step_label_rect(self) -> pygame.Rect:
        return pygame.Rect(8, 32, 42, 16)

    @property
    def inspector_step_input_rect(self) -> pygame.Rect:
        return pygame.Rect(56, 30, 58, 20)

    @property
    def inspector_move_label_rect(self) -> pygame.Rect:
        return pygame.Rect(8, 62, 50, 16)

    def inspector_move_button_rect(self, index: int) -> pygame.Rect:
        return pygame.Rect(62 + index * 42, 58, 36, 24)

    @property
    def inspector_size_label_rect(self) -> pygame.Rect:
        return pygame.Rect(8, 96, 42, 16)

    def inspector_size_button_rect(self, index: int) -> pygame.Rect:
        return pygame.Rect(62 + index * 42, 92, 36, 24)

    @property
    def inspector_dismiss_button_rect(self) -> pygame.Rect:
        return pygame.Rect(10, self.inspector_action_y, 94, 24)

    @property
    def inspector_cancel_button_rect(self) -> pygame.Rect:
        return pygame.Rect(114, self.inspector_action_y, 86, 24)

    @property
    def inspector_copy_id_button_rect(self) -> pygame.Rect:
        return pygame.Rect(210, self.inspector_action_y, 106, 24)

    @property
    def todo_existing_panel_rect(self) -> pygame.Rect:
        return pygame.Rect(8, 34, 760, 188)

    @property
    def todo_new_panel_rect(self) -> pygame.Rect:
        return pygame.Rect(778, 34, 790, 188)

    @property
    def todo_existing_title_rect(self) -> pygame.Rect:
        return pygame.Rect(8, 12, 300, 18)

    @property
    def todo_list_rect(self) -> pygame.Rect:
        return pygame.Rect(8, 36, 286, 116)

    @property
    def todo_selected_title_rect(self) -> pygame.Rect:
        return pygame.Rect(330, 12, 386, 18)

    @property
    def todo_selected_text_rect(self) -> pygame.Rect:
        return pygame.Rect(330, 36, 386, 116)

    def todo_existing_button_rect(self, index: int) -> pygame.Rect:
        return pygame.Rect(407 + index * 124, 160, 112, 22)

    @property
    def todo_new_title_rect(self) -> pygame.Rect:
        return pygame.Rect(8, 12, 360, 18)

    @property
    def todo_new_entry_rect(self) -> pygame.Rect:
        return pygame.Rect(8, 36, 600, 138)

    @property
    def todo_add_button_rect(self) -> pygame.Rect:
        return pygame.Rect(628, 68, 128, 30)

    @property
    def todo_clean_button_rect(self) -> pygame.Rect:
        return pygame.Rect(628, 112, 128, 30)

    @property
    def status_rect(self) -> pygame.Rect:
        return pygame.Rect(4, self.window_size[1] - 28, self.window_size[0] - 8, 24)


SHELL_LAYOUT = ShellLayoutMetrics()
