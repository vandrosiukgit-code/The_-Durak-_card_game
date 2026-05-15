from pathlib import Path

import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel, UIPanel

from .config import CARD_HEIGHT, CARD_WIDTH, HEIGHT, WIDTH


class GameUIController:
    def __init__(self, app: "DurakApp") -> None:
        self.app = app
        theme_path = Path(__file__).resolve().parent.parent / "ui_theme" / "theme.json"
        self.manager = pygame_gui.UIManager((WIDTH, HEIGHT), str(theme_path))

        self.actions_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, 170, 300),
            manager=self.manager,
            starting_height=1,
            object_id="#actions_panel",
        )
        self.actions_title = UILabel(
            relative_rect=pygame.Rect(18, 16, 130, 28),
            text="Actions",
            manager=self.manager,
            container=self.actions_panel,
            object_id="#panel_title",
        )
        self.pass_button = UIButton(
            relative_rect=pygame.Rect(30, 86, 110, 34),
            text="Pass",
            manager=self.manager,
            container=self.actions_panel,
            object_id="#action_button",
        )
        self.take_button = UIButton(
            relative_rect=pygame.Rect(30, 142, 110, 34),
            text="Take",
            manager=self.manager,
            container=self.actions_panel,
            object_id="#action_button",
        )
        self.restart_button = UIButton(
            relative_rect=pygame.Rect(30, 198, 110, 34),
            text="Restart",
            manager=self.manager,
            container=self.actions_panel,
            object_id="#action_button",
        )
        self.surrender_button = UIButton(
            relative_rect=pygame.Rect(30, 244, 110, 34),
            text="Surrender",
            manager=self.manager,
            container=self.actions_panel,
            object_id="#danger_button",
        )
        self.modals = None
        self.actions_panel.hide()

    def attach_modals(self, modals) -> None:
        self.modals = modals

    def process_event(self, event: pygame.event.Event) -> bool:
        if event.type != pygame_gui.UI_BUTTON_PRESSED:
            return False

        if self.modals is not None:
            modal_action = self.modals.event_action(event.ui_element)
            if modal_action == "intro_continue":
                self.app.intro_visible = False
                return True
            if modal_action == "endgame_continue":
                self.app.continue_match()
                return True
            if modal_action == "endgame_end":
                self.app.request_quit = True
                return True

        if event.ui_element == self.pass_button:
            if self.app.state and self.app.state.available_actions_for_player()["pass"]:
                self.app.state.pass_action("bottom")
                self.app.selected_card_index = None
                self.app.check_for_new_cards()
                self.app.advance_bots()
            return True

        if event.ui_element == self.take_button:
            if self.app.state and self.app.state.available_actions_for_player()["take"]:
                self.app.state.player_take()
                self.app.selected_card_index = None
                self.app.check_for_new_cards()
                self.app.advance_bots()
            return True

        if event.ui_element == self.restart_button:
            self.app.reset_game()
            return True

        if event.ui_element == self.surrender_button:
            self.app.player_surrender()
            return True

        return False

    def update(self, time_delta: float) -> None:
        self.sync_layout()
        self.sync_visibility()
        self.sync_enabled_states()
        if self.modals is not None:
            self.modals.sync_layout()
            self.modals.sync_content()
            self.modals.sync_visibility()
        self.manager.update(time_delta)

    def draw(self, surface: pygame.Surface) -> None:
        self.manager.draw_ui(surface)

    def sync_layout(self) -> None:
        if self.app.state is not None:
            actions_rect = self.app.table_screen.get_block_rects()["actions_panel"]
            self.actions_panel.set_relative_position((actions_rect.x, actions_rect.y))
            self.actions_panel.set_dimensions((actions_rect.width, actions_rect.height))

    def sync_visibility(self) -> None:
        if self.app.menu_visible or self.app.state is None:
            self.actions_panel.hide()
        elif self.app.intro_visible or self.app.endgame_visible:
            self.actions_panel.hide()
        else:
            self.actions_panel.show()

    def sync_enabled_states(self) -> None:
        if self.app.state is None:
            return

        actions = self.app.state.available_actions_for_player()
        self._set_enabled(self.pass_button, actions["pass"])
        self._set_enabled(self.take_button, actions["take"])
        self._set_enabled(self.restart_button, True)
        self._set_enabled(self.surrender_button, not self.app.state.is_game_over())

    @staticmethod
    def _set_enabled(button: UIButton, enabled: bool) -> None:
        if enabled:
            button.enable()
        else:
            button.disable()

    def point_over_ui(self, pos: tuple[int, int]) -> bool:
        if self.app.menu_visible or self.app.state is None:
            return False

        if self.modals is not None and self.modals.point_over_modal(pos):
            return True

        if not self.app.intro_visible and not self.app.endgame_visible:
            return self.actions_panel.get_abs_rect().collidepoint(pos)
        return False

    def deck_overlay_rect(self) -> pygame.Rect:
        if self.app.state is None:
            return pygame.Rect(0, 0, 0, 0)
        deck_x, deck_y = self.app.table_screen.get_deck_position()
        return pygame.Rect(deck_x, deck_y, CARD_WIDTH, CARD_HEIGHT)
