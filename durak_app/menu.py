import os

import pygame

from .config import (
    ANIMATION_SPEED_LABELS,
    CARD_BACK_OPTIONS,
    CARD_FACE_OPTIONS,
    HEIGHT,
    OPENING_MODE_LABELS,
    PLAYER_NAMES,
    PORTRAIT_SET_OPTIONS,
    TEXT_COLOR,
    WIDTH,
)
from .menu_support import DynamicSquareGrid, ResourceManager

RATIO_SQUARE = 1.0
RATIO_CARD = 0.66

BG_COLOR = (15, 15, 25)
MAIN_PANEL_COLOR = (30, 35, 55)
SUB_PANEL_COLOR = (40, 50, 80)
GRID_BASE_COLOR = (25, 30, 50)
FRAME_COLOR = (80, 95, 130)
EMPTY_SLOT_COLOR = (35, 40, 60)
HIGHLIGHT_COLOR = (80, 210, 80)
HIGHLIGHT_HOVER = (100, 255, 100)
TEXT_DIM = (130, 140, 160)


class MainMenuScreen:
    def __init__(self, app):
        self.app = app
        self.res = ResourceManager(EMPTY_SLOT_COLOR, FRAME_COLOR)
        self.state = "MAIN"
        self.dropdown_open = False
        self.editing_idx = 0
        self.click_zones = []

    @staticmethod
    def layout_schema() -> dict[str, dict[str, int]]:
        return {
            "menu_root": {"delta_x": 0, "delta_y": 0},
            "deck_panel": {"delta_x": 0, "delta_y": 0},
            "game_settings_panel": {"delta_x": 0, "delta_y": 0},
            "start_button": {"delta_x": 0, "delta_y": 0},
            "exit_button": {"delta_x": 0, "delta_y": 0},
        }

    def layout_rect(self, block_id: str, rect: pygame.Rect) -> pygame.Rect:
        delta_x, delta_y = self.app.app_config.get_layout_delta("main_menu", block_id)
        moved = rect.copy()
        moved.x += delta_x
        moved.y += delta_y
        return moved

    def get_block_rects(self) -> dict[str, pygame.Rect]:
        root_w, root_h = 1024, 840
        root_x, root_y = (WIDTH - root_w) // 2, (HEIGHT - root_h) // 2
        root_rect = self.layout_rect("menu_root", pygame.Rect(root_x, root_y, root_w, root_h))
        deck_rect = self.layout_rect("deck_panel", pygame.Rect(root_rect.x + 32, root_rect.y + 80, 960, 360))
        game_rect = self.layout_rect("game_settings_panel", pygame.Rect(root_rect.x + 32, deck_rect.bottom + 20, 960, 270))
        start_rect = self.layout_rect("start_button", pygame.Rect(root_rect.x + (root_rect.width - 240) // 2, game_rect.bottom + 25, 240, 50))
        exit_rect = self.layout_rect("exit_button", pygame.Rect(start_rect.right + 20, start_rect.y, 180, 50))
        return {
            "menu_root": root_rect,
            "deck_panel": deck_rect,
            "game_settings_panel": game_rect,
            "start_button": start_rect,
            "exit_button": exit_rect,
        }

    @property
    def portraits_dir(self) -> str:
        return self.app.option_by_id(PORTRAIT_SET_OPTIONS, self.app.selected_portrait_set)["path"]

    @property
    def backs_dir(self) -> str:
        return os.path.dirname(self.app.option_by_id(CARD_BACK_OPTIONS, self.app.selected_card_back)["path"])

    @property
    def faces_base_dir(self) -> str:
        return os.path.dirname(self.app.option_by_id(CARD_FACE_OPTIONS, "default")["path"])

    def _scan_dirs(self, path):
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            return []
        valid_dirs = []
        for d in os.listdir(path):
            full_dir_path = os.path.join(path, d)
            if os.path.isdir(full_dir_path):
                images = [f for f in os.listdir(full_dir_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
                if images:
                    valid_dirs.append(d)
        return sorted(valid_dirs)

    def _scan(self, path):
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            return []
        return sorted([f for f in os.listdir(path) if f.lower().endswith((".png", ".jpg", ".jpeg"))])

    def _current_face_cards(self):
        current_face_path = self.app.current_fronts_dir
        all_files = self._scan(current_face_path)
        jokers = [f for f in all_files if "joker" in f.lower()]
        current_joker = jokers[0] if jokers else ""
        faces_no_joker = [f for f in all_files if "joker" not in f.lower()]
        filtered = [f for f in faces_no_joker if f.lower().startswith(("a", "j", "q", "k"))]

        suit_order = {"clubs": 0, "diamonds": 1, "spades": 2, "hearts": 3}
        rank_order = {"j": 0, "q": 1, "k": 2, "a": 3}

        def sort_key(name):
            name_l = name.lower()
            suit_val = 99
            for s, val in suit_order.items():
                if s in name_l:
                    suit_val = val
                    break
            rank_val = 99
            for prefix, val in rank_order.items():
                if name_l.startswith(prefix):
                    rank_val = val
                    break
            return (suit_val, rank_val, name_l)

        filtered.sort(key=sort_key)
        cards = filtered[:16] + [""] * (16 - len(filtered[:16]))
        return current_joker, cards

    def draw_text(self, text, pos, size=20, color=TEXT_COLOR, anchor="center"):
        font = pygame.font.SysFont("Arial", size, bold=True)
        surf = font.render(str(text), True, color)
        rect = surf.get_rect(**{anchor: pos})
        self.app.screen.blit(surf, rect)
        return rect

    def draw_selector(self, label, value_text, x, y, width, action_prev, action_next, mouse_pos):
        self.draw_text(label, (x, y), 16, TEXT_DIM, anchor="topleft")
        btn_w, btn_h = 30, 30
        val_w = width - (btn_w * 2) - 10
        l_rect = pygame.Rect(x, y + 25, btn_w, btn_h)
        l_hov = mouse_pos and l_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.app.screen, HIGHLIGHT_COLOR if l_hov else FRAME_COLOR, l_rect, border_radius=6)
        self.draw_text("<", l_rect.center, 18, BG_COLOR if l_hov else TEXT_COLOR)
        self.click_zones.append((l_rect, action_prev))

        val_rect = pygame.Rect(l_rect.right + 5, y + 25, val_w, btn_h)
        pygame.draw.rect(self.app.screen, GRID_BASE_COLOR, val_rect, border_radius=6)
        pygame.draw.rect(self.app.screen, FRAME_COLOR, val_rect, 1, border_radius=6)
        self.draw_text(value_text, val_rect.center, 16, TEXT_COLOR)

        r_rect = pygame.Rect(val_rect.right + 5, y + 25, btn_w, btn_h)
        r_hov = mouse_pos and r_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.app.screen, HIGHLIGHT_COLOR if r_hov else FRAME_COLOR, r_rect, border_radius=6)
        self.draw_text(">", r_rect.center, 18, BG_COLOR if r_hov else TEXT_COLOR)
        self.click_zones.append((r_rect, action_next))

    def draw_stepper(self, label, value, x, y, width, action_minus, action_plus, mouse_pos):
        self.draw_text(label, (x, y), 16, TEXT_DIM, anchor="topleft")
        btn_w, btn_h = 30, 30
        val_w = width - (btn_w * 2) - 10
        m_rect = pygame.Rect(x, y + 25, btn_w, btn_h)
        m_hov = mouse_pos and m_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.app.screen, HIGHLIGHT_COLOR if m_hov else FRAME_COLOR, m_rect, border_radius=6)
        self.draw_text("-", m_rect.center, 22, BG_COLOR if m_hov else TEXT_COLOR)
        self.click_zones.append((m_rect, action_minus))

        val_rect = pygame.Rect(m_rect.right + 5, y + 25, val_w, btn_h)
        pygame.draw.rect(self.app.screen, GRID_BASE_COLOR, val_rect, border_radius=6)
        pygame.draw.rect(self.app.screen, FRAME_COLOR, val_rect, 1, border_radius=6)
        self.draw_text(str(value), val_rect.center, 18, TEXT_COLOR)

        p_rect = pygame.Rect(val_rect.right + 5, y + 25, btn_w, btn_h)
        p_hov = mouse_pos and p_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.app.screen, HIGHLIGHT_COLOR if p_hov else FRAME_COLOR, p_rect, border_radius=6)
        self.draw_text("+", p_rect.center, 20, BG_COLOR if p_hov else TEXT_COLOR)
        self.click_zones.append((p_rect, action_plus))

    def render_main(self, mouse_pos):
        block_rects = self.get_block_rects()
        root_rect = block_rects["menu_root"]

        pygame.draw.rect(self.app.screen, MAIN_PANEL_COLOR, root_rect, border_radius=25)
        pygame.draw.rect(self.app.screen, FRAME_COLOR, root_rect, 3, border_radius=25)
        self.draw_text("SETTINGS", (root_rect.centerx, root_rect.y + 35), 32)

        deck_rect = block_rects["deck_panel"]
        pygame.draw.rect(self.app.screen, SUB_PANEL_COLOR, deck_rect, border_radius=20)

        inner_padding = 60
        grid_h = deck_rect.height - inner_padding * 1.5
        grid_y = deck_rect.y + 70
        portrait_grid = DynamicSquareGrid(parent_height=grid_h, padding=10, spacing_ratio=0.32, aspect_ratio=RATIO_SQUARE)
        faces_grid = DynamicSquareGrid(parent_height=grid_h - 40, padding=10, spacing_ratio=0.1, aspect_ratio=RATIO_CARD)

        card_w = portrait_grid.S * RATIO_CARD
        preview_h = faces_grid.S
        preview_w = preview_h * RATIO_CARD
        gap_between_elements = 30
        combined_faces_width = faces_grid.S + gap_between_elements + preview_w
        total_content_width = portrait_grid.S + gap_between_elements + card_w + gap_between_elements + combined_faces_width
        start_x = deck_rect.x + (deck_rect.width - total_content_width) / 2

        portrait_x = start_x
        card_x = portrait_x + portrait_grid.S + gap_between_elements
        faces_x = card_x + card_w + gap_between_elements
        preview_x = faces_x + faces_grid.S + gap_between_elements
        title_y = grid_y - 15

        self.draw_text("Portraits", (portrait_x + portrait_grid.S / 2, title_y), 22, anchor="midbottom")
        self.draw_text("Card back", (card_x + card_w / 2, title_y), 22, anchor="midbottom")
        self.draw_text("Deck", (faces_x + faces_grid.S / 2, title_y), 22, anchor="midbottom")
        self.draw_text("Preview", (preview_x + preview_w / 2, title_y), 22, anchor="midbottom")

        portraits = [self.app.selected_portrait_files[seat] for seat in ("left", "top", "right", "bottom")]
        portrait_grid.calculate_and_draw(
            self.app.screen,
            portrait_x,
            grid_y,
            portraits,
            self.portraits_dir,
            self.res,
            self.click_zones,
            "edit_p",
            labels=["Bot: Left", "Bot: Top", "Bot: Right", "Player: You"],
            draw_text_fn=self.draw_text,
            mouse_pos=mouse_pos,
            colors={"grid_base": GRID_BASE_COLOR, "frame": FRAME_COLOR, "empty_slot": EMPTY_SLOT_COLOR, "highlight": HIGHLIGHT_COLOR, "text": TEXT_COLOR},
        )

        current_back_file = self.app.custom_back_file or os.path.basename(self.app.option_by_id(CARD_BACK_OPTIONS, self.app.selected_card_back)["path"])
        card_h = portrait_grid.S
        card_y = grid_y
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
        is_card_hovered = mouse_pos and card_rect.collidepoint(mouse_pos)
        if is_card_hovered:
            scale = 1.05
            h_w, h_h = card_w * scale, card_h * scale
            draw_rect = pygame.Rect(card_x - (h_w - card_w) / 2, card_y - (h_h - card_h) / 2, h_w, h_h)
            img = self.res.get_img(self.backs_dir, current_back_file, (int(h_w), int(h_h)))
            self.app.screen.blit(img, draw_rect)
            pygame.draw.rect(self.app.screen, HIGHLIGHT_COLOR, draw_rect, 3, border_radius=10)
        else:
            pygame.draw.rect(self.app.screen, EMPTY_SLOT_COLOR, card_rect, border_radius=10)
            img = self.res.get_img(self.backs_dir, current_back_file, (int(card_w), int(card_h)))
            self.app.screen.blit(img, card_rect)
            pygame.draw.rect(self.app.screen, FRAME_COLOR, card_rect, 1, border_radius=10)
        self.click_zones.append((card_rect, "edit_b_0"))

        current_joker, current_face_cards = self._current_face_cards()
        faces_grid.calculate_and_draw(
            self.app.screen,
            faces_x,
            grid_y,
            current_face_cards,
            self.app.current_fronts_dir,
            self.res,
            self.click_zones,
            "edit_f",
            mouse_pos=mouse_pos,
            colors={"grid_base": GRID_BASE_COLOR, "frame": FRAME_COLOR, "empty_slot": EMPTY_SLOT_COLOR, "highlight": HIGHLIGHT_COLOR, "text": TEXT_COLOR},
        )

        btn_w = faces_grid.S
        btn_rect = pygame.Rect(faces_x, grid_y + faces_grid.S + 4, btn_w, 36)
        is_btn_hovered = mouse_pos and btn_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.app.screen, GRID_BASE_COLOR, btn_rect, border_radius=10)
        pygame.draw.rect(self.app.screen, HIGHLIGHT_COLOR if is_btn_hovered else FRAME_COLOR, btn_rect, width=2, border_radius=10)
        current_face_name = os.path.basename(self.app.current_fronts_dir)
        self.draw_text(f"Deck: {current_face_name}", btn_rect.center, 16, TEXT_COLOR)
        self.click_zones.append((btn_rect, "toggle_dropdown"))

        preview_rect = pygame.Rect(preview_x, grid_y, preview_w, preview_h)
        active_preview_file = current_joker
        for i, f in enumerate(current_face_cards):
            if not f:
                continue
            for rect, action in self.click_zones:
                if action == f"edit_f_{i}" and mouse_pos and rect.collidepoint(mouse_pos):
                    active_preview_file = f
                    break
        pygame.draw.rect(self.app.screen, EMPTY_SLOT_COLOR, preview_rect, border_radius=10)
        if active_preview_file:
            img = self.res.get_img(self.app.current_fronts_dir, active_preview_file, (int(preview_w), int(preview_h)))
            self.app.screen.blit(img, preview_rect)
        pygame.draw.rect(self.app.screen, HIGHLIGHT_COLOR if active_preview_file and active_preview_file != current_joker else FRAME_COLOR, preview_rect, 3 if active_preview_file and active_preview_file != current_joker else 1, border_radius=10)

        game_rect = block_rects["game_settings_panel"]
        pygame.draw.rect(self.app.screen, SUB_PANEL_COLOR, game_rect, border_radius=20)
        self.draw_text("Game settings", (game_rect.centerx, game_rect.y + 20), 24, TEXT_COLOR)
        pygame.draw.line(self.app.screen, FRAME_COLOR, (game_rect.x + 40, game_rect.y + 40), (game_rect.right - 40, game_rect.y + 40), 2)

        col_w = game_rect.width // 3
        pad_x = 40
        ui_w = col_w - pad_x * 2
        start_y = game_rect.y + 60
        y_step = 65

        col1_x = game_rect.x + pad_x
        self.draw_text("Screen & Motion", (col1_x + ui_w / 2, start_y), 18, HIGHLIGHT_COLOR)
        self.draw_selector("Animation speed", ANIMATION_SPEED_LABELS[self.app.selected_animation_speed], col1_x, start_y + 25, ui_w, "anim_prev", "anim_next", mouse_pos)

        col2_x = game_rect.x + col_w + pad_x
        self.draw_text("Match rules", (col2_x + ui_w / 2, start_y), 18, HIGHLIGHT_COLOR)
        self.draw_stepper("Loss limit", self.app.selected_losses_to_finish, col2_x, start_y + 25, ui_w, "loss_minus", "loss_plus", mouse_pos)
        self.draw_selector("Opening move", OPENING_MODE_LABELS[self.app.selected_opening_mode], col2_x, start_y + 25 + y_step, ui_w, "mode_prev", "mode_next", mouse_pos)

        col3_x = game_rect.x + col_w * 2 + pad_x
        self.draw_text("Prepared themes", (col3_x + ui_w / 2, start_y), 18, HIGHLIGHT_COLOR)
        self.draw_text(f"Back sets: {len(CARD_BACK_OPTIONS)}", (col3_x, start_y + 35), 16, TEXT_COLOR, anchor="topleft")
        self.draw_text(f"Face sets: {len(self._scan_dirs(self.faces_base_dir))}", (col3_x, start_y + 65), 16, TEXT_COLOR, anchor="topleft")
        self.draw_text(f"Portrait sets: {len(PORTRAIT_SET_OPTIONS)}", (col3_x, start_y + 95), 16, TEXT_COLOR, anchor="topleft")

        accept_rect = block_rects["start_button"]
        is_accept_hovered = mouse_pos and accept_rect.collidepoint(mouse_pos)
        btn_color = HIGHLIGHT_HOVER if is_accept_hovered else HIGHLIGHT_COLOR
        pygame.draw.rect(self.app.screen, btn_color, accept_rect, border_radius=15)
        pygame.draw.rect(self.app.screen, TEXT_COLOR if is_accept_hovered else FRAME_COLOR, accept_rect, 2, border_radius=15)
        self.draw_text("START PARTY", accept_rect.center, 24, BG_COLOR)
        self.click_zones.append((accept_rect, "accept_config"))

        exit_rect = block_rects["exit_button"]
        is_exit_hovered = mouse_pos and exit_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.app.screen, HIGHLIGHT_HOVER if is_exit_hovered else FRAME_COLOR, exit_rect, border_radius=15)
        pygame.draw.rect(self.app.screen, TEXT_COLOR if is_exit_hovered else FRAME_COLOR, exit_rect, 2, border_radius=15)
        self.draw_text("EXIT", exit_rect.center, 24, BG_COLOR if is_exit_hovered else TEXT_COLOR)
        self.click_zones.append((exit_rect, "exit_app"))

        if self.dropdown_open:
            face_sets = self._scan_dirs(self.faces_base_dir)
            dd_y = btn_rect.bottom + 4
            dd_h = len(face_sets) * 36
            dd_rect = pygame.Rect(btn_rect.x, dd_y, btn_rect.width, dd_h)
            pygame.draw.rect(self.app.screen, MAIN_PANEL_COLOR, dd_rect, border_radius=10)
            pygame.draw.rect(self.app.screen, FRAME_COLOR, dd_rect, width=2, border_radius=10)
            for i, fset in enumerate(face_sets):
                item_rect = pygame.Rect(dd_rect.x, dd_rect.y + i * 36, dd_rect.width, 36)
                is_item_hovered = mouse_pos and item_rect.collidepoint(mouse_pos)
                if is_item_hovered:
                    pygame.draw.rect(self.app.screen, SUB_PANEL_COLOR, item_rect, border_radius=10)
                text_color = HIGHLIGHT_COLOR if os.path.basename(self.app.current_fronts_dir) == fset else TEXT_COLOR
                self.draw_text(f"Deck: {fset}", item_rect.center, 16, text_color)
                self.click_zones.append((item_rect, f"select_fset_{i}"))

    def render_overlay(self, files, folder, title, prefix, aspect_ratio, mouse_pos, labels=None):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.app.screen.blit(overlay, (0, 0))

        modal_h = 500
        modal_grid = DynamicSquareGrid(parent_height=modal_h, padding=20, spacing_ratio=0.1, aspect_ratio=aspect_ratio)
        m_x = (WIDTH - modal_grid.S - 80) // 2
        m_y = (HEIGHT - modal_h - 120) // 2
        modal_bg = pygame.Rect(m_x, m_y, modal_grid.S + 80, modal_h + 120)
        pygame.draw.rect(self.app.screen, MAIN_PANEL_COLOR, modal_bg, border_radius=25)
        pygame.draw.rect(self.app.screen, FRAME_COLOR, modal_bg, 3, border_radius=25)
        self.draw_text(title, (modal_bg.centerx, modal_bg.y + 40), 32, color=TEXT_COLOR)
        modal_grid.calculate_and_draw(
            self.app.screen,
            m_x + 40,
            m_y + 90,
            files,
            folder,
            self.res,
            self.click_zones,
            prefix,
            mouse_pos=mouse_pos,
            labels=labels,
            draw_text_fn=self.draw_text if labels else None,
            colors={"grid_base": GRID_BASE_COLOR, "frame": FRAME_COLOR, "empty_slot": EMPTY_SLOT_COLOR, "highlight": HIGHLIGHT_COLOR, "text": TEXT_COLOR},
        )

    def draw(self, mouse_pos: tuple[int, int]) -> None:
        self.app.screen.fill(BG_COLOR)
        self.click_zones = []
        self.render_main(mouse_pos)
        if self.state == "SELECT_P":
            all_portraits = self._scan(self.portraits_dir)
            self.render_overlay(all_portraits, self.portraits_dir, "CHOOSE PORTRAIT", "set_p", RATIO_SQUARE, mouse_pos)
        elif self.state == "SELECT_B":
            all_backs = self._scan(self.backs_dir)
            self.render_overlay(all_backs, self.backs_dir, "CHOOSE CARD BACK", "set_b", RATIO_CARD, mouse_pos)

    def handle_click(self, pos) -> bool:
        action = next((act for rect, act in self.click_zones if rect.collidepoint(pos)), None)
        config_changed = False
        if self.dropdown_open and action != "toggle_dropdown" and not (action and action.startswith("select_fset_")):
            self.dropdown_open = False
        if not action:
            if self.state != "MAIN":
                self.state = "MAIN"
            return True

        if action == "accept_config":
            self.app.start_match()
        elif action == "exit_app":
            return False
        elif action == "anim_prev":
            modes = ["slow", "normal", "fast"]
            idx = modes.index(self.app.selected_animation_speed)
            self.app.selected_animation_speed = modes[(idx - 1) % len(modes)]
            config_changed = True
        elif action == "anim_next":
            modes = ["slow", "normal", "fast"]
            idx = modes.index(self.app.selected_animation_speed)
            self.app.selected_animation_speed = modes[(idx + 1) % len(modes)]
            config_changed = True
        elif action == "mode_prev":
            modes = ["classic", "player", "random"]
            idx = modes.index(self.app.selected_opening_mode)
            self.app.selected_opening_mode = modes[(idx - 1) % len(modes)]
            config_changed = True
        elif action == "mode_next":
            modes = ["classic", "player", "random"]
            idx = modes.index(self.app.selected_opening_mode)
            self.app.selected_opening_mode = modes[(idx + 1) % len(modes)]
            config_changed = True
        elif action == "loss_minus":
            self.app.selected_losses_to_finish = max(1, self.app.selected_losses_to_finish - 1)
            config_changed = True
        elif action == "loss_plus":
            self.app.selected_losses_to_finish = min(6, self.app.selected_losses_to_finish + 1)
            config_changed = True
        elif action == "toggle_dropdown":
            self.dropdown_open = not self.dropdown_open
        elif action.startswith("select_fset_"):
            idx = int(action.split("_")[-1])
            face_sets = self._scan_dirs(self.faces_base_dir)
            if idx < len(face_sets):
                selected_dir = face_sets[idx]
                self.app.current_fronts_dir = os.path.join(self.faces_base_dir, selected_dir)
                selected_option = next(
                    (
                        option["id"]
                        for option in CARD_FACE_OPTIONS
                        if os.path.basename(option["path"]) == selected_dir
                    ),
                    "default",
                )
                self.app.selected_card_faces = selected_option
                self.app.card_front_cache.clear()
                config_changed = True
            self.dropdown_open = False
        elif action.startswith("edit_p_"):
            self.editing_idx = int(action.split("_")[-1])
            self.state = "SELECT_P"
            self.dropdown_open = False
        elif action.startswith("edit_b_"):
            self.state = "SELECT_B"
            self.dropdown_open = False
        elif action.startswith("set_p_"):
            portraits = self._scan(self.portraits_dir)
            idx = int(action.split("_")[-1])
            if idx < len(portraits):
                seat = ["left", "top", "right", "bottom"][self.editing_idx]
                self.app.selected_portrait_files[seat] = portraits[idx]
                self.app.load_visual_assets()
                config_changed = True
            self.state = "MAIN"
        elif action.startswith("set_b_"):
            backs = self._scan(self.backs_dir)
            idx = int(action.split("_")[-1])
            if idx < len(backs):
                self.app.custom_back_file = backs[idx]
                self.app.selected_card_back = "default"
                self.app.load_visual_assets()
                config_changed = True
            self.state = "MAIN"
        if config_changed:
            self.app.save_persistent_config()
        return True
