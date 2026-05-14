import pygame

from .config import (
    BUTTON_COLOR,
    MUTED_TEXT,
    PANEL_COLOR,
    PLAYER_NAMES,
    RESERVED_BG,
    SLOT_COLOR,
    TEXT_COLOR,
    WIDTH,
    HEIGHT,
)


class ModalRenderer:
    def __init__(self, app):
        self.app = app

    def draw_intro(self, mouse_pos: tuple[int, int]) -> None:
        state = self.app.state
        assert state is not None
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 18, 12, 150))
        self.app.screen.blit(overlay, (0, 0))

        modal_rect = pygame.Rect(WIDTH // 2 - 290, HEIGHT // 2 - 190, 580, 380)
        pygame.draw.rect(self.app.screen, PANEL_COLOR, modal_rect, border_radius=22)
        pygame.draw.rect(self.app.screen, SLOT_COLOR, modal_rect, width=2, border_radius=22)
        title = self.app.title_font.render("Welcome to Durak", True, TEXT_COLOR)
        self.app.screen.blit(title, (modal_rect.x + 34, modal_rect.y + 26))
        trump_text = self.app.small_font.render(
            f"Trump suit: {state.trump_suit.label} | Game {self.app.current_game_number}",
            True,
            MUTED_TEXT,
        )
        self.app.screen.blit(trump_text, (modal_rect.x + 36, modal_rect.y + 84))

        turn_lines = self.app.wrap_text(self.app.current_turn_hint(), self.app.small_font, modal_rect.width - 72)
        for index, line in enumerate(turn_lines[:2]):
            surface = self.app.small_font.render(line, True, TEXT_COLOR)
            self.app.screen.blit(surface, (modal_rect.x + 36, modal_rect.y + 120 + index * 26))

        tips = [
            "Click a card once to select it.",
            "Click the selected card again to play it.",
            "Use Take when you cannot defend.",
            "Use Pass when your throw-in is finished.",
        ]
        tips_title = self.app.small_font.render("Quick tips", True, TEXT_COLOR)
        self.app.screen.blit(tips_title, (modal_rect.x + 36, modal_rect.y + 186))
        for index, tip in enumerate(tips):
            bullet = self.app.tiny_font.render(f"- {tip}", True, MUTED_TEXT)
            self.app.screen.blit(bullet, (modal_rect.x + 42, modal_rect.y + 222 + index * 24))

        self.app.intro_ok_button.rect.center = (modal_rect.centerx, modal_rect.bottom - 42)
        self.app.intro_ok_button.draw(self.app.screen, mouse_pos, enabled=True)

    def draw_endgame(self, mouse_pos: tuple[int, int]) -> None:
        state = self.app.state
        assert state is not None
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 18, 12, 175))
        self.app.screen.blit(overlay, (0, 0))

        modal_rect = pygame.Rect(WIDTH // 2 - 330, HEIGHT // 2 - 250, 660, 500)
        pygame.draw.rect(self.app.screen, PANEL_COLOR, modal_rect, border_radius=22)
        pygame.draw.rect(self.app.screen, SLOT_COLOR, modal_rect, width=2, border_radius=22)
        title = self.app.title_font.render(self.app.endgame_title(), True, TEXT_COLOR)
        self.app.screen.blit(title, (modal_rect.x + 34, modal_rect.y + 28))

        loser_name = PLAYER_NAMES[state.loser_seat] if state.loser_seat else "Nobody"
        durak_title = self.app.small_font.render("Loser of this game", True, TEXT_COLOR)
        self.app.screen.blit(durak_title, (modal_rect.x + 36, modal_rect.y + 102))
        durak_name = self.app.text_font.render(loser_name, True, BUTTON_COLOR if loser_name == "You" else TEXT_COLOR)
        self.app.screen.blit(durak_name, (modal_rect.x + 36, modal_rect.y + 136))

        meta_line = self.app.tiny_font.render(
            f"Game {self.app.current_game_number} | Turns {state.turn_number} | Discard {state.discard_count}",
            True,
            MUTED_TEXT,
        )
        self.app.screen.blit(meta_line, (modal_rect.x + 36, modal_rect.y + 178))

        score_title = self.app.small_font.render("Loss statistics", True, TEXT_COLOR)
        self.app.screen.blit(score_title, (modal_rect.x + 36, modal_rect.y + 224))
        score_box = pygame.Rect(modal_rect.x + 36, modal_rect.y + 262, modal_rect.width - 72, 134)
        pygame.draw.rect(self.app.screen, RESERVED_BG, score_box, border_radius=16)
        pygame.draw.rect(self.app.screen, SLOT_COLOR, score_box, width=2, border_radius=16)

        left_scores = [("You", self.app.durak_counts["bottom"]), ("Bot Left", self.app.durak_counts["left"])]
        right_scores = [("Bot Top", self.app.durak_counts["top"]), ("Bot Right", self.app.durak_counts["right"])]
        for index, (label, value) in enumerate(left_scores):
            y = score_box.y + 20 + index * 46
            self.app.screen.blit(self.app.small_font.render(label, True, TEXT_COLOR), (score_box.x + 22, y))
            self.app.screen.blit(self.app.text_font.render(str(value), True, BUTTON_COLOR), (score_box.x + 170, y - 2))
        for index, (label, value) in enumerate(right_scores):
            y = score_box.y + 20 + index * 46
            self.app.screen.blit(self.app.small_font.render(label, True, TEXT_COLOR), (score_box.x + 330, y))
            self.app.screen.blit(self.app.text_font.render(str(value), True, BUTTON_COLOR), (score_box.x + 488, y - 2))

        if self.app.match_complete:
            match_title = self.app.small_font.render("Match survivors", True, TEXT_COLOR)
            self.app.screen.blit(match_title, (modal_rect.x + 36, modal_rect.y + 416))
            winner_text = self.app.small_font.render(self.app.match_survivors_text(), True, MUTED_TEXT)
            self.app.screen.blit(winner_text, (modal_rect.x + 36, modal_rect.y + 448))
            hint_text = "Continue returns to the menu. End game closes the window."
        else:
            hint_text = "Continue starts the next game in this match."

        self.app.endgame_continue_button.text = "Continue"
        hint = self.app.tiny_font.render(hint_text, True, MUTED_TEXT)
        self.app.screen.blit(hint, (modal_rect.x + 36, modal_rect.bottom - 92))
        buttons_y = modal_rect.bottom - 42
        self.app.endgame_continue_button.rect.center = (modal_rect.centerx - 110, buttons_y)
        self.app.endgame_end_button.rect.center = (modal_rect.centerx + 110, buttons_y)
        self.app.endgame_continue_button.draw(self.app.screen, mouse_pos, enabled=True)
        self.app.endgame_end_button.draw(self.app.screen, mouse_pos, enabled=True)
