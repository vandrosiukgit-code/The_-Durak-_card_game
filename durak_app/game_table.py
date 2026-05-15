import pygame

from .config import (
    BOT_CARD_HEIGHT,
    BOT_CARD_WIDTH,
    BOTTOM_ZONE_HEIGHT,
    BOTTOM_ZONE_TOP,
    BUTTON_TEXT,
    CARD_HEIGHT,
    CARD_WIDTH,
    FELT_DARK,
    MUTED_TEXT,
    PANEL_COLOR,
    PLAYER_NAMES,
    PORTRAIT_SIZE,
    RESERVED_BG,
    SELECTION_COLOR,
    SIDE_ZONE_TOP,
    SLOT_COLOR,
    TABLE_RECT,
    TEXT_COLOR,
    WIDTH,
)


class GameTableScreen:
    def __init__(self, app):
        self.app = app

    @staticmethod
    def layout_schema() -> dict[str, dict[str, int]]:
        return {
            "table_area": {"delta_x": 0, "delta_y": 0},
            "player_left_panel": {"delta_x": 0, "delta_y": 0},
            "player_top_panel": {"delta_x": 0, "delta_y": 0},
            "player_right_panel": {"delta_x": 0, "delta_y": 0},
            "player_bottom_panel": {"delta_x": 0, "delta_y": 0},
            "deck_panel": {"delta_x": 0, "delta_y": 0},
            "actions_panel": {"delta_x": 0, "delta_y": 0},
        }

    def layout_rect(self, block_id: str, rect: pygame.Rect) -> pygame.Rect:
        delta_x, delta_y = self.app.app_config.get_layout_delta("game_table", block_id)
        moved = rect.copy()
        moved.x += delta_x
        moved.y += delta_y
        return moved

    def get_deck_position(self) -> tuple[int, int]:
        base_rect = pygame.Rect(TABLE_RECT.right - CARD_WIDTH - 80, 190, CARD_WIDTH, CARD_HEIGHT)
        deck_rect = self.layout_rect("deck_panel", base_rect)
        return deck_rect.x, deck_rect.y

    def get_block_rects(self) -> dict[str, pygame.Rect]:
        table_rect = self.layout_rect("table_area", TABLE_RECT)
        left_rect = self.layout_rect("player_left_panel", pygame.Rect(32, SIDE_ZONE_TOP, 170, 620))
        top_rect = self.layout_rect("player_top_panel", pygame.Rect(WIDTH // 2 - 420, 20, 800, 160))
        right_rect = self.layout_rect("player_right_panel", pygame.Rect(WIDTH - 202, SIDE_ZONE_TOP, 170, 620))
        bottom_rect = self.layout_rect(
            "player_bottom_panel",
            pygame.Rect(WIDTH // 2 - 546, BOTTOM_ZONE_TOP + 82, 1092, BOTTOM_ZONE_HEIGHT - 96),
        )
        deck_x, deck_y = self.get_deck_position()
        deck_rect = pygame.Rect(deck_x, deck_y, CARD_WIDTH, CARD_HEIGHT)
        panel_width = 170
        panel_height = 300
        gap_width = deck_x - table_rect.right - panel_width
        panel_x = table_rect.right + max(0, gap_width // 2)
        actions_rect = self.layout_rect("actions_panel", pygame.Rect(panel_x, deck_y, panel_width, panel_height))
        return {
            "table_area": table_rect,
            "player_left_panel": left_rect,
            "player_top_panel": top_rect,
            "player_right_panel": right_rect,
            "player_bottom_panel": bottom_rect,
            "deck_panel": deck_rect,
            "actions_panel": actions_rect,
        }

    def draw(self, mouse_pos: tuple[int, int]) -> None:
        app = self.app
        screen = app.screen
        screen.fill((22, 96, 58))
        table_rect = self.get_block_rects()["table_area"]
        pygame.draw.rect(screen, FELT_DARK, table_rect, border_radius=40)
        self.draw_header()
        self.draw_scores()
        self.draw_player_zones()
        self.draw_center_cards()
        self.draw_controls(mouse_pos)

    def draw_header(self) -> None:
        title = self.app.title_font.render("Durak", True, TEXT_COLOR)
        subtitle = self.app.small_font.render("Classic throw-in Durak", True, MUTED_TEXT)
        self.app.screen.blit(title, (36, 20))
        self.app.screen.blit(subtitle, (40, 66))

    def draw_scores(self) -> None:
        state = self.app.state
        assert state is not None
        text = f"Attacker: {PLAYER_NAMES[state.attacker_seat]} | Defender: {PLAYER_NAMES[state.defender_seat]}"
        surface = self.app.text_font.render(text, True, TEXT_COLOR)
        self.app.screen.blit(surface, (720, 28))

        meta = f"Turn {state.turn_number} | Deck {state.deck_size()} | Discard {state.discard_count}"
        meta_surface = self.app.small_font.render(meta, True, MUTED_TEXT)
        self.app.screen.blit(meta_surface, (720, 64))

        if self.app.losses_to_finish:
            party_meta = (
                f"Game {self.app.current_game_number} | "
                f"Losses to finish: {self.app.losses_to_finish} | "
                f"Your losses: {self.app.durak_counts['bottom']}"
            )
            party_surface = self.app.tiny_font.render(party_meta, True, MUTED_TEXT)
            self.app.screen.blit(party_surface, (720, 96))

    def draw_player_zones(self) -> None:
        state = self.app.state
        assert state is not None
        block_rects = self.get_block_rects()
        zones = [
            ("left", block_rects["player_left_panel"]),
            ("top", block_rects["player_top_panel"]),
            ("right", block_rects["player_right_panel"]),
            ("bottom", block_rects["player_bottom_panel"]),
        ]

        for seat, rect in zones:
            border_color = SLOT_COLOR
            border_width = 2
            fill_color = RESERVED_BG
            if state.defender_seat == seat:
                border_color = (255, 215, 0)
                border_width = 6
            elif state.attacker_seat == seat:
                border_color = (220, 50, 50)
                fill_color = (60, 25, 25)
                border_width = 6

            if seat == "bottom":
                self.draw_bottom_player_zone(rect, border_color, border_width, fill_color)
            elif seat == "top":
                self.draw_top_player_zone(seat, rect, border_color, border_width, fill_color)
            else:
                self.draw_side_player_zone(seat, rect, border_color, border_width, fill_color)

    def draw_side_player_zone(self, seat: str, rect: pygame.Rect, border_color: tuple, border_width: int, fill_color: tuple) -> None:
        pygame.draw.rect(self.app.screen, fill_color, rect, border_radius=18)
        pygame.draw.rect(self.app.screen, border_color, rect, width=border_width, border_radius=18)
        self.draw_portrait(pygame.Rect(rect.x + 35, rect.y + 18, PORTRAIT_SIZE, PORTRAIT_SIZE), seat)

        name = self.app.small_font.render(PLAYER_NAMES[seat], True, TEXT_COLOR)
        label = self.app.tiny_font.render(self.app.seat_label(seat), True, MUTED_TEXT)
        losses = self.app.tiny_font.render(f"Losses {self.app.durak_counts[seat]}", True, TEXT_COLOR)
        self.app.screen.blit(name, (rect.x + 24, rect.y + 128))
        self.app.screen.blit(label, (rect.x + 24, rect.y + 156))
        self.app.screen.blit(losses, (rect.x + 24, rect.y + 182))

        visible = self.app.state.hand_size(seat)
        base_x, col_spacing, row_spacing = rect.x + 12, 52, 25
        for index in range(visible):
            col, row = index // 9, index % 9
            card_rect = pygame.Rect(base_x + col * col_spacing, rect.y + 224 + row * row_spacing, BOT_CARD_WIDTH, BOT_CARD_HEIGHT)
            self.draw_card_back(card_rect)

    def draw_top_player_zone(self, seat: str, rect: pygame.Rect, border_color: tuple, border_width: int, fill_color: tuple) -> None:
        pygame.draw.rect(self.app.screen, fill_color, rect, border_radius=18)
        pygame.draw.rect(self.app.screen, border_color, rect, width=border_width, border_radius=18)
        self.draw_portrait(pygame.Rect(rect.x + 18, rect.y + 20, PORTRAIT_SIZE, PORTRAIT_SIZE), seat)

        name = self.app.small_font.render(PLAYER_NAMES[seat], True, TEXT_COLOR)
        label = self.app.tiny_font.render(self.app.seat_label(seat), True, MUTED_TEXT)
        losses = self.app.tiny_font.render(f"Losses {self.app.durak_counts[seat]}", True, TEXT_COLOR)
        self.app.screen.blit(name, (rect.x + 136, rect.y + 24))
        self.app.screen.blit(label, (rect.x + 136, rect.y + 54))
        self.app.screen.blit(losses, (rect.x + 136, rect.y + 80))

        top_card_width = 78
        top_card_height = 118
        for index in range(self.app.state.hand_size(seat)):
            self.draw_card_back(pygame.Rect(rect.x + 250 + index * 28, rect.y + 20, top_card_width, top_card_height))

    def draw_bottom_player_zone(self, rect: pygame.Rect, border_color: tuple, border_width: int, fill_color: tuple) -> None:
        is_error = self.app.is_timer_active("bottom_zone_error")
        current_bg = (130, 40, 40) if is_error else fill_color
        edge_color = (255, 0, 0) if is_error else border_color

        pygame.draw.rect(self.app.screen, current_bg, rect, border_radius=18)
        pygame.draw.rect(self.app.screen, edge_color, rect, width=border_width, border_radius=18)
        self.draw_portrait(pygame.Rect(rect.x + 20, rect.y + 20, PORTRAIT_SIZE, PORTRAIT_SIZE), "bottom")

        name = self.app.small_font.render("You", True, TEXT_COLOR)
        label = self.app.tiny_font.render(self.app.seat_label("bottom"), True, MUTED_TEXT)
        losses = self.app.tiny_font.render(f"Losses {self.app.durak_counts['bottom']}", True, TEXT_COLOR)
        self.app.screen.blit(name, (rect.x + 18, rect.y + 146))
        self.app.screen.blit(label, (rect.x + 18, rect.y + 176))
        self.app.screen.blit(losses, (rect.x + 18, rect.y + 200))

        hand = self.app.sorted_bottom_hand()
        mouse_pos = pygame.mouse.get_pos()
        start_x = rect.x + 190
        available_width = rect.width - 230
        spacing = CARD_WIDTH
        if len(hand) > 1:
            spacing = min(CARD_WIDTH + 12, max(40, (available_width - CARD_WIDTH) // (len(hand) - 1)))

        hovered_index = None
        for index in range(len(hand) - 1, -1, -1):
            temp_rect = pygame.Rect(start_x + index * spacing, rect.bottom - CARD_HEIGHT - 15, CARD_WIDTH, CARD_HEIGHT)
            if self.app.selected_card_index == index:
                temp_rect.y -= 20
            if temp_rect.collidepoint(mouse_pos):
                hovered_index = index
                break

        self.app.player_card_rects = []
        for index, card in enumerate(hand):
            card_rect = pygame.Rect(start_x + index * spacing, rect.bottom - CARD_HEIGHT - 15, CARD_WIDTH, CARD_HEIGHT)
            if index == hovered_index:
                card_rect.y -= 45
            elif self.app.selected_card_index == index:
                card_rect.y -= 20
            self.app.player_card_rects.append(card_rect)
            if self.app.selected_card_index == index:
                pygame.draw.rect(self.app.screen, SELECTION_COLOR, card_rect.inflate(6, 6), width=3, border_radius=18)
            self.draw_card_front(card_rect, card)

    def draw_center_cards(self) -> None:
        state = self.app.state
        assert state is not None
        for index, pair in enumerate(state.table_attacks):
            col, row = index % 3, index // 3
            x = WIDTH // 2 - 480 + col * 200
            y = 190 + row * 100
            if (index, False) not in self.app.hidden_table_cards:
                self.draw_card_front(pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT), pair.attack_card)
            if pair.defense_card is not None and (index, True) not in self.app.hidden_table_cards:
                self.draw_card_front(pygame.Rect(x + 35, y + 25, CARD_WIDTH, CARD_HEIGHT), pair.defense_card)

        deck_x, deck_y = self.get_deck_position()
        trump_img = self.app.get_card_front(state.trump_card, (CARD_WIDTH, CARD_HEIGHT))
        trump_surface = pygame.transform.rotate(trump_img, 90)
        trump_rect = trump_surface.get_rect(topleft=(deck_x, deck_y + 40))
        trump_border_rect = pygame.Rect(deck_x - 2, deck_y + 38, CARD_HEIGHT + 4, CARD_WIDTH + 4)
        pygame.draw.rect(self.app.screen, (255, 255, 255), trump_border_rect, width=2, border_radius=12)

        if state.deck_size() > 0:
            border_rect = pygame.Rect(deck_x - 4, deck_y - 4, CARD_WIDTH + 8, CARD_HEIGHT + 8)
            pygame.draw.rect(self.app.screen, (255, 255, 255), border_rect, width=2, border_radius=12)
            self.app.screen.blit(trump_surface, trump_rect)
            self.draw_card_back(pygame.Rect(deck_x, deck_y, CARD_WIDTH, CARD_HEIGHT))
        else:
            self.app.screen.blit(trump_surface, trump_rect)
            mask = pygame.Surface(trump_rect.size, pygame.SRCALPHA)
            mask.fill((40, 40, 40, 160))
            self.app.screen.blit(mask, trump_rect)
            label = self.app.tiny_font.render("EMPTY", True, (200, 200, 200))
            self.app.screen.blit(label, (deck_x + (CARD_WIDTH // 2) - (label.get_width() // 2), deck_y + 20))

    def draw_controls(self, mouse_pos: tuple[int, int]) -> None:
        return

    def draw_portrait(self, rect: pygame.Rect, seat: str) -> None:
        portrait = pygame.transform.smoothscale(self.app.portraits[seat], rect.size)
        self.app.screen.blit(portrait, rect)
        pygame.draw.rect(self.app.screen, SLOT_COLOR, rect, width=2, border_radius=18)

    def draw_card_front(self, rect: pygame.Rect, card) -> None:
        self.app.screen.blit(self.app.get_card_front(card, rect.size), rect)
        pygame.draw.rect(self.app.screen, BUTTON_TEXT, rect, width=2, border_radius=14)

    def draw_card_back(self, rect: pygame.Rect) -> None:
        image = pygame.transform.smoothscale(self.app.card_back_image, rect.size)
        self.app.screen.blit(image, rect)
        pygame.draw.rect(self.app.screen, BUTTON_TEXT, rect, width=2, border_radius=14)
