import os

import pygame

from card_engine import DurakGameState
from card_engine.cards import Card

from .config import (
    ANIMATION_SPEED_FACTORS,
    AppConfig,
    CARD_BACK_OPTIONS,
    CARD_FACE_OPTIONS,
    CARD_HEIGHT,
    CARD_WIDTH,
    FPS,
    HEIGHT,
    OPENING_MODE_LABELS,
    PANEL_COLOR,
    PLAYER_HAND_SIZE,
    PLAYER_NAMES,
    PORTRAIT_SET_OPTIONS,
    RESERVED_BG,
    SLOT_COLOR,
    TABLE_COLOR,
    TABLE_RECT,
    TEXT_COLOR,
    WIDTH,
)
from .game_table import GameTableScreen
from .menu import MainMenuScreen
from .modals import ModalRenderer
from .ui import Button, CardAnimation


class DurakApp:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Durak")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.app_config = AppConfig()

        visual_config = self.app_config.data["visual"]
        defaults_config = self.app_config.data["defaults"]
        self.selected_card_back = visual_config["card_back"]
        self.custom_back_file: str | None = visual_config.get("custom_back_file")
        self.selected_card_faces = visual_config["card_faces"]
        self.selected_portrait_set = visual_config["portrait_set"]
        self.selected_portrait_files = dict(visual_config["portrait_files"])
        self.card_front_cache: dict[str, pygame.Surface] = {}
        self.card_back_image: pygame.Surface | None = None
        self.current_fronts_dir = CARD_FACE_OPTIONS[0]["path"]
        self.portraits: dict[str, pygame.Surface] = {}

        self.title_font = pygame.font.SysFont("arial", 40, bold=True)
        self.text_font = pygame.font.SysFont("arial", 28)
        self.small_font = pygame.font.SysFont("arial", 22)
        self.tiny_font = pygame.font.SysFont("arial", 18)

        self.pass_button = Button(pygame.Rect(0, 0, 96, 34), "Pass", self.small_font)
        self.take_button = Button(pygame.Rect(0, 0, 96, 34), "Take", self.small_font)
        self.restart_button = Button(pygame.Rect(0, 0, 110, 34), "Restart", self.small_font)
        self.surrender_button = Button(pygame.Rect(0, 0, 110, 34), "Surrender", self.small_font)
        self.intro_ok_button = Button(pygame.Rect(0, 0, 120, 42), "OK", self.small_font)
        self.endgame_continue_button = Button(pygame.Rect(0, 0, 180, 42), "Continue", self.small_font)
        self.endgame_end_button = Button(pygame.Rect(0, 0, 180, 42), "End game", self.small_font)
        self.menu_start_button = Button(pygame.Rect(0, 0, 190, 44), "Start party", self.small_font)
        self.menu_exit_button = Button(pygame.Rect(0, 0, 190, 44), "Exit", self.small_font)
        self.games_minus_button = Button(pygame.Rect(0, 0, 44, 44), "-", self.small_font)
        self.games_plus_button = Button(pygame.Rect(0, 0, 44, 44), "+", self.small_font)
        self.mode_prev_button = Button(pygame.Rect(0, 0, 44, 44), "<", self.small_font)
        self.mode_next_button = Button(pygame.Rect(0, 0, 44, 44), ">", self.small_font)
        self.speed_prev_button = Button(pygame.Rect(0, 0, 44, 44), "<", self.small_font)
        self.speed_next_button = Button(pygame.Rect(0, 0, 44, 44), ">", self.small_font)
        self.back_prev_button = Button(pygame.Rect(0, 0, 44, 44), "<", self.small_font)
        self.back_next_button = Button(pygame.Rect(0, 0, 44, 44), ">", self.small_font)
        self.faces_prev_button = Button(pygame.Rect(0, 0, 44, 44), "<", self.small_font)
        self.faces_next_button = Button(pygame.Rect(0, 0, 44, 44), ">", self.small_font)

        self.animations: list[CardAnimation] = []
        self.selected_card_index: int | None = None
        self.player_card_rects: list[pygame.Rect] = []
        self.message = ""
        self.status_log: list[str] = []
        self.last_message_text = ""
        self.active_timers: dict[str, int] = {}
        self.last_counts = {"left": 0, "top": 0, "right": 0, "bottom": 0}
        self.animation_queue_delay = 0
        self.intro_visible = True
        self.endgame_visible = False
        self.bot_autoplay_pending = False
        self.hidden_table_cards: set[tuple[int, bool]] = set()
        self.menu_visible = True
        self.state: DurakGameState | None = None
        self.selected_losses_to_finish = defaults_config["loss_limit"]
        self.selected_opening_mode = defaults_config["opening_mode"]
        self.selected_animation_speed = defaults_config["animation_speed"]
        self.losses_to_finish = 0
        self.current_game_number = 0
        self.series_results: list[dict[str, str | int]] = []
        self.durak_counts = {seat: 0 for seat in PLAYER_NAMES}
        self.match_complete = False
        self.game_result_recorded = False

        self.table_screen = GameTableScreen(self)
        self.menu_screen = MainMenuScreen(self)
        self.modal_renderer = ModalRenderer(self)
        self.app_config.sync_layout_schema(
            {
                "game_table": self.table_screen.layout_schema(),
                "main_menu": self.menu_screen.layout_schema(),
            }
        )
        self.load_visual_assets()

    def option_by_id(self, options: list[dict[str, str]], option_id: str) -> dict[str, str]:
        for option in options:
            if option["id"] == option_id:
                return option
        return options[0]

    def card_back_available(self, option_id: str) -> bool:
        return os.path.isfile(self.option_by_id(CARD_BACK_OPTIONS, option_id)["path"])

    def card_faces_available(self, option_id: str) -> bool:
        path = self.option_by_id(CARD_FACE_OPTIONS, option_id)["path"]
        return os.path.isdir(path) and any(name.lower().endswith(".png") for name in os.listdir(path))

    def portrait_set_available(self, option_id: str) -> bool:
        path = self.option_by_id(PORTRAIT_SET_OPTIONS, option_id)["path"]
        return os.path.isdir(path) and len(os.listdir(path)) > 0

    def cycle_option(self, current_id: str, options: list[dict[str, str]], direction: int, available_fn) -> str:
        ids = [option["id"] for option in options]
        if current_id not in ids:
            return options[0]["id"]
        index = ids.index(current_id)
        for _ in range(len(ids)):
            index = (index + direction) % len(ids)
            candidate = ids[index]
            if available_fn(candidate):
                return candidate
        return current_id

    def load_visual_assets(self) -> None:
        backs_dir = os.path.dirname(CARD_BACK_OPTIONS[0]["path"])
        if self.custom_back_file:
            back_path = os.path.join(backs_dir, self.custom_back_file)
        else:
            back_option = self.option_by_id(CARD_BACK_OPTIONS, self.selected_card_back)
            back_path = back_option["path"]
        if not os.path.isfile(back_path):
            fallback_files = []
            if os.path.isdir(backs_dir):
                fallback_files = sorted(
                    [os.path.join(backs_dir, name) for name in os.listdir(backs_dir) if name.lower().endswith((".png", ".jpg", ".jpeg"))]
                )
            back_path = fallback_files[0] if fallback_files else CARD_BACK_OPTIONS[0]["path"]
        self.card_back_image = pygame.image.load(back_path).convert_alpha()

        face_option = self.option_by_id(CARD_FACE_OPTIONS, self.selected_card_faces)
        self.current_fronts_dir = face_option["path"] if self.card_faces_available(self.selected_card_faces) else CARD_FACE_OPTIONS[0]["path"]

        portrait_dir = self.option_by_id(PORTRAIT_SET_OPTIONS, self.selected_portrait_set)["path"]
        if not self.portrait_set_available(self.selected_portrait_set):
            portrait_dir = PORTRAIT_SET_OPTIONS[0]["path"]
        portrait_paths = {
            seat: os.path.join(portrait_dir, filename)
            for seat, filename in self.selected_portrait_files.items()
        }
        self.portraits = {seat: pygame.image.load(path).convert_alpha() for seat, path in portrait_paths.items()}
        self.card_front_cache.clear()

    def save_persistent_config(self) -> None:
        self.app_config.data["visual"]["card_back"] = self.selected_card_back
        self.app_config.data["visual"]["card_faces"] = self.selected_card_faces
        self.app_config.data["visual"]["portrait_set"] = self.selected_portrait_set
        self.app_config.data["visual"]["portrait_files"] = dict(self.selected_portrait_files)
        self.app_config.data["visual"]["custom_back_file"] = self.custom_back_file
        self.app_config.data["defaults"]["loss_limit"] = self.selected_losses_to_finish
        self.app_config.data["defaults"]["opening_mode"] = self.selected_opening_mode
        self.app_config.data["defaults"]["animation_speed"] = self.selected_animation_speed
        self.app_config.save()

    def reset_game(self) -> None:
        self.state = DurakGameState.new_game(cards_per_player=PLAYER_HAND_SIZE, opening_mode=self.selected_opening_mode)
        self.animations.clear()
        self.selected_card_index = None
        self.message = self.state.last_result
        self.status_log.clear()
        self.last_message_text = ""
        self.animation_queue_delay = 0
        self.intro_visible = True
        self.endgame_visible = False
        self.bot_autoplay_pending = self.state.current_actor != "bottom"
        self.hidden_table_cards.clear()
        self.game_result_recorded = False
        self.add_status_message(self.state.last_result)
        self.update_last_counts()

    def start_match(self) -> None:
        self.menu_visible = False
        self.losses_to_finish = self.selected_losses_to_finish
        self.current_game_number = 1
        self.series_results.clear()
        self.durak_counts = {seat: 0 for seat in PLAYER_NAMES}
        self.match_complete = False
        self.reset_game()

    def continue_match(self) -> None:
        if self.match_complete:
            self.menu_visible = True
            self.intro_visible = False
            self.endgame_visible = False
            self.state = None
            self.animations.clear()
            self.hidden_table_cards.clear()
            self.bot_autoplay_pending = False
            self.current_game_number = 0
            return
        self.current_game_number += 1
        self.reset_game()

    def update_last_counts(self) -> None:
        if self.state is None:
            return
        for seat in self.last_counts:
            self.last_counts[seat] = self.state.hand_size(seat)

    def start_timer(self, name: str, duration_ms: int) -> None:
        self.active_timers[name] = pygame.time.get_ticks() + duration_ms

    def is_timer_active(self, name: str) -> bool:
        return pygame.time.get_ticks() < self.active_timers.get(name, 0)

    def scaled_duration(self, duration_ms: int) -> int:
        return max(120, int(duration_ms * ANIMATION_SPEED_FACTORS[self.selected_animation_speed]))

    def sorted_bottom_hand(self) -> list[Card]:
        assert self.state is not None
        hand = list(self.state.hand_for("bottom").cards)
        return sorted(hand, key=lambda card: (card.suit == self.state.trump_suit, card.rank_value))

    def add_status_message(self, message: str) -> None:
        self.message = message
        if message and message != self.last_message_text:
            self.status_log.append(message)
            self.last_message_text = message
            if len(self.status_log) > 4:
                self.status_log.pop(0)

    def check_for_new_cards(self) -> bool:
        assert self.state is not None
        deck_center = (WIDTH // 2 + 400 + CARD_WIDTH // 2, 210 + CARD_HEIGHT // 2)
        targets = {"bottom": (WIDTH // 2, HEIGHT - 150), "left": (118, 450), "right": (WIDTH - 118, 450), "top": (WIDTH // 2, 120)}
        queued_any = False
        for seat, drawn_cards in self.state.recent_deck_draws.items():
            if not drawn_cards:
                continue
            is_player = seat == "bottom"
            end_size = (CARD_WIDTH, CARD_HEIGHT) if is_player else (112, 168)
            for index, card in enumerate(drawn_cards):
                front_img = self.get_card_front(card, end_size)
                self.animations.append(CardAnimation(deck_center, targets[seat], self.scaled_duration(1350 + index * 220), self.card_back_image, front_img, (CARD_WIDTH, CARD_HEIGHT), end_size, flip=is_player, delay_ms=self.animation_queue_delay))
                self.animation_queue_delay += 180
                queued_any = True
            self.state.recent_deck_draws[seat] = []
        self.update_last_counts()
        return queued_any

    def advance_bots(self) -> None:
        assert self.state is not None
        if self.state.is_game_over():
            self.finish_current_game()
            self.bot_autoplay_pending = False
            return
        if self.fast_forward_endgame_if_player_finished():
            return
        self.bot_autoplay_pending = not self.state.is_player_turn() and not self.state.is_game_over()

    def process_pending_bot_step(self) -> None:
        assert self.state is not None
        if not self.bot_autoplay_pending or self.state.is_game_over():
            if self.state.is_game_over():
                self.finish_current_game()
            self.bot_autoplay_pending = False
            return
        if self.state.current_actor == "bottom":
            self.bot_autoplay_pending = False
            return
        pre_step_table = [(pair.attack_card, pair.defense_card) for pair in self.state.table_attacks]
        self.animation_queue_delay = 0
        step_taken = self.state.auto_step()
        if not step_taken:
            self.bot_autoplay_pending = False
            return
        self.queue_take_pile_animation(pre_step_table)
        self.queue_bot_table_animation()
        self.check_for_new_cards()
        self.add_status_message(self.state.last_result)
        self.start_timer("bot_step_pause", self.scaled_duration(320))
        if self.fast_forward_endgame_if_player_finished():
            return
        if self.state.is_game_over():
            self.finish_current_game()
            self.bot_autoplay_pending = False
        else:
            self.bot_autoplay_pending = self.state.current_actor != "bottom"

    def fast_forward_endgame_if_player_finished(self) -> bool:
        assert self.state is not None
        if "bottom" not in self.state.winner_seats or self.state.is_game_over():
            return False
        self.animations.clear()
        self.hidden_table_cards.clear()
        self.bot_autoplay_pending = False
        for seat in self.state.recent_deck_draws:
            self.state.recent_deck_draws[seat] = []
        while not self.state.is_game_over() and self.state.auto_step():
            self.add_status_message(self.state.last_result)
        self.update_last_counts()
        if self.state.is_game_over():
            self.finish_current_game()
        return True

    def finish_current_game(self) -> None:
        assert self.state is not None
        if self.game_result_recorded:
            self.endgame_visible = True
            return
        self.game_result_recorded = True
        loser = self.state.loser_seat or "none"
        if loser in self.durak_counts:
            self.durak_counts[loser] += 1
        self.series_results.append({"game": self.current_game_number, "loser": loser, "turns": self.state.turn_number, "discard": self.state.discard_count})
        self.match_complete = any(count >= self.losses_to_finish for count in self.durak_counts.values())
        self.endgame_visible = True

    def extract_actor_from_message(self, message: str) -> str | None:
        for prefix, seat in {"Left": "left", "Top": "top", "Right": "right", "Bottom": "bottom"}.items():
            if message.startswith(prefix):
                return seat
        return None

    def extract_table_card_from_message(self, message: str) -> tuple[Card | None, int | None, bool]:
        assert self.state is not None
        if not self.state.table_attacks:
            return None, None, False
        if "attacks with " in message or "tosses in " in message:
            return self.state.table_attacks[-1].attack_card, len(self.state.table_attacks) - 1, False
        if "defends with " in message:
            for index in range(len(self.state.table_attacks) - 1, -1, -1):
                pair = self.state.table_attacks[index]
                if pair.defense_card is not None:
                    return pair.defense_card, index, True
        return None, None, False

    def bot_hand_anchor(self, seat: str) -> tuple[tuple[int, int], tuple[int, int]]:
        return {"left": ((88, 600), (112, 168)), "top": ((WIDTH // 2, 110), (112, 168)), "right": ((WIDTH - 88, 600), (112, 168))}[seat]

    def table_rect_for_animation(self, index: int, is_defense: bool) -> pygame.Rect:
        col, row = index % 3, index // 3
        x = WIDTH // 2 - 480 + col * 200
        y = 190 + row * 100
        if is_defense:
            x += 35
            y += 25
        return pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

    def queue_take_pile_animation(self, pre_step_table: list[tuple[Card, Card | None]]) -> None:
        assert self.state is not None
        if "takes the pile" not in self.state.last_result or not pre_step_table:
            return
        defender = self.extract_actor_from_message(self.state.last_result)
        if defender not in {"left", "top", "right"}:
            return
        end_pos, end_size = self.bot_hand_anchor(defender)
        cards_to_move: list[tuple[Card, bool, int]] = []
        for index, (attack_card, defense_card) in enumerate(pre_step_table):
            cards_to_move.append((attack_card, False, index))
            if defense_card is not None:
                cards_to_move.append((defense_card, True, index))
        for offset, (card, is_defense, index) in enumerate(cards_to_move):
            start_rect = self.table_rect_for_animation(index, is_defense)
            front_img = self.get_card_front(card, start_rect.size)
            self.animations.append(CardAnimation(start_rect.center, end_pos, self.scaled_duration(700), front_img, front_img, start_rect.size, end_size, delay_ms=self.animation_queue_delay + offset * self.scaled_duration(90)))
        self.animation_queue_delay += self.scaled_duration(700) + len(cards_to_move) * self.scaled_duration(90)

    def queue_bot_table_animation(self) -> None:
        assert self.state is not None
        actor = self.extract_actor_from_message(self.state.last_result)
        if actor not in {"left", "top", "right"}:
            return
        card, target_index, is_defense = self.extract_table_card_from_message(self.state.last_result)
        if card is None or target_index is None:
            return
        start_pos, start_size = self.bot_hand_anchor(actor)
        end_rect = self.table_rect_for_animation(target_index, is_defense)
        front_img = self.get_card_front(card, end_rect.size)
        hide_key = (target_index, is_defense)
        self.hidden_table_cards.add(hide_key)
        self.animations.append(CardAnimation(start_pos, end_rect.center, self.scaled_duration(900), self.card_back_image, front_img, start_size, end_rect.size, flip=True, delay_ms=self.animation_queue_delay, hide_table_card=hide_key))
        self.animation_queue_delay += 220

    def handle_player_card_click(self, mouse_pos: tuple[int, int]) -> None:
        assert self.state is not None
        if not self.state.is_player_turn():
            return
        for index in range(len(self.player_card_rects) - 1, -1, -1):
            if self.player_card_rects[index].collidepoint(mouse_pos):
                if self.selected_card_index == index:
                    self.try_play_selected_card()
                else:
                    self.selected_card_index = index
                return

    def try_play_selected_card(self) -> None:
        assert self.state is not None
        hand = self.sorted_bottom_hand()
        if self.selected_card_index is None or self.selected_card_index >= len(hand):
            return
        card = hand[self.selected_card_index]
        start_rect = self.player_card_rects[self.selected_card_index].copy()
        played = self.state.play_attack_card("bottom", card) if self.state.phase in {"attack", "toss", "toss_after_take"} else self.state.play_defense_card(card)
        if played:
            card_on_table, target_index, is_defense = self.extract_table_card_from_message(self.state.last_result)
            if card_on_table is not None and target_index is not None:
                self.queue_player_table_animation(card_on_table, start_rect, target_index, is_defense)
            self.selected_card_index = None
            self.check_for_new_cards()
            self.advance_bots()
        else:
            self.start_timer("bottom_zone_error", 1000)

    def queue_player_table_animation(self, card: Card, start_rect: pygame.Rect, target_index: int, is_defense: bool) -> None:
        end_rect = self.table_rect_for_animation(target_index, is_defense)
        front_img = self.get_card_front(card, end_rect.size)
        hide_key = (target_index, is_defense)
        self.hidden_table_cards.add(hide_key)
        self.animations.append(CardAnimation(start_rect.center, end_rect.center, self.scaled_duration(500), front_img, front_img, start_rect.size, end_rect.size, hide_table_card=hide_key))

    def player_surrender(self) -> None:
        assert self.state is not None
        self.animations.clear()
        self.hidden_table_cards.clear()
        self.bot_autoplay_pending = False
        self.selected_card_index = None
        self.state.phase = "game_over"
        self.state.current_actor = "bottom"
        self.state.loser_seat = "bottom"
        self.state.winner_seats = [seat for seat in PLAYER_NAMES if seat != "bottom"]
        self.state.last_result = "You surrendered. You are the durak."
        self.finish_current_game()

    def seat_label(self, seat: str) -> str:
        assert self.state is not None
        parts = [f"Hand {self.state.hand_size(seat)}"]
        if self.state.attacker_seat == seat:
            parts.append("attacks")
        if self.state.defender_seat == seat:
            parts.append("defends")
        if self.state.is_game_over() and self.state.loser_seat == seat:
            parts.append("durak")
        return " | ".join(parts)

    def get_card_front(self, card: Card, size: tuple[int, int]) -> pygame.Surface:
        key = f"{card.image_key}:{size}"
        if key not in self.card_front_cache:
            image_path = os.path.join(self.current_fronts_dir, f"{card.image_key}.png")
            try:
                image = pygame.image.load(image_path).convert_alpha()
            except FileNotFoundError:
                image = self.build_missing_card_face(card)
            self.card_front_cache[key] = pygame.transform.smoothscale(image, size)
        return self.card_front_cache[key]

    def build_missing_card_face(self, card: Card) -> pygame.Surface:
        width, height = 480, 720
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        suit_color = (150, 38, 44) if card.suit.label in {"Hearts", "Diamonds"} else (44, 58, 86)
        pygame.draw.rect(surface, (247, 243, 235), (8, 8, width - 16, height - 16), border_radius=28)
        pygame.draw.rect(surface, (48, 42, 38), (8, 8, width - 16, height - 16), width=4, border_radius=28)
        pygame.draw.rect(surface, (252, 249, 243), (72, 116, width - 144, 392), border_radius=20)
        pygame.draw.rect(surface, (176, 147, 94), (72, 116, width - 144, 392), width=2, border_radius=20)
        rank_font = pygame.font.SysFont("georgia", 44, bold=True)
        title_font = pygame.font.SysFont("georgia", 22, bold=True)
        symbol_font = pygame.font.SysFont("segoeuisymbol", 30)
        center_font = pygame.font.SysFont("segoeuisymbol", 140)
        rank = rank_font.render(card.rank_label, True, suit_color)
        suit_symbol = symbol_font.render(card.short_name[-1], True, suit_color)
        title = title_font.render(card.display_name.upper(), True, suit_color)
        center = center_font.render(card.short_name[-1], True, suit_color)
        surface.blit(rank, (30, 20))
        surface.blit(suit_symbol, (38, 74))
        surface.blit(rank, (width - 30 - rank.get_width(), height - 20 - rank.get_height()))
        surface.blit(suit_symbol, (width - 38 - suit_symbol.get_width(), height - 74 - suit_symbol.get_height()))
        surface.blit(center, center.get_rect(center=(width // 2, 300)))
        surface.blit(title, title.get_rect(center=(width // 2, 440)))
        return surface

    def wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        words = text.split()
        if not words:
            return [""]
        lines: list[str] = []
        current = words[0]
        for word in words[1:]:
            probe = f"{current} {word}"
            if font.size(probe)[0] <= max_width:
                current = probe
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return lines

    def describe_phase(self) -> str:
        return {
            "attack": "Attack",
            "defend": "Defense",
            "toss": "Throw-in",
            "toss_after_take": "Throw-in after take",
            "game_over": "Game over",
        }.get(self.state.phase, self.state.phase.title())

    def current_turn_hint(self) -> str:
        assert self.state is not None
        actor_name = PLAYER_NAMES.get(self.state.current_actor, self.state.current_actor.title())
        phase_label = self.describe_phase().lower()
        if self.state.is_game_over():
            return self.state.last_result
        return f"Now {actor_name} is in {phase_label}."

    def endgame_title(self) -> str:
        assert self.state is not None
        if self.state.loser_seat == "bottom":
            return "You are the durak"
        if "bottom" in self.state.winner_seats:
            return "You win"
        if self.state.loser_seat is None:
            return "Draw game"
        return "Game over"

    def match_survivors_text(self) -> str:
        worst_score = max(self.durak_counts.values())
        survivors = [PLAYER_NAMES[seat] for seat, count in self.durak_counts.items() if count < worst_score]
        return ", ".join(survivors) if survivors else "Nobody"

    def run(self) -> None:
        running = True
        while running:
            self.clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and not self.menu_visible:
                    self.reset_game()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.menu_visible:
                        running = self.menu_screen.handle_click(event.pos)
                    elif self.endgame_visible:
                        if self.endgame_continue_button.is_clicked(event):
                            self.continue_match()
                        elif self.endgame_end_button.is_clicked(event):
                            running = False
                    elif self.intro_visible:
                        if self.intro_ok_button.is_clicked(event):
                            self.intro_visible = False
                    elif self.restart_button.is_clicked(event):
                        self.reset_game()
                    elif self.surrender_button.is_clicked(event):
                        self.player_surrender()
                    elif self.pass_button.is_clicked(event) and self.state.available_actions_for_player()["pass"]:
                        self.state.pass_action("bottom")
                        self.selected_card_index = None
                        self.check_for_new_cards()
                        self.advance_bots()
                    elif self.take_button.is_clicked(event) and self.state.available_actions_for_player()["take"]:
                        self.state.player_take()
                        self.selected_card_index = None
                        self.check_for_new_cards()
                        self.advance_bots()
                    else:
                        self.handle_player_card_click(event.pos)

            if self.state is not None:
                self.table_screen.draw(mouse_pos)
                for animation in self.animations[:]:
                    animation.update()
                    animation.draw(self.screen)
                    if animation.done:
                        if animation.hide_table_card is not None:
                            self.hidden_table_cards.discard(animation.hide_table_card)
                        self.animations.remove(animation)
                if self.bot_autoplay_pending and not self.animations and not self.intro_visible and not self.endgame_visible and not self.menu_visible and not self.is_timer_active("bot_step_pause"):
                    self.process_pending_bot_step()
                if self.intro_visible:
                    self.modal_renderer.draw_intro(mouse_pos)
                elif self.endgame_visible:
                    self.modal_renderer.draw_endgame(mouse_pos)
            else:
                self.screen.fill(TABLE_COLOR)
                pygame.draw.rect(self.screen, PANEL_COLOR, TABLE_RECT, border_radius=40)
                header = self.title_font.render("Durak", True, TEXT_COLOR)
                self.screen.blit(header, (36, 20))

            if self.menu_visible:
                self.menu_screen.draw(mouse_pos)
            pygame.display.flip()
        pygame.quit()
