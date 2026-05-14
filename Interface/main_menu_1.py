import pygame
import math
import sys
import os

# --- КОНСТАНТЫ ---
WIDTH, HEIGHT = 1600, 900
FPS = 60

# Пропорции
RATIO_SQUARE = 1.0  # 1:1
RATIO_CARD = 0.66  # ~2:3

# Цвета
BG_COLOR = (15, 15, 25)
MAIN_PANEL_COLOR = (30, 35, 55)
SUB_PANEL_COLOR = (40, 50, 80)
GRID_BASE_COLOR = (25, 30, 50)
FRAME_COLOR = (80, 95, 130)
EMPTY_SLOT_COLOR = (35, 40, 60)
HIGHLIGHT_COLOR = (80, 210, 80)
HIGHLIGHT_HOVER = (100, 255, 100)
TEXT_COLOR = (200, 210, 230)
TEXT_DIM = (130, 140, 160)

# Пути
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
PORTRAITS_DIR = os.path.join(BASE_PATH, "../assets", "portraits")
BACKS_DIR = os.path.join(BASE_PATH, "../assets", "cards", "backs")
FACES_BASE_DIR = os.path.join(BASE_PATH, "../assets", "cards", "faces")

# Имена игроков для подписей
PLAYERS_NAMES = ["Bot: Left", "Bot: Top", "Bot: Right", "Player: You"]


class ResourceManager:
    def __init__(self):
        self.cache = {}

    def get_img(self, folder, filename, size):
        size_int = (int(size[0]), int(size[1]))
        if not filename:
            return self._make_placeholder(size_int)

        # ИСПРАВЛЕНИЕ: Добавляем folder в ключ кэша, чтобы
        # одинаковые имена файлов из разных папок не конфликтовали
        key = (folder, filename, size_int)

        if key not in self.cache:
            path = os.path.join(folder, filename) if folder else filename
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, size_int)
                self.cache[key] = img
            except Exception:
                self.cache[key] = self._make_placeholder(size_int)
        return self.cache[key]

    def _make_placeholder(self, size):
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surf, EMPTY_SLOT_COLOR, (0, 0, *size), border_radius=10)
        pygame.draw.rect(surf, FRAME_COLOR, (0, 0, *size), 1, border_radius=10)
        return surf

class DynamicSquareGrid:
    def __init__(self, parent_height, padding, spacing_ratio=0.1, aspect_ratio=1.0):
        self.parent_height = parent_height
        self.padding = padding
        self.spacing_ratio = spacing_ratio
        self.aspect_ratio = aspect_ratio
        self.S = parent_height - (2 * padding)
        self.rect = pygame.Rect(0, 0, self.S, self.S)

    def calculate_and_draw(self, surface, x, y, items, res_folder, res_manager, click_list, action_prefix, labels=None,
                           draw_text_fn=None, mouse_pos=None):
        total_elements = len(items)

        if total_elements <= 4:
            N = 2
        else:
            N = math.ceil(math.sqrt(total_elements))
        N = max(1, N)

        cell_size = self.S / N
        item_h = cell_size * (1 - self.spacing_ratio)
        item_w = item_h * self.aspect_ratio

        offset_x = (cell_size - item_w) / 2
        text_space = 24 if labels else 0
        free_space_y = cell_size - (item_h + text_space)

        if labels:
            offset_y = (free_space_y / 3) * 2
        else:
            offset_y = free_space_y / 2

        self.rect.x = x
        self.rect.y = y

        pygame.draw.rect(surface, GRID_BASE_COLOR, self.rect, border_radius=12)
        pygame.draw.rect(surface, FRAME_COLOR, self.rect, 1, border_radius=12)

        total_cells = N * N
        for k in range(total_cells):
            row = math.floor(k / N)
            col = k % N

            x_local = col * cell_size
            y_local = row * cell_size

            final_x = self.rect.x + x_local + offset_x
            final_y = self.rect.y + y_local + offset_y

            current_rect = pygame.Rect(final_x, final_y, item_w, item_h)
            is_hovered = mouse_pos and current_rect.collidepoint(mouse_pos)

            if k < total_elements:
                if is_hovered:
                    scale = 1.05
                    hover_w = item_w * scale
                    hover_h = item_h * scale
                    hover_x = final_x - (hover_w - item_w) / 2
                    hover_y = final_y - (hover_h - item_h) / 2

                    draw_rect = pygame.Rect(hover_x, hover_y, hover_w, hover_h)
                    size_int = (int(hover_w), int(hover_h))

                    img = res_manager.get_img(res_folder, items[k], size_int)
                    surface.blit(img, draw_rect)
                    pygame.draw.rect(surface, HIGHLIGHT_COLOR, draw_rect, width=3, border_radius=10)
                else:
                    size_int = (int(item_w), int(item_h))
                    img = res_manager.get_img(res_folder, items[k], size_int)
                    surface.blit(img, current_rect)
                    pygame.draw.rect(surface, FRAME_COLOR, current_rect, width=1, border_radius=10)

                click_list.append((current_rect, f"{action_prefix}_{k}"))
            else:
                pygame.draw.rect(surface, EMPTY_SLOT_COLOR, current_rect, border_radius=10)
                pygame.draw.rect(surface, FRAME_COLOR, current_rect, 1, border_radius=10)

            if labels and k < len(labels) and draw_text_fn:
                text_y = current_rect.bottom + 5
                label_color = HIGHLIGHT_COLOR if is_hovered else TEXT_COLOR
                draw_text_fn(labels[k], (current_rect.centerx, text_y), size=14, color=label_color, anchor="midtop")


# --- ГЛАВНОЕ ОКНО ---
class SettingsApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.res = ResourceManager()

        self.all_portraits = self._scan(PORTRAITS_DIR)
        self.all_backs = self._scan(BACKS_DIR)
        self.player_portraits = (self.all_portraits[:4] + [""] * 4)[:4]
        self.current_back = self.all_backs[0] if self.all_backs else ""

        self.face_sets = self._scan_dirs(FACES_BASE_DIR)
        if not self.face_sets:
            os.makedirs(os.path.join(FACES_BASE_DIR, "set_1"), exist_ok=True)
            self.face_sets = ["set_1"]
        self.current_face_set = self.face_sets[0]
        self.current_joker = ""
        self.current_face_cards = []
        self._load_current_deck()

        # --- СОСТОЯНИЕ НАСТРОЕК ИГРЫ ---
        self.resolutions = ["1280x720", "1600x900", "1920x1080", "2560x1440"]
        self.res_idx = 1

        self.anim_speeds = ["Медленно", "Обычно", "Быстро", "Мгновенно"]
        self.anim_idx = 1

        self.difficulties = ["Новичок", "Любитель", "Профи", "Шулер"]
        self.diff_idx = 1

        self.matches = 5
        self.losses = 2

        self.volumes = {"master": 80, "music": 50, "sfx": 100}
        self.active_slider = None

        self.state = "MAIN"
        self.dropdown_open = False
        self.editing_idx = 0
        self.click_zones = []

    def apply_resolution(self):
        pass

    def apply_animation_speed(self):
        pass

    def update_match_rules(self):
        pass

    def apply_difficulty(self):
        pass

    def apply_volume(self, channel):
        pass

    def save_configuration(self):
        """
        =========================================================
        ИНСТРУКЦИЯ ПО СОЗДАНИЮ КОНФИГУРАЦИОННОГО ФАЙЛА JSON
        =========================================================

        При нажатии на кнопку "ПРИНЯТЬ" этот метод должен
        собирать все текущие параметры и сохранять их в файл.

        Пример реализации:
        ---------------------------------------------------------
        import json

        # 1. Собираем все данные в один Python словарь
        config_data = {
            "deck_settings": {
                "player_portraits": self.player_portraits,
                "card_back": self.current_back,
                "face_set": self.current_face_set
            },
            "video_settings": {
                "resolution": self.resolutions[self.res_idx],
                "animation_speed": self.anim_speeds[self.anim_idx]
            },
            "game_rules": {
                "total_matches": self.matches,
                "allowed_losses": self.losses,
                "difficulty": self.difficulties[self.diff_idx]
            },
            "audio_settings": {
                "master_volume": self.volumes["master"],
                "music_volume": self.volumes["music"],
                "sfx_volume": self.volumes["sfx"]
            }
        }

        # 2. Сохраняем в файл 'config.json' в корневой папке игры
        try:
            config_path = os.path.join(BASE_PATH, "config.json")
            with open(config_path, "w", encoding="utf-8") as f:
                # indent=4 делает json красивым и читаемым для человека
                # ensure_ascii=False позволяет сохранять кириллицу
                json.dump(config_data, f, indent=4, ensure_ascii=False)

            print("Настройки успешно сохранены в config.json!")

            # 3. Здесь можно добавить переход на следующий экран
            # (например, возврат в главное меню или запуск игры)

        except Exception as e:
            print(f"Ошибка при сохранении конфигурации: {e}")
        ---------------------------------------------------------
        """
        print("Кнопка 'ПРИНЯТЬ' нажата! Функция save_configuration вызвана.")
        # Раскомментируй код из инструкции выше, чтобы JSON начал сохраняться

    def _scan_dirs(self, path):
        """
        Сканирует директорию на наличие подпапок.
        Игнорирует пустые папки и папки без изображений.
        """
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            return []

        valid_dirs = []
        # Проходим по всем элементам в базовой директории (faces)
        for d in os.listdir(path):
            full_dir_path = os.path.join(path, d)

            # Если это папка (например, set_1)
            if os.path.isdir(full_dir_path):
                # Ищем внутри файлы с расширениями картинок
                images = [f for f in os.listdir(full_dir_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

                # Если список картинок не пустой — папка валидна, добавляем в меню
                if images:
                    valid_dirs.append(d)

        return valid_dirs

    def _scan(self, path):
        if not os.path.exists(path): os.makedirs(path, exist_ok=True); return []
        return [f for f in os.listdir(path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    def _load_current_deck(self):
        path = os.path.join(FACES_BASE_DIR, self.current_face_set)
        all_files = self._scan(path)
        jokers = [f for f in all_files if 'joker' in f.lower()]
        self.current_joker = jokers[0] if jokers else ""
        faces_no_joker = [f for f in all_files if 'joker' not in f.lower()]
        filtered = [f for f in faces_no_joker if f.lower().startswith(('a', 'j', 'q', 'k'))]

        suit_order = {"clubs": 0, "diamonds": 1, "spades": 2, "hearts": 3}
        rank_order = {"j": 0, "q": 1, "k": 2, "a": 3}

        def sort_key(name):
            name_l = name.lower()
            suit_val = 99
            for s, val in suit_order.items():
                if s in name_l: suit_val = val; break
            rank_val = 99
            if name_l.startswith('j'):
                rank_val = rank_order['j']
            elif name_l.startswith('q'):
                rank_val = rank_order['q']
            elif name_l.startswith('k'):
                rank_val = rank_order['k']
            elif name_l.startswith('a'):
                rank_val = rank_order['a']
            return (suit_val, rank_val, name_l)

        filtered.sort(key=sort_key)
        self.current_face_cards = filtered[:16] + [""] * (16 - len(filtered[:16]))

    def draw_text(self, text, pos, size=20, color=TEXT_COLOR, anchor="center"):
        font = pygame.font.SysFont("Arial", size, bold=True)
        surf = font.render(str(text), True, color)
        rect = surf.get_rect(**{anchor: pos})
        self.screen.blit(surf, rect)
        return rect

    def draw_selector(self, label, value_text, x, y, width, action_prev, action_next, mouse_pos):
        self.draw_text(label, (x, y), 16, TEXT_DIM, anchor="topleft")
        btn_w, btn_h = 30, 30
        val_w = width - (btn_w * 2) - 10
        l_rect = pygame.Rect(x, y + 25, btn_w, btn_h)
        l_hov = mouse_pos and l_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, HIGHLIGHT_COLOR if l_hov else FRAME_COLOR, l_rect, border_radius=6)
        self.draw_text("<", l_rect.center, 18, BG_COLOR if l_hov else TEXT_COLOR)
        self.click_zones.append((l_rect, action_prev))

        val_rect = pygame.Rect(l_rect.right + 5, y + 25, val_w, btn_h)
        pygame.draw.rect(self.screen, GRID_BASE_COLOR, val_rect, border_radius=6)
        pygame.draw.rect(self.screen, FRAME_COLOR, val_rect, 1, border_radius=6)
        self.draw_text(value_text, val_rect.center, 16, TEXT_COLOR)

        r_rect = pygame.Rect(val_rect.right + 5, y + 25, btn_w, btn_h)
        r_hov = mouse_pos and r_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, HIGHLIGHT_COLOR if r_hov else FRAME_COLOR, r_rect, border_radius=6)
        self.draw_text(">", r_rect.center, 18, BG_COLOR if r_hov else TEXT_COLOR)
        self.click_zones.append((r_rect, action_next))

    def draw_stepper(self, label, value, x, y, width, action_minus, action_plus, mouse_pos):
        self.draw_text(label, (x, y), 16, TEXT_DIM, anchor="topleft")
        btn_w, btn_h = 30, 30
        val_w = width - (btn_w * 2) - 10
        m_rect = pygame.Rect(x, y + 25, btn_w, btn_h)
        m_hov = mouse_pos and m_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, HIGHLIGHT_COLOR if m_hov else FRAME_COLOR, m_rect, border_radius=6)
        self.draw_text("-", m_rect.center, 22, BG_COLOR if m_hov else TEXT_COLOR)
        self.click_zones.append((m_rect, action_minus))

        val_rect = pygame.Rect(m_rect.right + 5, y + 25, val_w, btn_h)
        pygame.draw.rect(self.screen, GRID_BASE_COLOR, val_rect, border_radius=6)
        pygame.draw.rect(self.screen, FRAME_COLOR, val_rect, 1, border_radius=6)
        self.draw_text(str(value), val_rect.center, 18, TEXT_COLOR)

        p_rect = pygame.Rect(val_rect.right + 5, y + 25, btn_w, btn_h)
        p_hov = mouse_pos and p_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, HIGHLIGHT_COLOR if p_hov else FRAME_COLOR, p_rect, border_radius=6)
        self.draw_text("+", p_rect.center, 20, BG_COLOR if p_hov else TEXT_COLOR)
        self.click_zones.append((p_rect, action_plus))

    def draw_slider(self, label, value, x, y, width, action_key, mouse_pos):
        self.draw_text(label, (x, y), 16, TEXT_DIM, anchor="topleft")
        self.draw_text(f"{value}%", (x + width, y), 16, TEXT_COLOR, anchor="topright")
        track_rect = pygame.Rect(x, y + 30, width, 10)
        pygame.draw.rect(self.screen, GRID_BASE_COLOR, track_rect, border_radius=5)
        fill_w = int(width * (value / 100.0))
        fill_rect = pygame.Rect(x, y + 30, fill_w, 10)
        pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, fill_rect, border_radius=5)
        thumb_r = 10
        thumb_x = x + fill_w
        thumb_y = track_rect.centery
        thumb_rect = pygame.Rect(thumb_x - thumb_r, thumb_y - thumb_r, thumb_r * 2, thumb_r * 2)

        is_hovered = mouse_pos and (track_rect.collidepoint(mouse_pos) or thumb_rect.collidepoint(mouse_pos))
        is_active = self.active_slider == action_key
        color = HIGHLIGHT_HOVER if (is_hovered or is_active) else TEXT_COLOR
        pygame.draw.circle(self.screen, color, (thumb_x, thumb_y), thumb_r)
        hitbox = pygame.Rect(x, y + 15, width, 40)
        self.click_zones.append((hitbox, f"slider_{action_key}"))

    def render_main(self, mouse_pos):
        # Увеличил высоту главной панели до 840, чтобы влезла кнопка "Принять"
        root_w, root_h = 1024, 840
        root_x, root_y = (WIDTH - root_w) // 2, (HEIGHT - root_h) // 2
        root_rect = pygame.Rect(root_x, root_y, root_w, root_h)

        pygame.draw.rect(self.screen, MAIN_PANEL_COLOR, root_rect, border_radius=25)
        pygame.draw.rect(self.screen, FRAME_COLOR, root_rect, 3, border_radius=25)
        self.draw_text("НАСТРОЙКИ", (root_rect.centerx, root_rect.y + 35), 32)

        deck_w, deck_h = 960, 360
        deck_rect = pygame.Rect(root_x + 32, root_y + 80, deck_w, deck_h)
        pygame.draw.rect(self.screen, SUB_PANEL_COLOR, deck_rect, border_radius=20)

        inner_padding = 60
        grid_h = deck_h - inner_padding * 1.5
        grid_y = deck_rect.y + 70

        portrait_grid = DynamicSquareGrid(parent_height=grid_h, padding=10, spacing_ratio=0.32,
                                          aspect_ratio=RATIO_SQUARE)
        faces_grid = DynamicSquareGrid(parent_height=grid_h - 40, padding=10, spacing_ratio=0.1,
                                       aspect_ratio=RATIO_CARD)

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

        self.draw_text("Настройки колоды", (portrait_x + portrait_grid.S / 2, title_y), 22, anchor="midbottom")
        self.draw_text("Рубашка карт", (card_x + card_w / 2, title_y), 22, anchor="midbottom")
        self.draw_text("Колода", (faces_x + faces_grid.S / 2, title_y), 22, anchor="midbottom")
        self.draw_text("Просмотр", (preview_x + preview_w / 2, title_y), 22, anchor="midbottom")

        portrait_grid.calculate_and_draw(
            self.screen, portrait_x, grid_y, self.player_portraits, PORTRAITS_DIR, self.res, self.click_zones, "edit_p",
            labels=PLAYERS_NAMES, draw_text_fn=self.draw_text, mouse_pos=mouse_pos
        )

        card_h = portrait_grid.S
        card_y = grid_y
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
        is_card_hovered = mouse_pos and card_rect.collidepoint(mouse_pos)
        if is_card_hovered:
            scale = 1.05
            h_w, h_h = card_w * scale, card_h * scale
            draw_rect = pygame.Rect(card_x - (h_w - card_w) / 2, card_y - (h_h - card_h) / 2, h_w, h_h)
            img = self.res.get_img(BACKS_DIR, self.current_back, (int(h_w), int(h_h)))
            self.screen.blit(img, draw_rect)
            pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, draw_rect, 3, border_radius=10)
        else:
            pygame.draw.rect(self.screen, EMPTY_SLOT_COLOR, card_rect, border_radius=10)
            img = self.res.get_img(BACKS_DIR, self.current_back, (int(card_w), int(card_h)))
            self.screen.blit(img, card_rect)
            pygame.draw.rect(self.screen, FRAME_COLOR, card_rect, 1, border_radius=10)
        self.click_zones.append((card_rect, "edit_b_0"))

        faces_grid.calculate_and_draw(
            self.screen, faces_x, grid_y, self.current_face_cards,
            os.path.join(FACES_BASE_DIR, self.current_face_set),
            self.res, self.click_zones, "edit_f", mouse_pos=mouse_pos
        )

        btn_w = faces_grid.S
        btn_x = faces_x
        btn_h = 36
        btn_rect = pygame.Rect(btn_x, grid_y + faces_grid.S + 4, btn_w, btn_h)
        is_btn_hovered = mouse_pos and btn_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, GRID_BASE_COLOR, btn_rect, border_radius=10)
        pygame.draw.rect(self.screen, HIGHLIGHT_COLOR if is_btn_hovered else FRAME_COLOR, btn_rect, width=2,
                         border_radius=10)
        self.draw_text(f"Колода: {self.current_face_set}", btn_rect.center, 16, TEXT_COLOR)
        self.click_zones.append((btn_rect, "toggle_dropdown"))

        preview_y = grid_y
        preview_rect = pygame.Rect(preview_x, preview_y, preview_w, preview_h)
        active_preview_file = self.current_joker
        for i, f in enumerate(self.current_face_cards):
            if not f: continue
            for rect, action in self.click_zones:
                if action == f"edit_f_{i}" and mouse_pos and rect.collidepoint(mouse_pos):
                    active_preview_file = f
                    break

        pygame.draw.rect(self.screen, EMPTY_SLOT_COLOR, preview_rect, border_radius=10)
        if active_preview_file:
            img = self.res.get_img(os.path.join(FACES_BASE_DIR, self.current_face_set), active_preview_file,
                                   (int(preview_w), int(preview_h)))
            self.screen.blit(img, preview_rect)

        if active_preview_file != self.current_joker and active_preview_file != "":
            pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, preview_rect, 3, border_radius=10)
        else:
            pygame.draw.rect(self.screen, FRAME_COLOR, preview_rect, 1, border_radius=10)

        # ==========================================
        # НАСТРОЙКИ ИГРЫ
        # ==========================================
        game_rect = pygame.Rect(root_x + 32, deck_rect.bottom + 20, 960, 270)
        pygame.draw.rect(self.screen, SUB_PANEL_COLOR, game_rect, border_radius=20)

        self.draw_text("Настройки игры", (game_rect.centerx, game_rect.y + 20), 24, TEXT_COLOR)
        pygame.draw.line(self.screen, FRAME_COLOR, (game_rect.x + 40, game_rect.y + 40),
                         (game_rect.right - 40, game_rect.y + 40), 2)

        col_w = game_rect.width // 3
        pad_x = 40
        ui_w = col_w - pad_x * 2
        start_y = game_rect.y + 60
        y_step = 65

        # --- Колонка 1: Графика ---
        col1_x = game_rect.x + pad_x
        self.draw_text("Экран и Графика", (col1_x + ui_w / 2, start_y), 18, HIGHLIGHT_COLOR)

        self.draw_selector("Разрешение", self.resolutions[self.res_idx], col1_x, start_y + 25, ui_w, "res_prev",
                           "res_next", mouse_pos)
        self.draw_selector("Скорость анимаций", self.anim_speeds[self.anim_idx], col1_x, start_y + 25 + y_step, ui_w,
                           "anim_prev", "anim_next", mouse_pos)

        # --- Колонка 2: Правила ---
        col2_x = game_rect.x + col_w + pad_x
        self.draw_text("Условия игры", (col2_x + ui_w / 2, start_y), 18, HIGHLIGHT_COLOR)

        self.draw_stepper("Количество матчей", self.matches, col2_x, start_y + 25, ui_w, "match_minus", "match_plus",
                          mouse_pos)
        self.draw_stepper("Порог поражений", self.losses, col2_x, start_y + 25 + y_step, ui_w, "loss_minus",
                          "loss_plus", mouse_pos)
        self.draw_selector("Сложность ботов", self.difficulties[self.diff_idx], col2_x, start_y + 25 + y_step * 2 - 10,
                           ui_w, "diff_prev", "diff_next", mouse_pos)

        # --- Колонка 3: Звук ---
        col3_x = game_rect.x + col_w * 2 + pad_x
        self.draw_text("Аудио", (col3_x + ui_w / 2, start_y), 18, HIGHLIGHT_COLOR)

        self.draw_slider("Общая громкость", self.volumes["master"], col3_x, start_y + 25, ui_w, "master", mouse_pos)
        self.draw_slider("Музыка", self.volumes["music"], col3_x, start_y + 25 + 60, ui_w, "music", mouse_pos)
        self.draw_slider("Эффекты", self.volumes["sfx"], col3_x, start_y + 25 + 120, ui_w, "sfx", mouse_pos)

        # ==========================================
        # ГЛАВНАЯ КНОПКА ПРИНЯТЬ
        # ==========================================
        accept_w, accept_h = 240, 50
        # Размещаем по центру, под панелью настроек игры
        accept_rect = pygame.Rect(root_x + (root_w - accept_w) // 2, game_rect.bottom + 25, accept_w, accept_h)

        is_accept_hovered = mouse_pos and accept_rect.collidepoint(mouse_pos)
        btn_color = HIGHLIGHT_HOVER if is_accept_hovered else HIGHLIGHT_COLOR

        pygame.draw.rect(self.screen, btn_color, accept_rect, border_radius=15)
        # Рамка кнопки
        pygame.draw.rect(self.screen, TEXT_COLOR if is_accept_hovered else FRAME_COLOR, accept_rect, 2,
                         border_radius=15)

        # Текст на кнопке темный для контраста
        self.draw_text("ПРИНЯТЬ", accept_rect.center, 24, BG_COLOR)
        self.click_zones.append((accept_rect, "accept_config"))
        # ==========================================

        # Выпадающий список
        if self.dropdown_open:
            dd_y = btn_rect.bottom + 4
            dd_h = len(self.face_sets) * 36
            dd_rect = pygame.Rect(btn_rect.x, dd_y, btn_rect.width, dd_h)

            pygame.draw.rect(self.screen, MAIN_PANEL_COLOR, dd_rect, border_radius=10)
            pygame.draw.rect(self.screen, FRAME_COLOR, dd_rect, width=2, border_radius=10)

            for i, fset in enumerate(self.face_sets):
                item_rect = pygame.Rect(dd_rect.x, dd_rect.y + i * 36, dd_rect.width, 36)
                is_item_hovered = mouse_pos and item_rect.collidepoint(mouse_pos)
                if is_item_hovered:
                    pygame.draw.rect(self.screen, SUB_PANEL_COLOR, item_rect, border_radius=10)

                text_color = HIGHLIGHT_COLOR if fset == self.current_face_set else TEXT_COLOR
                self.draw_text(f"Колода: {fset}", item_rect.center, 16, text_color)
                self.click_zones.append((item_rect, f"select_fset_{i}"))

    def render_overlay(self, files, folder, title, prefix, aspect_ratio, mouse_pos, labels=None):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))

        modal_h = 500
        modal_grid = DynamicSquareGrid(parent_height=modal_h, padding=20, spacing_ratio=0.1, aspect_ratio=aspect_ratio)

        m_x = (WIDTH - modal_grid.S - 80) // 2
        m_y = (HEIGHT - modal_h - 120) // 2
        modal_bg = pygame.Rect(m_x, m_y, modal_grid.S + 80, modal_h + 120)

        pygame.draw.rect(self.screen, MAIN_PANEL_COLOR, modal_bg, border_radius=25)
        pygame.draw.rect(self.screen, FRAME_COLOR, modal_bg, 3, border_radius=25)
        self.draw_text(title, (modal_bg.centerx, modal_bg.y + 40), 32, color=TEXT_COLOR)

        modal_grid.calculate_and_draw(
            self.screen, m_x + 40, m_y + 90, files, folder, self.res, self.click_zones, prefix,
            mouse_pos=mouse_pos, labels=labels, draw_text_fn=self.draw_text if labels else None
        )

    def run(self):
        while True:
            self.screen.fill(BG_COLOR)
            self.click_zones = []

            mouse_pos = pygame.mouse.get_pos()

            if self.active_slider:
                for rect, action in self.click_zones:
                    if action == f"slider_{self.active_slider}":
                        rel_x = mouse_pos[0] - rect.x
                        percentage = int((rel_x / rect.width) * 100)
                        percentage = max(0, min(100, percentage))
                        self.volumes[self.active_slider] = percentage
                        self.apply_volume(self.active_slider)
                        break

            self.render_main(mouse_pos)

            if self.state == "SELECT_P":
                self.render_overlay(self.all_portraits, PORTRAITS_DIR, "ВЫБОР ПЕРСОНАЖА", "set_p", RATIO_SQUARE,
                                    mouse_pos)
            elif self.state == "SELECT_B":
                self.render_overlay(self.all_backs, BACKS_DIR, "ВЫБОР РУБАШКИ", "set_b", RATIO_CARD, mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()

                if event.type == pygame.MOUSEBUTTONUP:
                    self.active_slider = None

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            pygame.display.flip()
            self.clock.tick(FPS)

    def handle_click(self, pos):
        action = next((act for rect, act in self.click_zones if rect.collidepoint(pos)), None)

        if self.dropdown_open and action != "toggle_dropdown" and not (action and action.startswith("select_fset_")):
            self.dropdown_open = False

        if not action:
            if self.state != "MAIN": self.state = "MAIN"
            return

        if action == "accept_config":
            self.save_configuration()

        elif action.startswith("slider_"):
            self.active_slider = action.replace("slider_", "")

        elif action == "res_prev":
            self.res_idx = (self.res_idx - 1) % len(self.resolutions)
            self.apply_resolution()
        elif action == "res_next":
            self.res_idx = (self.res_idx + 1) % len(self.resolutions)
            self.apply_resolution()

        elif action == "anim_prev":
            self.anim_idx = (self.anim_idx - 1) % len(self.anim_speeds)
            self.apply_animation_speed()
        elif action == "anim_next":
            self.anim_idx = (self.anim_idx + 1) % len(self.anim_speeds)
            self.apply_animation_speed()

        elif action == "diff_prev":
            self.diff_idx = (self.diff_idx - 1) % len(self.difficulties)
            self.apply_difficulty()
        elif action == "diff_next":
            self.diff_idx = (self.diff_idx + 1) % len(self.difficulties)
            self.apply_difficulty()

        elif action == "match_minus":
            self.matches = max(1, self.matches - 1)
            if self.losses > self.matches:
                self.losses = self.matches
            self.update_match_rules()

        elif action == "match_plus":
            self.matches = min(99, self.matches + 1)
            self.update_match_rules()

        elif action == "loss_minus":
            self.losses = max(1, self.losses - 1)
            self.update_match_rules()

        elif action == "loss_plus":
            self.losses = min(self.matches, self.losses + 1)
            self.update_match_rules()

        elif action == "toggle_dropdown":
            self.dropdown_open = not self.dropdown_open
        elif action.startswith("select_fset_"):
            idx = int(action.split("_")[-1])
            self.current_face_set = self.face_sets[idx]
            self._load_current_deck()
            self.dropdown_open = False
        elif action.startswith("edit_p_"):
            self.editing_idx = int(action.split("_")[-1])
            self.state = "SELECT_P"
            self.dropdown_open = False
        elif action.startswith("edit_b_"):
            self.state = "SELECT_B"
            self.dropdown_open = False
        elif action.startswith("set_p_"):
            self.player_portraits[self.editing_idx] = self.all_portraits[int(action.split("_")[-1])]
            self.state = "MAIN"
        elif action.startswith("set_b_"):
            self.current_back = self.all_backs[int(action.split("_")[-1])]
            self.state = "MAIN"


if __name__ == "__main__":
    SettingsApp().run()