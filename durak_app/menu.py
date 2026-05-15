import math
import os

import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIImage, UILabel, UIPanel

from .config import (
    ANIMATION_SPEED_LABELS,
    CARD_BACK_OPTIONS,
    CARD_FACE_OPTIONS,
    HEIGHT,
    OPENING_MODE_LABELS,
    PORTRAIT_SET_OPTIONS,
    WIDTH,
)
from .menu_support import DynamicSquareGrid, ResourceManager

RATIO_SQUARE = 1.0
RATIO_CARD = 0.66

BG_COLOR = (15, 15, 25)
EMPTY_SLOT_COLOR = (35, 40, 60)
FRAME_COLOR = (80, 95, 130)


class MainMenuScreen:
    def __init__(self, app):
        self.app = app
        self.manager = app.ui_controller.manager
        self.res = ResourceManager(EMPTY_SLOT_COLOR, FRAME_COLOR)
        self.state = "MAIN"
        self.dropdown_open = False
        self.editing_idx = 0

        self.root_panel = UIPanel(relative_rect=pygame.Rect(0, 0, 100, 100), manager=self.manager, object_id="#menu_root_panel")
        self.title_label = UILabel(relative_rect=pygame.Rect(0, 0, 300, 50), text="Settings", manager=self.manager, container=self.root_panel, object_id="#menu_title")

        self.deck_panel = UIPanel(relative_rect=pygame.Rect(0, 0, 100, 100), manager=self.manager, container=self.root_panel, object_id="#menu_sub_panel")
        self.settings_panel = UIPanel(relative_rect=pygame.Rect(0, 0, 100, 100), manager=self.manager, container=self.root_panel, object_id="#menu_sub_panel")

        self.portraits_title = UILabel(relative_rect=pygame.Rect(0, 0, 200, 28), text="Portraits", manager=self.manager, container=self.deck_panel, object_id="#menu_section")
        self.back_title = UILabel(relative_rect=pygame.Rect(0, 0, 200, 28), text="Card back", manager=self.manager, container=self.deck_panel, object_id="#menu_section")
        self.faces_title = UILabel(relative_rect=pygame.Rect(0, 0, 200, 28), text="Deck", manager=self.manager, container=self.deck_panel, object_id="#menu_section")
        self.preview_title = UILabel(relative_rect=pygame.Rect(0, 0, 200, 28), text="Preview", manager=self.manager, container=self.deck_panel, object_id="#menu_section")

        self.portrait_images: list[UIImage] = []
        self.portrait_buttons: list[UIButton] = []
        self.portrait_labels: list[UILabel] = []
        for text in ["Bot: Left", "Bot: Top", "Bot: Right", "Player: You"]:
            image = UIImage(relative_rect=pygame.Rect(0, 0, 60, 60), image_surface=pygame.Surface((60, 60)), manager=self.manager, container=self.deck_panel)
            button = UIButton(relative_rect=pygame.Rect(0, 0, 60, 60), text="", manager=self.manager, container=self.deck_panel, object_id="#menu_image_button")
            label = UILabel(relative_rect=pygame.Rect(0, 0, 150, 24), text=text, manager=self.manager, container=self.deck_panel, object_id="#menu_small_text")
            self.portrait_images.append(image)
            self.portrait_buttons.append(button)
            self.portrait_labels.append(label)

        self.back_image = UIImage(relative_rect=pygame.Rect(0, 0, 60, 90), image_surface=pygame.Surface((60, 90)), manager=self.manager, container=self.deck_panel)
        self.back_button = UIButton(relative_rect=pygame.Rect(0, 0, 60, 90), text="", manager=self.manager, container=self.deck_panel, object_id="#menu_image_button")

        self.face_images: list[UIImage] = []
        self.face_buttons: list[UIButton] = []
        for _ in range(16):
            image = UIImage(relative_rect=pygame.Rect(0, 0, 40, 60), image_surface=pygame.Surface((40, 60)), manager=self.manager, container=self.deck_panel)
            button = UIButton(relative_rect=pygame.Rect(0, 0, 40, 60), text="", manager=self.manager, container=self.deck_panel, object_id="#menu_image_button")
            self.face_images.append(image)
            self.face_buttons.append(button)

        self.preview_image = UIImage(relative_rect=pygame.Rect(0, 0, 80, 120), image_surface=pygame.Surface((80, 120)), manager=self.manager, container=self.deck_panel)
        self.face_set_button = UIButton(relative_rect=pygame.Rect(0, 0, 200, 36), text="", manager=self.manager, container=self.deck_panel, object_id="#menu_value_button")

        self.settings_title = UILabel(relative_rect=pygame.Rect(0, 0, 240, 30), text="Game settings", manager=self.manager, container=self.settings_panel, object_id="#menu_section")

        self.anim_label = UILabel(relative_rect=pygame.Rect(0, 0, 180, 24), text="Animation speed", manager=self.manager, container=self.settings_panel, object_id="#menu_small_text")
        self.anim_prev = UIButton(relative_rect=pygame.Rect(0, 0, 30, 30), text="<", manager=self.manager, container=self.settings_panel, object_id="#menu_small_button")
        self.anim_value = UILabel(relative_rect=pygame.Rect(0, 0, 180, 30), text="", manager=self.manager, container=self.settings_panel, object_id="#menu_value_label")
        self.anim_next = UIButton(relative_rect=pygame.Rect(0, 0, 30, 30), text=">", manager=self.manager, container=self.settings_panel, object_id="#menu_small_button")

        self.loss_label = UILabel(relative_rect=pygame.Rect(0, 0, 180, 24), text="Loss limit", manager=self.manager, container=self.settings_panel, object_id="#menu_small_text")
        self.loss_minus = UIButton(relative_rect=pygame.Rect(0, 0, 30, 30), text="-", manager=self.manager, container=self.settings_panel, object_id="#menu_small_button")
        self.loss_value = UILabel(relative_rect=pygame.Rect(0, 0, 180, 30), text="", manager=self.manager, container=self.settings_panel, object_id="#menu_value_label")
        self.loss_plus = UIButton(relative_rect=pygame.Rect(0, 0, 30, 30), text="+", manager=self.manager, container=self.settings_panel, object_id="#menu_small_button")

        self.mode_label = UILabel(relative_rect=pygame.Rect(0, 0, 180, 24), text="Opening move", manager=self.manager, container=self.settings_panel, object_id="#menu_small_text")
        self.mode_prev = UIButton(relative_rect=pygame.Rect(0, 0, 30, 30), text="<", manager=self.manager, container=self.settings_panel, object_id="#menu_small_button")
        self.mode_value = UILabel(relative_rect=pygame.Rect(0, 0, 180, 30), text="", manager=self.manager, container=self.settings_panel, object_id="#menu_value_label")
        self.mode_next = UIButton(relative_rect=pygame.Rect(0, 0, 30, 30), text=">", manager=self.manager, container=self.settings_panel, object_id="#menu_small_button")

        self.prepared_title = UILabel(relative_rect=pygame.Rect(0, 0, 220, 24), text="Prepared themes", manager=self.manager, container=self.settings_panel, object_id="#menu_small_text")
        self.back_count = UILabel(relative_rect=pygame.Rect(0, 0, 220, 24), text="", manager=self.manager, container=self.settings_panel, object_id="#menu_plain_text")
        self.face_count = UILabel(relative_rect=pygame.Rect(0, 0, 220, 24), text="", manager=self.manager, container=self.settings_panel, object_id="#menu_plain_text")
        self.portrait_count = UILabel(relative_rect=pygame.Rect(0, 0, 220, 24), text="", manager=self.manager, container=self.settings_panel, object_id="#menu_plain_text")

        self.start_button = UIButton(relative_rect=pygame.Rect(0, 0, 240, 50), text="Start party", manager=self.manager, container=self.root_panel, object_id="#primary_button")
        self.exit_button = UIButton(relative_rect=pygame.Rect(0, 0, 180, 50), text="Exit", manager=self.manager, container=self.root_panel, object_id="#action_button")

        self.dropdown_panel = UIPanel(relative_rect=pygame.Rect(0, 0, 100, 100), manager=self.manager, container=self.root_panel, object_id="#menu_dropdown_panel")
        self.dropdown_buttons: list[UIButton] = []

        self.overlay_panel = UIPanel(relative_rect=pygame.Rect(0, 0, 100, 100), manager=self.manager, object_id="#menu_overlay_panel")
        self.overlay_title = UILabel(relative_rect=pygame.Rect(0, 0, 400, 36), text="", manager=self.manager, container=self.overlay_panel, object_id="#menu_title")
        self.overlay_images: list[UIImage] = []
        self.overlay_buttons: list[UIButton] = []

        self._hide_optional_panels()

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

    def _grid_item_rects(self, x, y, items, grid: DynamicSquareGrid, labels: bool = False):
        rects = []
        total_elements = len(items)
        if total_elements == 0:
            return rects
        n = 2 if total_elements <= 4 else math.ceil(math.sqrt(total_elements))
        n = max(1, n)
        cell_size = grid.S / n
        item_h = cell_size * (1 - grid.spacing_ratio)
        item_w = item_h * grid.aspect_ratio
        offset_x = (cell_size - item_w) / 2
        text_space = 24 if labels else 0
        free_space_y = cell_size - (item_h + text_space)
        offset_y = (free_space_y / 3) * 2 if labels else free_space_y / 2
        for k in range(total_elements):
            row = math.floor(k / n)
            col = k % n
            x_local = col * cell_size
            y_local = row * cell_size
            final_x = x + x_local + offset_x
            final_y = y + y_local + offset_y
            rects.append(pygame.Rect(int(final_x), int(final_y), int(item_w), int(item_h)))
        return rects

    def compute_main_layout(self):
        block_rects = self.get_block_rects()
        root_rect = block_rects["menu_root"]
        deck_rect = block_rects["deck_panel"]
        game_rect = block_rects["game_settings_panel"]
        start_rect = block_rects["start_button"]
        exit_rect = block_rects["exit_button"]

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

        portraits = [self.app.selected_portrait_files[seat] for seat in ("left", "top", "right", "bottom")]
        current_joker, current_face_cards = self._current_face_cards()
        current_back_file = self.app.custom_back_file or os.path.basename(self.app.option_by_id(CARD_BACK_OPTIONS, self.app.selected_card_back)["path"])

        btn_rect = pygame.Rect(faces_x, grid_y + faces_grid.S + 4, faces_grid.S, 36)

        col_w = game_rect.width // 3
        pad_x = 40
        ui_w = col_w - pad_x * 2
        start_y = game_rect.y + 60
        y_step = 65
        col1_x = game_rect.x + pad_x
        col2_x = game_rect.x + col_w + pad_x
        col3_x = game_rect.x + col_w * 2 + pad_x

        return {
            "block_rects": block_rects,
            "root_rect": root_rect,
            "deck_rect": deck_rect,
            "game_rect": game_rect,
            "start_rect": start_rect,
            "exit_rect": exit_rect,
            "portrait_grid": portrait_grid,
            "faces_grid": faces_grid,
            "grid_y": grid_y,
            "portrait_x": portrait_x,
            "card_x": card_x,
            "card_w": card_w,
            "faces_x": faces_x,
            "preview_x": preview_x,
            "preview_h": preview_h,
            "preview_w": preview_w,
            "portraits": portraits,
            "current_joker": current_joker,
            "current_face_cards": current_face_cards,
            "current_back_file": current_back_file,
            "btn_rect": btn_rect,
            "col1_x": col1_x,
            "col2_x": col2_x,
            "col3_x": col3_x,
            "ui_w": ui_w,
            "start_y": start_y,
            "y_step": y_step,
        }

    def _hide_optional_panels(self) -> None:
        self.dropdown_panel.hide()
        self.overlay_panel.hide()

    def _ensure_dynamic_ui_count(self, images: list[UIImage], buttons: list[UIButton], count: int, container: UIPanel, button_id: str) -> None:
        while len(images) < count:
            images.append(UIImage(relative_rect=pygame.Rect(0, 0, 60, 60), image_surface=pygame.Surface((60, 60)), manager=self.manager, container=container))
            buttons.append(UIButton(relative_rect=pygame.Rect(0, 0, 60, 60), text="", manager=self.manager, container=container, object_id=button_id))

    def _ensure_dropdown_count(self, count: int) -> None:
        while len(self.dropdown_buttons) < count:
            self.dropdown_buttons.append(
                UIButton(relative_rect=pygame.Rect(0, 0, 220, 32), text="", manager=self.manager, container=self.dropdown_panel, object_id="#menu_option_button")
            )

    def _surface_for_file(self, folder: str, filename: str, size: tuple[int, int]) -> pygame.Surface:
        if not filename:
            surface = pygame.Surface(size, pygame.SRCALPHA)
            surface.fill(EMPTY_SLOT_COLOR)
            return surface
        return self.res.get_img(folder, filename, size)

    def _sync_main_layout(self) -> dict:
        layout = self.compute_main_layout()
        root_rect = layout["root_rect"]
        deck_rect = layout["deck_rect"]
        game_rect = layout["game_rect"]
        start_rect = layout["start_rect"]
        exit_rect = layout["exit_rect"]

        self.root_panel.set_relative_position((root_rect.x, root_rect.y))
        self.root_panel.set_dimensions((root_rect.width, root_rect.height))
        self.deck_panel.set_relative_position((deck_rect.x - root_rect.x, deck_rect.y - root_rect.y))
        self.deck_panel.set_dimensions((deck_rect.width, deck_rect.height))
        self.settings_panel.set_relative_position((game_rect.x - root_rect.x, game_rect.y - root_rect.y))
        self.settings_panel.set_dimensions((game_rect.width, game_rect.height))
        self.start_button.set_relative_position((start_rect.x - root_rect.x, start_rect.y - root_rect.y))
        self.start_button.set_dimensions((start_rect.width, start_rect.height))
        self.exit_button.set_relative_position((exit_rect.x - root_rect.x, exit_rect.y - root_rect.y))
        self.exit_button.set_dimensions((exit_rect.width, exit_rect.height))

        self.title_label.set_relative_position(((root_rect.width - 300) // 2, 18))

        deck_local_x = deck_rect.x
        deck_local_y = deck_rect.y
        game_local_x = game_rect.x
        game_local_y = game_rect.y

        title_y = layout["grid_y"] - deck_local_y - 30
        self.portraits_title.set_relative_position((layout["portrait_x"] - deck_local_x + max(0, int((layout["portrait_grid"].S - 200) / 2)), title_y))
        self.back_title.set_relative_position((layout["card_x"] - deck_local_x + max(0, int((layout["card_w"] - 200) / 2)), title_y))
        self.faces_title.set_relative_position((layout["faces_x"] - deck_local_x + max(0, int((layout["faces_grid"].S - 200) / 2)), title_y))
        self.preview_title.set_relative_position((layout["preview_x"] - deck_local_x + max(0, int((layout["preview_w"] - 200) / 2)), title_y))

        portrait_rects = self._grid_item_rects(layout["portrait_x"], layout["grid_y"], layout["portraits"], layout["portrait_grid"], labels=True)
        for idx, rect in enumerate(portrait_rects[:4]):
            local_rect = rect.move(-deck_local_x, -deck_local_y)
            self.portrait_images[idx].set_relative_position((local_rect.x, local_rect.y))
            self.portrait_images[idx].set_dimensions((local_rect.width, local_rect.height))
            self.portrait_buttons[idx].set_relative_position((local_rect.x, local_rect.y))
            self.portrait_buttons[idx].set_dimensions((local_rect.width, local_rect.height))
            self.portrait_labels[idx].set_relative_position((local_rect.x - 20, local_rect.bottom + 4))

        back_rect = pygame.Rect(int(layout["card_x"]), int(layout["grid_y"]), int(layout["card_w"]), int(layout["portrait_grid"].S))
        back_local = back_rect.move(-deck_local_x, -deck_local_y)
        self.back_image.set_relative_position((back_local.x, back_local.y))
        self.back_image.set_dimensions((back_local.width, back_local.height))
        self.back_button.set_relative_position((back_local.x, back_local.y))
        self.back_button.set_dimensions((back_local.width, back_local.height))

        face_rects = self._grid_item_rects(layout["faces_x"], layout["grid_y"], layout["current_face_cards"], layout["faces_grid"])
        for idx, rect in enumerate(face_rects):
            local_rect = rect.move(-deck_local_x, -deck_local_y)
            self.face_images[idx].set_relative_position((local_rect.x, local_rect.y))
            self.face_images[idx].set_dimensions((local_rect.width, local_rect.height))
            self.face_buttons[idx].set_relative_position((local_rect.x, local_rect.y))
            self.face_buttons[idx].set_dimensions((local_rect.width, local_rect.height))
            self.face_images[idx].show()
            self.face_buttons[idx].show()
        for idx in range(len(face_rects), len(self.face_images)):
            self.face_images[idx].hide()
            self.face_buttons[idx].hide()

        preview_local = pygame.Rect(int(layout["preview_x"] - deck_local_x), int(layout["grid_y"] - deck_local_y), int(layout["preview_w"]), int(layout["preview_h"]))
        self.preview_image.set_relative_position((preview_local.x, preview_local.y))
        self.preview_image.set_dimensions((preview_local.width, preview_local.height))

        btn_local = layout["btn_rect"].move(-deck_local_x, -deck_local_y)
        self.face_set_button.set_relative_position((btn_local.x, btn_local.y))
        self.face_set_button.set_dimensions((btn_local.width, btn_local.height))

        self.settings_title.set_relative_position(((game_rect.width - 240) // 2, 16))

        col1_x = layout["col1_x"] - game_local_x
        col2_x = layout["col2_x"] - game_local_x
        col3_x = layout["col3_x"] - game_local_x
        ui_w = layout["ui_w"]
        start_y = layout["start_y"] - game_local_y
        y_step = layout["y_step"]
        btn_w, btn_h = 30, 30
        val_w = ui_w - (btn_w * 2) - 10

        self.anim_label.set_relative_position((col1_x, start_y + 10))
        self.anim_prev.set_relative_position((col1_x, start_y + 42))
        self.anim_prev.set_dimensions((btn_w, btn_h))
        self.anim_value.set_relative_position((col1_x + btn_w + 5, start_y + 42))
        self.anim_value.set_dimensions((val_w, btn_h))
        self.anim_next.set_relative_position((col1_x + btn_w + 5 + val_w + 5, start_y + 42))
        self.anim_next.set_dimensions((btn_w, btn_h))

        self.loss_label.set_relative_position((col2_x, start_y + 10))
        self.loss_minus.set_relative_position((col2_x, start_y + 42))
        self.loss_minus.set_dimensions((btn_w, btn_h))
        self.loss_value.set_relative_position((col2_x + btn_w + 5, start_y + 42))
        self.loss_value.set_dimensions((val_w, btn_h))
        self.loss_plus.set_relative_position((col2_x + btn_w + 5 + val_w + 5, start_y + 42))
        self.loss_plus.set_dimensions((btn_w, btn_h))

        self.mode_label.set_relative_position((col2_x, start_y + 10 + y_step))
        self.mode_prev.set_relative_position((col2_x, start_y + 42 + y_step))
        self.mode_prev.set_dimensions((btn_w, btn_h))
        self.mode_value.set_relative_position((col2_x + btn_w + 5, start_y + 42 + y_step))
        self.mode_value.set_dimensions((val_w, btn_h))
        self.mode_next.set_relative_position((col2_x + btn_w + 5 + val_w + 5, start_y + 42 + y_step))
        self.mode_next.set_dimensions((btn_w, btn_h))

        self.prepared_title.set_relative_position((col3_x, start_y + 10))
        self.back_count.set_relative_position((col3_x, start_y + 46))
        self.face_count.set_relative_position((col3_x, start_y + 74))
        self.portrait_count.set_relative_position((col3_x, start_y + 102))

        return layout

    def _sync_content(self, layout: dict, mouse_pos: tuple[int, int]) -> None:
        portraits = layout["portraits"]
        current_back_file = layout["current_back_file"]
        current_joker = layout["current_joker"]
        current_face_cards = layout["current_face_cards"]

        for idx, filename in enumerate(portraits):
            rect = self.portrait_images[idx].get_abs_rect()
            self.portrait_images[idx].set_image(self._surface_for_file(self.portraits_dir, filename, rect.size))

        back_rect = self.back_image.get_abs_rect()
        self.back_image.set_image(self._surface_for_file(self.backs_dir, current_back_file, back_rect.size))

        hover_preview = current_joker
        for idx, filename in enumerate(current_face_cards):
            rect = self.face_images[idx].get_abs_rect()
            self.face_images[idx].set_image(self._surface_for_file(self.app.current_fronts_dir, filename, rect.size))
            if filename and self.face_buttons[idx].get_abs_rect().collidepoint(mouse_pos):
                hover_preview = filename

        preview_rect = self.preview_image.get_abs_rect()
        self.preview_image.set_image(self._surface_for_file(self.app.current_fronts_dir, hover_preview, preview_rect.size))

        self.face_set_button.set_text(f"Deck: {os.path.basename(self.app.current_fronts_dir)}")
        self.anim_value.set_text(ANIMATION_SPEED_LABELS[self.app.selected_animation_speed])
        self.loss_value.set_text(str(self.app.selected_losses_to_finish))
        self.mode_value.set_text(OPENING_MODE_LABELS[self.app.selected_opening_mode])
        self.back_count.set_text(f"Back sets: {len(CARD_BACK_OPTIONS)}")
        self.face_count.set_text(f"Face sets: {len(self._scan_dirs(self.faces_base_dir))}")
        self.portrait_count.set_text(f"Portrait sets: {len(PORTRAIT_SET_OPTIONS)}")

        self._sync_dropdown()
        self._sync_overlay()

    def _sync_dropdown(self) -> None:
        if not self.dropdown_open or not self.app.menu_visible:
            self.dropdown_panel.hide()
            for button in self.dropdown_buttons:
                button.hide()
            return

        face_sets = self._scan_dirs(self.faces_base_dir)
        self._ensure_dropdown_count(len(face_sets))
        button_rect = self.face_set_button.get_abs_rect()
        root_rect = self.root_panel.get_abs_rect()
        height = max(42, len(face_sets) * 36 + 8)
        self.dropdown_panel.set_relative_position((button_rect.x - root_rect.x, button_rect.bottom - root_rect.y + 4))
        self.dropdown_panel.set_dimensions((button_rect.width, height))
        self.dropdown_panel.show()
        for idx, button in enumerate(self.dropdown_buttons):
            if idx < len(face_sets):
                button.set_relative_position((4, 4 + idx * 36))
                button.set_dimensions((button_rect.width - 8, 32))
                button.set_text(face_sets[idx])
                button.show()
            else:
                button.hide()

    def _sync_overlay(self) -> None:
        if self.state not in {"SELECT_P", "SELECT_B"} or not self.app.menu_visible:
            self.overlay_panel.hide()
            for image in self.overlay_images:
                image.hide()
            for button in self.overlay_buttons:
                button.hide()
            return

        files = self._scan(self.portraits_dir) if self.state == "SELECT_P" else self._scan(self.backs_dir)
        aspect_ratio = RATIO_SQUARE if self.state == "SELECT_P" else RATIO_CARD
        modal_h = 500
        modal_grid = DynamicSquareGrid(parent_height=modal_h, padding=20, spacing_ratio=0.1, aspect_ratio=aspect_ratio)
        m_x = (WIDTH - modal_grid.S - 80) // 2
        m_y = (HEIGHT - modal_h - 120) // 2
        overlay_rect = pygame.Rect(m_x, m_y, modal_grid.S + 80, modal_h + 120)
        self.overlay_panel.set_relative_position((overlay_rect.x, overlay_rect.y))
        self.overlay_panel.set_dimensions((overlay_rect.width, overlay_rect.height))
        self.overlay_title.set_relative_position(((overlay_rect.width - 400) // 2, 20))
        self.overlay_title.set_text("Choose portrait" if self.state == "SELECT_P" else "Choose card back")
        self.overlay_panel.show()

        rects = self._grid_item_rects(m_x + 40, m_y + 90, files, modal_grid, labels=self.state == "SELECT_P")
        self._ensure_dynamic_ui_count(self.overlay_images, self.overlay_buttons, len(rects), self.overlay_panel, "#menu_image_button")
        for idx, rect in enumerate(rects):
            local_rect = rect.move(-overlay_rect.x, -overlay_rect.y)
            self.overlay_images[idx].set_relative_position((local_rect.x, local_rect.y))
            self.overlay_images[idx].set_dimensions((local_rect.width, local_rect.height))
            self.overlay_buttons[idx].set_relative_position((local_rect.x, local_rect.y))
            self.overlay_buttons[idx].set_dimensions((local_rect.width, local_rect.height))
            folder = self.portraits_dir if self.state == "SELECT_P" else self.backs_dir
            self.overlay_images[idx].set_image(self._surface_for_file(folder, files[idx], rect.size))
            self.overlay_images[idx].show()
            self.overlay_buttons[idx].show()
        for idx in range(len(rects), len(self.overlay_images)):
            self.overlay_images[idx].hide()
            self.overlay_buttons[idx].hide()

    def sync_ui(self, mouse_pos: tuple[int, int]) -> None:
        if not self.app.menu_visible:
            self.root_panel.hide()
            self.dropdown_panel.hide()
            self.overlay_panel.hide()
            return
        self.root_panel.show()
        layout = self._sync_main_layout()
        self._sync_content(layout, mouse_pos)

    def draw(self, mouse_pos: tuple[int, int]) -> None:
        self.app.screen.fill(BG_COLOR)
        self.sync_ui(mouse_pos)

    def process_event(self, event: pygame.event.Event) -> bool:
        if event.type != pygame_gui.UI_BUTTON_PRESSED:
            return False

        ui = event.ui_element

        if ui == self.start_button:
            self.app.start_match()
            return True
        if ui == self.exit_button:
            self.app.request_quit = True
            return True

        if ui == self.anim_prev:
            modes = ["slow", "normal", "fast"]
            idx = modes.index(self.app.selected_animation_speed)
            self.app.selected_animation_speed = modes[(idx - 1) % len(modes)]
            self.app.save_persistent_config()
            return True
        if ui == self.anim_next:
            modes = ["slow", "normal", "fast"]
            idx = modes.index(self.app.selected_animation_speed)
            self.app.selected_animation_speed = modes[(idx + 1) % len(modes)]
            self.app.save_persistent_config()
            return True
        if ui == self.loss_minus:
            self.app.selected_losses_to_finish = max(1, self.app.selected_losses_to_finish - 1)
            self.app.save_persistent_config()
            return True
        if ui == self.loss_plus:
            self.app.selected_losses_to_finish = min(6, self.app.selected_losses_to_finish + 1)
            self.app.save_persistent_config()
            return True
        if ui == self.mode_prev:
            modes = ["classic", "player", "random"]
            idx = modes.index(self.app.selected_opening_mode)
            self.app.selected_opening_mode = modes[(idx - 1) % len(modes)]
            self.app.save_persistent_config()
            return True
        if ui == self.mode_next:
            modes = ["classic", "player", "random"]
            idx = modes.index(self.app.selected_opening_mode)
            self.app.selected_opening_mode = modes[(idx + 1) % len(modes)]
            self.app.save_persistent_config()
            return True
        if ui == self.face_set_button:
            self.dropdown_open = not self.dropdown_open
            return True
        if ui == self.back_button:
            self.state = "SELECT_B"
            self.dropdown_open = False
            return True

        for idx, button in enumerate(self.portrait_buttons):
            if ui == button:
                self.editing_idx = idx
                self.state = "SELECT_P"
                self.dropdown_open = False
                return True

        for idx, button in enumerate(self.dropdown_buttons):
            if ui == button and idx < len(self._scan_dirs(self.faces_base_dir)):
                selected_dir = self._scan_dirs(self.faces_base_dir)[idx]
                self.app.current_fronts_dir = os.path.join(self.faces_base_dir, selected_dir)
                selected_option = next(
                    (option["id"] for option in CARD_FACE_OPTIONS if os.path.basename(option["path"]) == selected_dir),
                    "default",
                )
                self.app.selected_card_faces = selected_option
                self.app.card_front_cache.clear()
                self.app.save_persistent_config()
                self.dropdown_open = False
                return True

        for idx, button in enumerate(self.overlay_buttons):
            if ui != button:
                continue
            if self.state == "SELECT_P":
                portraits = self._scan(self.portraits_dir)
                if idx < len(portraits):
                    seat = ["left", "top", "right", "bottom"][self.editing_idx]
                    self.app.selected_portrait_files[seat] = portraits[idx]
                    self.app.load_visual_assets()
                    self.app.save_persistent_config()
                self.state = "MAIN"
                return True
            if self.state == "SELECT_B":
                backs = self._scan(self.backs_dir)
                if idx < len(backs):
                    self.app.custom_back_file = backs[idx]
                    self.app.selected_card_back = "default"
                    self.app.load_visual_assets()
                    self.app.save_persistent_config()
                self.state = "MAIN"
                return True

        return False
