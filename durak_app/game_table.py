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
    PORTRAIT_SIZE,
    RESERVED_BG,
    SELECTION_COLOR,
    SIDE_ZONE_TOP,
    SLOT_COLOR,
    TABLE_RECT,
    WIDTH,
)


class GameTableScreen:
    def __init__(self, app):
        self.app = app

    @staticmethod
    def layout_schema() -> dict[str, dict[str, str]]:
        return {
            "table_area": {"module": "durak_app.game_table", "type": "panel", "label": "Игровой стол"},
            "table_cards_area": {"module": "durak_app.game_table", "type": "card_zone", "label": "Зона карт на столе"},
            "player_left_panel": {"module": "durak_app.game_table", "type": "player_panel", "label": "Левая панель игрока"},
            "player_top_panel": {"module": "durak_app.game_table", "type": "player_panel", "label": "Верхняя панель игрока"},
            "player_right_panel": {"module": "durak_app.game_table", "type": "player_panel", "label": "Правая панель игрока"},
            "player_bottom_panel": {"module": "durak_app.game_table", "type": "player_panel", "label": "Нижняя панель игрока"},
            "left_hand_area": {"module": "durak_app.game_table", "type": "hand_zone", "label": "Левая рука"},
            "top_hand_area": {"module": "durak_app.game_table", "type": "hand_zone", "label": "Верхняя рука"},
            "right_hand_area": {"module": "durak_app.game_table", "type": "hand_zone", "label": "Правая рука"},
            "bottom_hand_area": {"module": "durak_app.game_table", "type": "hand_zone", "label": "Нижняя рука"},
            "deck_panel": {"module": "durak_app.game_table", "type": "card_zone", "label": "Колода"},
            "trump_panel": {"module": "durak_app.game_table", "type": "card_zone", "label": "Козырь"},
            "actions_panel": {"module": "durak_app.game_table", "type": "panel", "label": "Панель действий"},
        }

    def layout_box(self, block_id: str, rect: pygame.Rect) -> pygame.Rect:
        delta_x, delta_y = self.app.app_config.get_layout_delta("game_table", block_id)
        width_delta, height_delta = self.app.app_config.get_layout_size_delta("game_table", block_id)
        moved = rect.copy()
        moved.x += delta_x
        moved.y += delta_y
        moved.width = max(12, moved.width + width_delta)
        moved.height = max(12, moved.height + height_delta)
        return moved

    def layout_rect(self, block_id: str, rect: pygame.Rect) -> pygame.Rect:
        return self.layout_box(block_id, rect)

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
        trump_rect = self.layout_rect("trump_panel", pygame.Rect(deck_x, deck_y + 40, CARD_HEIGHT, CARD_WIDTH))

        panel_width = 170
        panel_height = 300
        gap_width = deck_x - table_rect.right - panel_width
        panel_x = table_rect.right + max(0, gap_width // 2)
        actions_rect = self.layout_rect("actions_panel", pygame.Rect(panel_x, deck_y, panel_width, panel_height))
        table_cards_rect = self.layout_rect("table_cards_area", pygame.Rect(WIDTH // 2 - 500, 190, 560, 310))

        left_hand_rect = self.layout_rect(
            "left_hand_area",
            pygame.Rect(left_rect.x + 12, left_rect.y + 224, BOT_CARD_WIDTH + 52, 9 * 25 + BOT_CARD_HEIGHT),
        )
        top_hand_rect = self.layout_rect("top_hand_area", pygame.Rect(top_rect.x + 250, top_rect.y + 20, 260, 118))
        right_hand_rect = self.layout_rect(
            "right_hand_area",
            pygame.Rect(right_rect.x + 12, right_rect.y + 224, BOT_CARD_WIDTH + 52, 9 * 25 + BOT_CARD_HEIGHT),
        )
        bottom_hand_rect = self.layout_rect(
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

    def player_label_rects(self) -> dict[str, pygame.Rect]:
        blocks = self.get_block_rects()
        left_rect = blocks["player_left_panel"]
        top_rect = blocks["player_top_panel"]
        right_rect = blocks["player_right_panel"]
        bottom_rect = blocks["player_bottom_panel"]
        return {
            "left_name_label": pygame.Rect(left_rect.x + 24, left_rect.y + 128, 120, 24),
            "left_role_label": pygame.Rect(left_rect.x + 24, left_rect.y + 156, 130, 22),
            "left_loss_label": pygame.Rect(left_rect.x + 24, left_rect.y + 182, 120, 20),
            "top_name_label": pygame.Rect(top_rect.x + 136, top_rect.y + 24, 140, 24),
            "top_role_label": pygame.Rect(top_rect.x + 136, top_rect.y + 52, 180, 22),
            "top_loss_label": pygame.Rect(top_rect.x + 136, top_rect.y + 80, 120, 20),
            "right_name_label": pygame.Rect(right_rect.x + 24, right_rect.y + 128, 120, 24),
            "right_role_label": pygame.Rect(right_rect.x + 24, right_rect.y + 156, 130, 22),
            "right_loss_label": pygame.Rect(right_rect.x + 24, right_rect.y + 182, 120, 20),
            "bottom_name_label": pygame.Rect(bottom_rect.x + 18, bottom_rect.y + 146, 120, 24),
            "bottom_role_label": pygame.Rect(bottom_rect.x + 18, bottom_rect.y + 174, 160, 22),
            "bottom_loss_label": pygame.Rect(bottom_rect.x + 18, bottom_rect.y + 200, 120, 20),
        }

    def draw(self, mouse_pos: tuple[int, int]) -> None:
        screen = self.app.screen
        screen.fill((22, 96, 58))
        block_rects = self.get_block_rects()
        table_rect = block_rects["table_area"]
        pygame.draw.rect(screen, FELT_DARK, table_rect, border_radius=40)
        self.draw_player_zones(block_rects)
        self.draw_center_cards(block_rects)

    def draw_player_zones(self, block_rects: dict[str, pygame.Rect]) -> None:
        state = self.app.state
        assert state is not None
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
                self.draw_bottom_player_zone(
                    rect,
                    border_color,
                    border_width,
                    fill_color,
                    block_rects["bottom_hand_area"],
                )
            elif seat == "top":
                self.draw_top_player_zone(
                    seat,
                    rect,
                    border_color,
                    border_width,
                    fill_color,
                    block_rects["top_hand_area"],
                )
            else:
                hand_key = "left_hand_area" if seat == "left" else "right_hand_area"
                self.draw_side_player_zone(seat, rect, border_color, border_width, fill_color, block_rects[hand_key])

    def draw_side_player_zone(
        self,
        seat: str,
        rect: pygame.Rect,
        border_color: tuple,
        border_width: int,
        fill_color: tuple,
        hand_rect: pygame.Rect,
    ) -> None:
        pygame.draw.rect(self.app.screen, fill_color, rect, border_radius=18)
        pygame.draw.rect(self.app.screen, border_color, rect, width=border_width, border_radius=18)
        self.draw_portrait(pygame.Rect(rect.x + 35, rect.y + 18, PORTRAIT_SIZE, PORTRAIT_SIZE), seat)

        visible = self.app.state.hand_size(seat)
        base_x, base_y = hand_rect.x, hand_rect.y
        col_spacing, row_spacing = 52, 25
        for index in range(visible):
            col, row = index // 9, index % 9
            card_rect = pygame.Rect(base_x + col * col_spacing, base_y + row * row_spacing, BOT_CARD_WIDTH, BOT_CARD_HEIGHT)
            self.draw_card_back(card_rect)

    def draw_top_player_zone(
        self,
        seat: str,
        rect: pygame.Rect,
        border_color: tuple,
        border_width: int,
        fill_color: tuple,
        hand_rect: pygame.Rect,
    ) -> None:
        pygame.draw.rect(self.app.screen, fill_color, rect, border_radius=18)
        pygame.draw.rect(self.app.screen, border_color, rect, width=border_width, border_radius=18)
        self.draw_portrait(pygame.Rect(rect.x + 18, rect.y + 20, PORTRAIT_SIZE, PORTRAIT_SIZE), seat)

        top_card_width = 78
        top_card_height = 118
        for index in range(self.app.state.hand_size(seat)):
            self.draw_card_back(pygame.Rect(hand_rect.x + index * 28, hand_rect.y, top_card_width, top_card_height))

    def draw_bottom_player_zone(
        self,
        rect: pygame.Rect,
        border_color: tuple,
        border_width: int,
        fill_color: tuple,
        hand_rect: pygame.Rect,
    ) -> None:
        is_error = self.app.is_timer_active("bottom_zone_error")
        current_bg = (130, 40, 40) if is_error else fill_color
        edge_color = (255, 0, 0) if is_error else border_color

        pygame.draw.rect(self.app.screen, current_bg, rect, border_radius=18)
        pygame.draw.rect(self.app.screen, edge_color, rect, width=border_width, border_radius=18)
        self.draw_portrait(pygame.Rect(rect.x + 20, rect.y + 20, PORTRAIT_SIZE, PORTRAIT_SIZE), "bottom")

        hand = self.app.sorted_bottom_hand()
        mouse_pos = pygame.mouse.get_pos()
        start_x = hand_rect.x
        base_y = hand_rect.y
        available_width = hand_rect.width
        spacing = CARD_WIDTH
        if len(hand) > 1:
            spacing = min(CARD_WIDTH + 12, max(40, (available_width - CARD_WIDTH) // (len(hand) - 1)))

        hovered_index = None
        for index in range(len(hand) - 1, -1, -1):
            temp_rect = pygame.Rect(start_x + index * spacing, base_y + 20, CARD_WIDTH, CARD_HEIGHT)
            if self.app.selected_card_index == index:
                temp_rect.y -= 20
            if temp_rect.collidepoint(mouse_pos):
                hovered_index = index
                break

        self.app.player_card_rects = []
        for index, card in enumerate(hand):
            card_rect = pygame.Rect(start_x + index * spacing, base_y + 20, CARD_WIDTH, CARD_HEIGHT)
            if index == hovered_index:
                card_rect.y -= 45
            elif self.app.selected_card_index == index:
                card_rect.y -= 20
            self.app.player_card_rects.append(card_rect)
            if self.app.selected_card_index == index:
                pygame.draw.rect(self.app.screen, SELECTION_COLOR, card_rect.inflate(6, 6), width=3, border_radius=18)
            self.draw_card_front(card_rect, card)

    def draw_center_cards(self, block_rects: dict[str, pygame.Rect]) -> None:
        state = self.app.state
        assert state is not None
        table_cards_rect = block_rects["table_cards_area"]
        for index, pair in enumerate(state.table_attacks):
            col, row = index % 3, index // 3
            x = table_cards_rect.x + 20 + col * 200
            y = table_cards_rect.y + row * 100
            if (index, False) not in self.app.hidden_table_cards:
                self.draw_card_front(pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT), pair.attack_card)
            if pair.defense_card is not None and (index, True) not in self.app.hidden_table_cards:
                self.draw_card_front(pygame.Rect(x + 35, y + 25, CARD_WIDTH, CARD_HEIGHT), pair.defense_card)

        deck_rect = block_rects["deck_panel"]
        trump_rect = block_rects["trump_panel"]
        deck_x, deck_y = deck_rect.x, deck_rect.y
        trump_img = self.app.get_card_front(state.trump_card, (CARD_WIDTH, CARD_HEIGHT))
        trump_surface = pygame.transform.rotate(trump_img, 90)
        trump_surface_rect = trump_surface.get_rect(topleft=trump_rect.topleft)
        trump_border_rect = trump_rect.inflate(4, 4)
        pygame.draw.rect(self.app.screen, (255, 255, 255), trump_border_rect, width=2, border_radius=12)

        if state.deck_size() > 0:
            border_rect = deck_rect.inflate(8, 8)
            pygame.draw.rect(self.app.screen, (255, 255, 255), border_rect, width=2, border_radius=12)
            self.app.screen.blit(trump_surface, trump_surface_rect)
            self.draw_card_back(deck_rect)
        else:
            self.app.screen.blit(trump_surface, trump_surface_rect)
            mask = pygame.Surface(trump_surface_rect.size, pygame.SRCALPHA)
            mask.fill((40, 40, 40, 160))
            self.app.screen.blit(mask, trump_surface_rect)

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
