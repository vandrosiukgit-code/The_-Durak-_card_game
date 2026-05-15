import pygame
from pygame_gui.elements import UIButton, UILabel, UIPanel

from .config import HEIGHT, PLAYER_NAMES, WIDTH


class ModalRenderer:
    def __init__(self, app, manager) -> None:
        self.app = app
        self.manager = manager

        self.intro_modal_rect = pygame.Rect(WIDTH // 2 - 290, HEIGHT // 2 - 190, 580, 380)
        self.endgame_modal_rect = pygame.Rect(WIDTH // 2 - 330, HEIGHT // 2 - 250, 660, 500)

        self._build_intro_modal()
        self._build_endgame_modal()
        self.hide_all()

    def _build_intro_modal(self) -> None:
        self.intro_overlay = UIPanel(
            relative_rect=pygame.Rect(0, 0, WIDTH, HEIGHT),
            manager=self.manager,
            starting_height=4,
            object_id="#modal_overlay",
        )
        self.intro_panel = UIPanel(
            relative_rect=self.intro_modal_rect.copy(),
            manager=self.manager,
            container=self.intro_overlay,
            starting_height=5,
            object_id="#modal_panel",
        )
        self.intro_title = UILabel(
            relative_rect=pygame.Rect(34, 24, 500, 40),
            text="Welcome to Durak",
            manager=self.manager,
            container=self.intro_panel,
            object_id="#modal_title",
        )
        self.intro_trump = UILabel(
            relative_rect=pygame.Rect(36, 82, 500, 24),
            text="",
            manager=self.manager,
            container=self.intro_panel,
            object_id="#modal_text",
        )
        self.intro_turn_lines = [
            UILabel(
                relative_rect=pygame.Rect(36, 118 + index * 28, 508, 24),
                text="",
                manager=self.manager,
                container=self.intro_panel,
                object_id="#modal_text",
            )
            for index in range(2)
        ]
        self.intro_tips_title = UILabel(
            relative_rect=pygame.Rect(36, 184, 200, 28),
            text="Quick tips",
            manager=self.manager,
            container=self.intro_panel,
            object_id="#modal_section",
        )
        self.intro_tip_lines = [
            UILabel(
                relative_rect=pygame.Rect(42, 220 + index * 24, 500, 22),
                text="",
                manager=self.manager,
                container=self.intro_panel,
                object_id="#modal_text",
            )
            for index in range(4)
        ]
        self.intro_ok_button = UIButton(
            relative_rect=pygame.Rect((self.intro_modal_rect.width - 140) // 2, self.intro_modal_rect.height - 70, 140, 42),
            text="Continue",
            manager=self.manager,
            container=self.intro_panel,
            object_id="#primary_button",
        )

    def _build_endgame_modal(self) -> None:
        self.endgame_overlay = UIPanel(
            relative_rect=pygame.Rect(0, 0, WIDTH, HEIGHT),
            manager=self.manager,
            starting_height=4,
            object_id="#modal_overlay",
        )
        self.endgame_panel = UIPanel(
            relative_rect=self.endgame_modal_rect.copy(),
            manager=self.manager,
            container=self.endgame_overlay,
            starting_height=5,
            object_id="#modal_panel",
        )
        self.endgame_title = UILabel(
            relative_rect=pygame.Rect(34, 24, 560, 42),
            text="Game over",
            manager=self.manager,
            container=self.endgame_panel,
            object_id="#modal_title",
        )
        self.endgame_loser_title = UILabel(
            relative_rect=pygame.Rect(36, 98, 240, 24),
            text="Loser of this game",
            manager=self.manager,
            container=self.endgame_panel,
            object_id="#modal_section",
        )
        self.endgame_loser_name = UILabel(
            relative_rect=pygame.Rect(36, 132, 320, 30),
            text="",
            manager=self.manager,
            container=self.endgame_panel,
            object_id="#modal_value",
        )
        self.endgame_meta = UILabel(
            relative_rect=pygame.Rect(36, 174, 560, 22),
            text="",
            manager=self.manager,
            container=self.endgame_panel,
            object_id="#modal_hint",
        )
        self.endgame_score_title = UILabel(
            relative_rect=pygame.Rect(36, 218, 240, 24),
            text="Loss statistics",
            manager=self.manager,
            container=self.endgame_panel,
            object_id="#modal_section",
        )
        self.endgame_score_panel = UIPanel(
            relative_rect=pygame.Rect(36, 258, self.endgame_modal_rect.width - 72, 134),
            manager=self.manager,
            container=self.endgame_panel,
            object_id="#score_panel",
        )
        left_positions = [("You", 22, 18), ("Bot Left", 22, 64)]
        right_positions = [("Bot Top", 330, 18), ("Bot Right", 330, 64)]
        self.endgame_score_labels: dict[str, tuple[UILabel, UILabel]] = {}
        for seat_key, label_text, x, y in (
            ("bottom", "You", 22, 18),
            ("left", "Bot Left", 22, 64),
            ("top", "Bot Top", 330, 18),
            ("right", "Bot Right", 330, 64),
        ):
            label = UILabel(
                relative_rect=pygame.Rect(x, y, 120, 24),
                text=label_text,
                manager=self.manager,
                container=self.endgame_score_panel,
                object_id="#modal_text",
            )
            value = UILabel(
                relative_rect=pygame.Rect(x + 150, y, 48, 24),
                text="0",
                manager=self.manager,
                container=self.endgame_score_panel,
                object_id="#modal_value",
            )
            self.endgame_score_labels[seat_key] = (label, value)

        self.endgame_match_title = UILabel(
            relative_rect=pygame.Rect(36, 412, 240, 24),
            text="Match survivors",
            manager=self.manager,
            container=self.endgame_panel,
            object_id="#modal_section",
        )
        self.endgame_match_value = UILabel(
            relative_rect=pygame.Rect(36, 444, 560, 24),
            text="",
            manager=self.manager,
            container=self.endgame_panel,
            object_id="#modal_text",
        )
        self.endgame_hint = UILabel(
            relative_rect=pygame.Rect(36, self.endgame_modal_rect.height - 102, 560, 22),
            text="",
            manager=self.manager,
            container=self.endgame_panel,
            object_id="#modal_hint",
        )
        self.endgame_continue_button = UIButton(
            relative_rect=pygame.Rect(self.endgame_modal_rect.width // 2 - 220, self.endgame_modal_rect.height - 72, 180, 42),
            text="Continue",
            manager=self.manager,
            container=self.endgame_panel,
            object_id="#primary_button",
        )
        self.endgame_end_button = UIButton(
            relative_rect=pygame.Rect(self.endgame_modal_rect.width // 2 + 40, self.endgame_modal_rect.height - 72, 180, 42),
            text="End game",
            manager=self.manager,
            container=self.endgame_panel,
            object_id="#danger_button",
        )

    def hide_all(self) -> None:
        self.intro_overlay.hide()
        self.endgame_overlay.hide()

    def sync_layout(self) -> None:
        self.intro_overlay.set_relative_position((0, 0))
        self.intro_overlay.set_dimensions((WIDTH, HEIGHT))
        self.intro_modal_rect = pygame.Rect(WIDTH // 2 - 290, HEIGHT // 2 - 190, 580, 380)
        self.intro_panel.set_relative_position((self.intro_modal_rect.x, self.intro_modal_rect.y))
        self.intro_panel.set_dimensions((self.intro_modal_rect.width, self.intro_modal_rect.height))
        self.intro_ok_button.set_relative_position(((self.intro_modal_rect.width - 140) // 2, self.intro_modal_rect.height - 70))

        self.endgame_overlay.set_relative_position((0, 0))
        self.endgame_overlay.set_dimensions((WIDTH, HEIGHT))
        self.endgame_modal_rect = pygame.Rect(WIDTH // 2 - 330, HEIGHT // 2 - 250, 660, 500)
        self.endgame_panel.set_relative_position((self.endgame_modal_rect.x, self.endgame_modal_rect.y))
        self.endgame_panel.set_dimensions((self.endgame_modal_rect.width, self.endgame_modal_rect.height))
        self.endgame_score_panel.set_dimensions((self.endgame_modal_rect.width - 72, 134))
        self.endgame_hint.set_relative_position((36, self.endgame_modal_rect.height - 102))
        self.endgame_continue_button.set_relative_position((self.endgame_modal_rect.width // 2 - 220, self.endgame_modal_rect.height - 72))
        self.endgame_end_button.set_relative_position((self.endgame_modal_rect.width // 2 + 40, self.endgame_modal_rect.height - 72))

    def sync_visibility(self) -> None:
        if self.app.intro_visible and self.app.state is not None:
            self.intro_overlay.show()
        else:
            self.intro_overlay.hide()

        if self.app.endgame_visible and self.app.state is not None:
            self.endgame_overlay.show()
        else:
            self.endgame_overlay.hide()

    def sync_content(self) -> None:
        if self.app.state is None:
            return
        self._sync_intro_content()
        self._sync_endgame_content()

    def _sync_intro_content(self) -> None:
        state = self.app.state
        assert state is not None
        self.intro_trump.set_text(f"Trump suit: {state.trump_suit.label} | Game {self.app.current_game_number}")
        turn_lines = self.app.wrap_text(self.app.current_turn_hint(), self.app.small_font, self.intro_modal_rect.width - 72)
        for index, label in enumerate(self.intro_turn_lines):
            label.set_text(turn_lines[index] if index < len(turn_lines[:2]) else "")

        tips = [
            "Click a card once to select it.",
            "Click the selected card again to play it.",
            "Use Take when you cannot defend.",
            "Use Pass when your throw-in is finished.",
        ]
        for label, tip in zip(self.intro_tip_lines, tips):
            label.set_text(f"- {tip}")

    def _sync_endgame_content(self) -> None:
        state = self.app.state
        assert state is not None
        self.endgame_title.set_text(self.app.endgame_title())
        loser_name = PLAYER_NAMES[state.loser_seat] if state.loser_seat else "Nobody"
        self.endgame_loser_name.set_text(loser_name)
        self.endgame_meta.set_text(
            f"Game {self.app.current_game_number} | Turns {state.turn_number} | Discard {state.discard_count}"
        )

        for seat_key, (_, value_label) in self.endgame_score_labels.items():
            value_label.set_text(str(self.app.durak_counts[seat_key]))

        if self.app.match_complete:
            self.endgame_match_title.show()
            self.endgame_match_value.show()
            self.endgame_match_value.set_text(self.app.match_survivors_text())
            hint_text = "Continue returns to the menu. End game closes the window."
        else:
            self.endgame_match_title.hide()
            self.endgame_match_value.hide()
            hint_text = "Continue starts the next game in this match."

        self.endgame_hint.set_text(hint_text)
        self.endgame_continue_button.set_text("Continue")

    def event_action(self, ui_element) -> str | None:
        if ui_element == self.intro_ok_button:
            return "intro_continue"
        if ui_element == self.endgame_continue_button:
            return "endgame_continue"
        if ui_element == self.endgame_end_button:
            return "endgame_end"
        return None

    def point_over_modal(self, pos: tuple[int, int]) -> bool:
        if self.intro_overlay.visible:
            return self.intro_modal_rect.collidepoint(pos)
        if self.endgame_overlay.visible:
            return self.endgame_modal_rect.collidepoint(pos)
        return False
