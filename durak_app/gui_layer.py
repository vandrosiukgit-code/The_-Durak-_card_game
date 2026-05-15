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

        self.title_label = UILabel(
            relative_rect=pygame.Rect(36, 20, 240, 46),
            text="Durak",
            manager=self.manager,
            object_id="#game_title_label",
        )
        self.subtitle_label = UILabel(
            relative_rect=pygame.Rect(40, 66, 260, 28),
            text="Classic throw-in Durak",
            manager=self.manager,
            object_id="#game_subtitle_label",
        )
        self.attacker_label = UILabel(
            relative_rect=pygame.Rect(720, 28, 560, 30),
            text="",
            manager=self.manager,
            object_id="#game_info_label",
        )
        self.meta_label = UILabel(
            relative_rect=pygame.Rect(720, 64, 560, 24),
            text="",
            manager=self.manager,
            object_id="#game_meta_label",
        )
        self.party_meta_label = UILabel(
            relative_rect=pygame.Rect(720, 96, 620, 24),
            text="",
            manager=self.manager,
            object_id="#game_meta_small_label",
        )

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

        self.player_name_labels: dict[str, UILabel] = {}
        self.player_role_labels: dict[str, UILabel] = {}
        self.player_loss_labels: dict[str, UILabel] = {}
        for seat in ("left", "top", "right", "bottom"):
            self.player_name_labels[seat] = UILabel(
                relative_rect=pygame.Rect(0, 0, 160, 24),
                text="",
                manager=self.manager,
                object_id="#player_name_label",
            )
            self.player_role_labels[seat] = UILabel(
                relative_rect=pygame.Rect(0, 0, 180, 22),
                text="",
                manager=self.manager,
                object_id="#player_role_label",
            )
            self.player_loss_labels[seat] = UILabel(
                relative_rect=pygame.Rect(0, 0, 140, 22),
                text="",
                manager=self.manager,
                object_id="#player_loss_label",
            )

        self.modals = None
        self._game_elements = [
            self.title_label,
            self.subtitle_label,
            self.attacker_label,
            self.meta_label,
            self.party_meta_label,
            self.actions_panel,
            *self.player_name_labels.values(),
            *self.player_role_labels.values(),
            *self.player_loss_labels.values(),
        ]
        self.hide_game_ui()

    @staticmethod
    def layout_schema() -> dict[str, dict[str, int | str]]:
        return {
            "title_label": {"module": "durak_app.gui_layer", "type": "label", "label": "Заголовок игры"},
            "subtitle_label": {"module": "durak_app.gui_layer", "type": "label", "label": "Подзаголовок игры"},
            "attacker_label": {"module": "durak_app.gui_layer", "type": "label", "label": "Статус атаки и защиты"},
            "meta_label": {"module": "durak_app.gui_layer", "type": "label", "label": "Служебная статистика хода"},
            "party_meta_label": {"module": "durak_app.gui_layer", "type": "label", "label": "Статус серии игр"},
            "actions_panel": {"module": "durak_app.gui_layer", "type": "panel", "label": "Панель Actions"},
            "pass_button": {"module": "durak_app.gui_layer", "type": "button", "label": "Кнопка Pass"},
            "take_button": {"module": "durak_app.gui_layer", "type": "button", "label": "Кнопка Take"},
            "restart_button": {"module": "durak_app.gui_layer", "type": "button", "label": "Кнопка Restart"},
            "surrender_button": {"module": "durak_app.gui_layer", "type": "button", "label": "Кнопка Surrender"},
            "left_name_label": {"module": "durak_app.gui_layer", "type": "label", "label": "Имя левого игрока"},
            "left_role_label": {"module": "durak_app.gui_layer", "type": "label", "label": "Роль левого игрока"},
            "left_loss_label": {"module": "durak_app.gui_layer", "type": "label", "label": "Поражения левого игрока"},
            "top_name_label": {"module": "durak_app.gui_layer", "type": "label", "label": "Имя верхнего игрока"},
            "top_role_label": {"module": "durak_app.gui_layer", "type": "label", "label": "Роль верхнего игрока"},
            "top_loss_label": {"module": "durak_app.gui_layer", "type": "label", "label": "Поражения верхнего игрока"},
            "right_name_label": {"module": "durak_app.gui_layer", "type": "label", "label": "Имя правого игрока"},
            "right_role_label": {"module": "durak_app.gui_layer", "type": "label", "label": "Роль правого игрока"},
            "right_loss_label": {"module": "durak_app.gui_layer", "type": "label", "label": "Поражения правого игрока"},
            "bottom_name_label": {"module": "durak_app.gui_layer", "type": "label", "label": "Имя игрока You"},
            "bottom_role_label": {"module": "durak_app.gui_layer", "type": "label", "label": "Роль игрока You"},
            "bottom_loss_label": {"module": "durak_app.gui_layer", "type": "label", "label": "Поражения игрока You"},
        }

    def layout_rect(self, block_id: str, rect: pygame.Rect) -> pygame.Rect:
        delta_x, delta_y = self.app.app_config.get_layout_delta("game_ui", block_id)
        width_delta, height_delta = self.app.app_config.get_layout_size_delta("game_ui", block_id)
        moved = rect.copy()
        moved.x += delta_x
        moved.y += delta_y
        moved.width = max(12, moved.width + width_delta)
        moved.height = max(12, moved.height + height_delta)
        return moved

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
        self.sync_text()
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
        if self.app.state is None:
            return

        table_blocks = self.app.table_screen.get_block_rects()
        table_blocks.update(self.app.table_screen.player_label_rects())

        for block_id, label, base_rect in [
            ("title_label", self.title_label, pygame.Rect(36, 20, 240, 46)),
            ("subtitle_label", self.subtitle_label, pygame.Rect(40, 66, 260, 28)),
            ("attacker_label", self.attacker_label, pygame.Rect(720, 28, 560, 30)),
            ("meta_label", self.meta_label, pygame.Rect(720, 64, 560, 24)),
            ("party_meta_label", self.party_meta_label, pygame.Rect(720, 96, 620, 24)),
        ]:
            rect = self.layout_rect(block_id, base_rect)
            label.set_relative_position((rect.x, rect.y))
            label.set_dimensions((rect.width, rect.height))

        for seat, name_key, role_key, loss_key in [
            ("left", "left_name_label", "left_role_label", "left_loss_label"),
            ("top", "top_name_label", "top_role_label", "top_loss_label"),
            ("right", "right_name_label", "right_role_label", "right_loss_label"),
            ("bottom", "bottom_name_label", "bottom_role_label", "bottom_loss_label"),
        ]:
            for block_id, label in [
                (name_key, self.player_name_labels[seat]),
                (role_key, self.player_role_labels[seat]),
                (loss_key, self.player_loss_labels[seat]),
            ]:
                rect = self.layout_rect(block_id, table_blocks[block_id])
                label.set_relative_position((rect.x, rect.y))
                label.set_dimensions((rect.width, rect.height))

        base_actions_rect = table_blocks["actions_panel"]
        actions_rect = self.layout_rect("actions_panel", base_actions_rect)
        self.actions_panel.set_relative_position((actions_rect.x, actions_rect.y))
        self.actions_panel.set_dimensions((actions_rect.width, actions_rect.height))

        for block_id, button, base_rect in [
            ("pass_button", self.pass_button, pygame.Rect(30, 86, 110, 34)),
            ("take_button", self.take_button, pygame.Rect(30, 142, 110, 34)),
            ("restart_button", self.restart_button, pygame.Rect(30, 198, 110, 34)),
            ("surrender_button", self.surrender_button, pygame.Rect(30, 244, 110, 34)),
        ]:
            rect = self.layout_rect(block_id, base_rect)
            button.set_relative_position((rect.x, rect.y))
            button.set_dimensions((rect.width, rect.height))

    def sync_text(self) -> None:
        if self.app.state is None:
            return

        state = self.app.state
        self._set_label_text(
            self.attacker_label,
            f"Attacker: {self.app.player_name(state.attacker_seat)} | Defender: {self.app.player_name(state.defender_seat)}",
        )
        self._set_label_text(
            self.meta_label,
            f"Turn {state.turn_number} | Deck {state.deck_size()} | Discard {state.discard_count}",
        )
        if self.app.losses_to_finish:
            party_text = (
                f"Game {self.app.current_game_number} | "
                f"Losses to finish: {self.app.losses_to_finish} | "
                f"Your losses: {self.app.durak_counts['bottom']}"
            )
        else:
            party_text = ""
        self._set_label_text(self.party_meta_label, party_text)

        for seat in ("left", "top", "right", "bottom"):
            display_name = "You" if seat == "bottom" else self.app.player_name(seat)
            self._set_label_text(self.player_name_labels[seat], display_name)
            self._set_label_text(self.player_role_labels[seat], self.app.seat_label(seat))
            self._set_label_text(self.player_loss_labels[seat], f"Losses {self.app.durak_counts[seat]}")

    def sync_visibility(self) -> None:
        if self.app.menu_visible or self.app.state is None:
            self.hide_game_ui()
        elif self.app.intro_visible or self.app.endgame_visible:
            self.hide_game_ui()
        else:
            self.show_game_ui()

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

    @staticmethod
    def _set_label_text(label: UILabel, text: str) -> None:
        if label.text != text:
            label.set_text(text)

    def hide_game_ui(self) -> None:
        for element in self._game_elements:
            element.hide()

    def show_game_ui(self) -> None:
        for element in self._game_elements:
            element.show()

    def point_over_ui(self, pos: tuple[int, int]) -> bool:
        if self.app.menu_visible or self.app.state is None:
            return False

        if self.modals is not None and self.modals.point_over_modal(pos):
            return True

        if not self.app.intro_visible and not self.app.endgame_visible:
            return self.actions_panel.get_abs_rect().collidepoint(pos)
        return False

    def get_block_rects(self) -> dict[str, pygame.Rect]:
        rects = {
            "title_label": self.title_label.get_abs_rect(),
            "subtitle_label": self.subtitle_label.get_abs_rect(),
            "attacker_label": self.attacker_label.get_abs_rect(),
            "meta_label": self.meta_label.get_abs_rect(),
            "party_meta_label": self.party_meta_label.get_abs_rect(),
            "actions_panel": self.actions_panel.get_abs_rect(),
            "pass_button": self.pass_button.get_abs_rect(),
            "take_button": self.take_button.get_abs_rect(),
            "restart_button": self.restart_button.get_abs_rect(),
            "surrender_button": self.surrender_button.get_abs_rect(),
        }
        for seat in ("left", "top", "right", "bottom"):
            rects[f"{seat}_name_label"] = self.player_name_labels[seat].get_abs_rect()
            rects[f"{seat}_role_label"] = self.player_role_labels[seat].get_abs_rect()
            rects[f"{seat}_loss_label"] = self.player_loss_labels[seat].get_abs_rect()
        return rects

    def deck_overlay_rect(self) -> pygame.Rect:
        if self.app.state is None:
            return pygame.Rect(0, 0, 0, 0)
        deck_x, deck_y = self.app.table_screen.get_deck_position()
        return pygame.Rect(deck_x, deck_y, CARD_WIDTH, CARD_HEIGHT)
