from __future__ import annotations

import copy
import html
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import pygame
import pygame_gui
from pygame_gui.elements import (
    UIButton,
    UIDropDownMenu,
    UILabel,
    UIPanel,
    UITextBox,
    UITextEntryLine,
)

UI_TEXT_ENTRY_FINISHED = getattr(pygame_gui, "UI_TEXT_ENTRY_FINISHED", None)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from durak_app.config import (  # noqa: E402
    BOT_CARD_HEIGHT,
    BOT_CARD_WIDTH,
    BOTTOM_ZONE_HEIGHT,
    BOTTOM_ZONE_TOP,
    CARD_HEIGHT,
    CARD_WIDTH,
    HEIGHT,
    SIDE_ZONE_TOP,
    TABLE_RECT,
    WIDTH,
)

THEME_PATH = PROJECT_ROOT / "ui_theme" / "layout_debug_tool_win95.json"
APP_CONFIG_PATH = PROJECT_ROOT / "app_config.json"

SUPPORTED_SCREEN_IDS = ("game_table", "main_menu", "modal_intro", "modal_endgame")
DEFAULT_SCREEN_ID = "game_table"
SCREEN_LABELS = {
    "game_table": "Игровой стол",
    "main_menu": "Главное меню",
    "modal_intro": "Стартовая модалка",
    "modal_endgame": "Финальная модалка",
}
SCREEN_IDS_BY_LABEL = {label: screen_id for screen_id, label in SCREEN_LABELS.items()}

WINDOW_SIZE = (1600, 940)
GAME_CANVAS_SIZE = (1600, 900)

CONTEXT_RECT = pygame.Rect(12, 8, 1576, 104)
NAVIGATOR_RECT = pygame.Rect(12, 122, 264, 540)
INSPECTOR_RECT = pygame.Rect(284, 122, 330, 540)
PREVIEW_RECT = pygame.Rect(622, 122, 966, 540)
TODO_RECT = pygame.Rect(12, 672, 1576, 232)
STATUS_RECT = pygame.Rect(4, WINDOW_SIZE[1] - 28, WINDOW_SIZE[0] - 8, 24)

INSPECTOR_CONTENT_X = 10
INSPECTOR_GROUP_X = 8
INSPECTOR_GROUP_WIDTH = 314
INSPECTOR_ACTION_Y = 506
INSPECTOR_GROUP_HEIGHT = 78
INSPECTOR_CONTROL_HEIGHT = 130

WIN95_FACE = pygame.Color(192, 192, 192)
WIN95_DARK = pygame.Color(128, 128, 128)
WIN95_DARKER = pygame.Color(64, 64, 64)
WIN95_LIGHT = pygame.Color(255, 255, 255)
PREVIEW_BG = pygame.Color(18, 70, 44)
PREVIEW_FELT = pygame.Color(24, 104, 62)
HOVER_COLOR = pygame.Color(255, 255, 170)
SELECTED_COLOR = pygame.Color(255, 210, 80)


def safe_int(value: object, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def safe_str(value: object, fallback: str = "") -> str:
    return value if isinstance(value, str) else fallback


@dataclass(frozen=True)
class LayoutObject:
    screen_id: str
    object_id: str
    path: str
    object_type: str
    x: int
    y: int
    width: int
    height: int
    delta_x: int
    delta_y: int
    width_delta: int
    height_delta: int
    color: str
    font: str
    font_size: int
    todo_text: str

    @classmethod
    def from_config_entry(cls, screen_id: str, object_id: str, entry: object) -> "LayoutObject":
        safe_entry = entry if isinstance(entry, dict) else {}
        return cls(
            screen_id=screen_id,
            object_id=object_id,
            path=f"{screen_id}.{object_id}",
            object_type=safe_str(safe_entry.get("type"), "block"),
            x=safe_int(safe_entry.get("x")),
            y=safe_int(safe_entry.get("y")),
            width=safe_int(safe_entry.get("width")),
            height=safe_int(safe_entry.get("height")),
            delta_x=safe_int(safe_entry.get("delta_x")),
            delta_y=safe_int(safe_entry.get("delta_y")),
            width_delta=safe_int(safe_entry.get("width_delta")),
            height_delta=safe_int(safe_entry.get("height_delta")),
            color=safe_str(safe_entry.get("color"), ""),
            font=safe_str(safe_entry.get("font"), ""),
            font_size=safe_int(safe_entry.get("font_size")),
            todo_text=safe_str(safe_entry.get("todo_text"), ""),
        )


class LayoutDataSource:
    def __init__(self, config_path: Path, screen_ids: tuple[str, ...]) -> None:
        self.config_path = config_path
        self.screen_ids = screen_ids
        self.data: dict = {}
        self.layout: dict[str, dict] = {}
        self.load_error: str | None = None

    def load(self) -> None:
        try:
            with self.config_path.open("r", encoding="utf-8") as config_file:
                raw_data = json.load(config_file)
        except (OSError, json.JSONDecodeError) as exc:
            self.data = {}
            self.layout = {}
            self.load_error = f"{type(exc).__name__}: {exc}"
            return

        raw_layout = raw_data.get("layout", {})
        if not isinstance(raw_layout, dict):
            raw_layout = {}

        self.data = raw_data
        self.layout = {}
        for screen_id in self.screen_ids:
            screen_layout = raw_layout.get(screen_id, {})
            self.layout[screen_id] = screen_layout if isinstance(screen_layout, dict) else {}
        self.load_error = None

    def screen_ids_found(self) -> list[str]:
        return [
            screen_id
            for screen_id in self.screen_ids
            if self.layout_for_screen(screen_id)
        ]

    def layout_for_screen(self, screen_id: str) -> dict:
        screen_layout = self.layout.get(screen_id, {})
        return screen_layout if isinstance(screen_layout, dict) else {}

    def object_count(self, screen_id: str) -> int:
        return len(self.layout_for_screen(screen_id))

    def total_object_count(self) -> int:
        return sum(self.object_count(screen_id) for screen_id in self.screen_ids)

    def objects_for_screen(self, screen_id: str) -> list[LayoutObject]:
        objects: list[LayoutObject] = []
        for object_id, entry in self.layout_for_screen(screen_id).items():
            objects.append(LayoutObject.from_config_entry(screen_id, str(object_id), entry))
        objects.sort(key=lambda item: (item.object_type, item.object_id))
        return objects

    def summary_text(self) -> str:
        if self.load_error:
            return f"Layout load ERROR: {self.load_error}"

        counts = ", ".join(
            f"{screen_id}={self.object_count(screen_id)}"
            for screen_id in self.screen_ids
        )
        return (
            f"Layout loaded: {len(self.screen_ids_found())}/{len(self.screen_ids)} screens, "
            f"{self.total_object_count()} objects ({counts})"
        )


def draw_sunken_rect(surface: pygame.Surface, rect: pygame.Rect, fill: pygame.Color) -> None:
    pygame.draw.rect(surface, fill, rect)
    pygame.draw.line(surface, WIN95_DARKER, rect.topleft, rect.topright)
    pygame.draw.line(surface, WIN95_DARKER, rect.topleft, rect.bottomleft)
    pygame.draw.line(surface, WIN95_LIGHT, rect.bottomleft, rect.bottomright)
    pygame.draw.line(surface, WIN95_LIGHT, rect.topright, rect.bottomright)


class LayoutDebugToolV2Shell:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Layout Debug Tool v2 Shell")
        self.window = pygame.display.set_mode(WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        self.manager = pygame_gui.UIManager(WINDOW_SIZE, str(THEME_PATH))

        self.font = pygame.font.SysFont("consolas", 16)
        self.small_font = pygame.font.SysFont("consolas", 14)
        self.running = True
        self.selected_filter_types = {"visible", "panel", "button"}
        self.show_hitboxes = False
        self.hover_object = "game_table.players.left.panel"
        self.selected_object = "game_table.players.left.name"
        self.layout_data = LayoutDataSource(APP_CONFIG_PATH, SUPPORTED_SCREEN_IDS)
        self.layout_data.load()
        self.initial_layout = copy.deepcopy(self.layout_data.layout)
        self.session_dirty = False
        self.current_screen_id = DEFAULT_SCREEN_ID
        self.layout_objects = self.layout_data.objects_for_screen(self.current_screen_id)
        self.selected_layout_object_id = self.layout_objects[0].object_id if self.layout_objects else None
        self.hover_layout_object_id: str | None = None
        self.preview_rects = self._build_preview_rects()
        self.layout_summary = self._layout_status_text()
        self.control_buttons: dict[UIButton, tuple[int, int, int, int]] = {}
        self.step_field: UITextEntryLine | None = None
        self.selected_object_snapshot: dict | None = self._copy_selected_layout_entry()

        self._build_ui()

    def _layout_status_text(self) -> str:
        hover = self.hover_layout_object_id or "-"
        selected = self.selected_layout_object_id or "-"
        session = "UNSAVED" if self.session_dirty else "saved"
        return (
            f"{self.layout_data.summary_text()} | "
            f"model: {self.current_screen_id}={len(self.layout_objects)} objects | "
            f"session: {session} | hover: {hover} | selected: {selected}"
        )

    def _update_session_status(self) -> None:
        self.session_dirty = self.layout_data.layout != self.initial_layout
        self.layout_summary = self._layout_status_text()
        if hasattr(self, "status_label"):
            status_text = "Статус: UNSAVED" if self.session_dirty else "Статус: saved"
            self.status_label.set_text(status_text)
        if hasattr(self, "status_bar_label"):
            self.status_bar_label.set_text(self.layout_summary)

    def set_current_screen(self, screen_id: str) -> None:
        if screen_id not in SUPPORTED_SCREEN_IDS:
            return
        self.current_screen_id = screen_id
        self.layout_objects = self.layout_data.objects_for_screen(self.current_screen_id)
        self.selected_layout_object_id = self.layout_objects[0].object_id if self.layout_objects else None
        self.hover_layout_object_id = None
        self.selected_object_snapshot = self._copy_selected_layout_entry()
        self.preview_rects = self._build_preview_rects()
        self.navigator_body.set_text(self._navigator_html())
        self._update_inspector()
        self._update_session_status()

    def _navigator_html(self) -> str:
        if not self.layout_objects:
            return (
                "<font face=consolas size=3>"
                f"<b>{html.escape(self.current_screen_id)}</b><br><br>"
                "Нет layout-объектов."
                "</font>"
            )

        lines = [
            "<font face=consolas size=3>",
            f"<b>{html.escape(self.current_screen_id)}</b>",
            f"{len(self.layout_objects)} objects",
            f"Selected: {html.escape(self.selected_layout_object_id or '-')}",
            f"Hover: {html.escape(self.hover_layout_object_id or '-')}",
            "",
        ]
        current_type: str | None = None
        for layout_object in self.layout_objects:
            if layout_object.object_type != current_type:
                current_type = layout_object.object_type
                lines.append(f"<b>{html.escape(current_type)}</b>")

            selected_mark = " SELECTED" if layout_object.object_id == self.selected_layout_object_id else ""
            hover_mark = " HOVER" if layout_object.object_id == self.hover_layout_object_id else ""
            todo_mark = " TODO" if layout_object.todo_text else ""
            delta_text = (
                f"dx:{layout_object.delta_x} dy:{layout_object.delta_y} "
                f"dw:{layout_object.width_delta} dh:{layout_object.height_delta}"
            )
            object_line = html.escape(f"  |- {layout_object.object_id}{selected_mark}{hover_mark}{todo_mark}")
            delta_line = html.escape(f"     {delta_text}")
            lines.append(object_line)
            lines.append(delta_line)
            lines.append("")

        lines.append("</font>")
        return "<br>".join(lines)

    def _layout_object_by_id(self, object_id: str) -> LayoutObject | None:
        for layout_object in self.layout_objects:
            if layout_object.object_id == object_id:
                return layout_object
        return None

    def _selected_layout_object(self) -> LayoutObject | None:
        if self.selected_layout_object_id is None:
            return None
        return self._layout_object_by_id(self.selected_layout_object_id)

    def _selected_preview_rect(self) -> pygame.Rect:
        if self.selected_layout_object_id is None:
            return pygame.Rect(0, 0, 0, 0)
        return self.preview_rects.get(self.selected_layout_object_id, pygame.Rect(0, 0, 0, 0))

    def _selected_layout_entry(self) -> dict | None:
        if self.selected_layout_object_id is None:
            return None
        screen_layout = self.layout_data.layout.get(self.current_screen_id, {})
        if not isinstance(screen_layout, dict):
            return None
        entry = screen_layout.get(self.selected_layout_object_id)
        return entry if isinstance(entry, dict) else None

    def _copy_selected_layout_entry(self) -> dict | None:
        entry = self._selected_layout_entry()
        return copy.deepcopy(entry) if entry is not None else None

    def _dismiss_selected_object_changes(self) -> None:
        self.selected_object_snapshot = self._copy_selected_layout_entry()
        self._update_session_status()

    def _cancel_selected_object_changes(self) -> None:
        entry = self._selected_layout_entry()
        if entry is None or self.selected_object_snapshot is None:
            return
        entry.clear()
        entry.update(copy.deepcopy(self.selected_object_snapshot))
        self._refresh_layout_session_view()

    def _refresh_layout_session_view(self) -> None:
        self.layout_objects = self.layout_data.objects_for_screen(self.current_screen_id)
        if self.selected_layout_object_id and self._layout_object_by_id(self.selected_layout_object_id) is None:
            self.selected_layout_object_id = self.layout_objects[0].object_id if self.layout_objects else None
        self.preview_rects = self._build_preview_rects()
        self.navigator_body.set_text(self._navigator_html())
        self._update_inspector()
        self._update_session_status()

    def _apply_inspector_field_change(self, field_name: str, text: str) -> None:
        entry = self._selected_layout_entry()
        if entry is None:
            return

        rect = self._selected_preview_rect()
        if field_name == "x":
            entry["delta_x"] = safe_int(entry.get("delta_x")) + safe_int(text, rect.x) - rect.x
        elif field_name == "y":
            entry["delta_y"] = safe_int(entry.get("delta_y")) + safe_int(text, rect.y) - rect.y
        elif field_name == "width":
            entry["width_delta"] = safe_int(entry.get("width_delta")) + safe_int(text, rect.width) - rect.width
        elif field_name == "height":
            entry["height_delta"] = safe_int(entry.get("height_delta")) + safe_int(text, rect.height) - rect.height
        elif field_name in {"delta_x", "delta_y", "width_delta", "height_delta", "font_size"}:
            entry[field_name] = safe_int(text)
        elif field_name in {"color", "font"}:
            entry[field_name] = text.strip()
        else:
            return

        self._refresh_layout_session_view()

    def _current_step(self) -> int:
        if self.step_field is None:
            return 10
        return max(1, safe_int(self.step_field.get_text(), 10))

    def _nudge_selected_object(self, dx: int = 0, dy: int = 0, dw: int = 0, dh: int = 0) -> None:
        entry = self._selected_layout_entry()
        if entry is None:
            return
        if dx:
            entry["delta_x"] = safe_int(entry.get("delta_x")) + dx
        if dy:
            entry["delta_y"] = safe_int(entry.get("delta_y")) + dy
        if dw:
            entry["width_delta"] = safe_int(entry.get("width_delta")) + dw
        if dh:
            entry["height_delta"] = safe_int(entry.get("height_delta")) + dh
        self._refresh_layout_session_view()

    def _layout_rect(self, object_id: str, rect: pygame.Rect) -> pygame.Rect:
        layout_object = self._layout_object_by_id(object_id)
        moved = rect.copy()
        if layout_object is None:
            return moved
        moved.x += layout_object.delta_x
        moved.y += layout_object.delta_y
        moved.width = max(12, moved.width + layout_object.width_delta)
        moved.height = max(12, moved.height + layout_object.height_delta)
        return moved

    def _build_preview_rects(self) -> dict[str, pygame.Rect]:
        if self.current_screen_id == "game_table":
            return self._game_table_preview_rects()
        if self.current_screen_id == "main_menu":
            return self._main_menu_preview_rects()
        if self.current_screen_id == "modal_intro":
            return self._modal_intro_preview_rects()
        if self.current_screen_id == "modal_endgame":
            return self._modal_endgame_preview_rects()
        return {}

    def _game_table_preview_rects(self) -> dict[str, pygame.Rect]:
        table_rect = self._layout_rect("table_area", TABLE_RECT)
        left_rect = self._layout_rect("player_left_panel", pygame.Rect(32, SIDE_ZONE_TOP, 170, 620))
        top_rect = self._layout_rect("player_top_panel", pygame.Rect(WIDTH // 2 - 420, 20, 800, 160))
        right_rect = self._layout_rect("player_right_panel", pygame.Rect(WIDTH - 202, SIDE_ZONE_TOP, 170, 620))
        bottom_rect = self._layout_rect(
            "player_bottom_panel",
            pygame.Rect(WIDTH // 2 - 546, BOTTOM_ZONE_TOP + 82, 1092, BOTTOM_ZONE_HEIGHT - 96),
        )
        deck_rect = self._layout_rect("deck_panel", pygame.Rect(TABLE_RECT.right - CARD_WIDTH - 80, 190, CARD_WIDTH, CARD_HEIGHT))
        trump_rect = self._layout_rect("trump_panel", pygame.Rect(deck_rect.x, deck_rect.y + 40, CARD_HEIGHT, CARD_WIDTH))

        panel_width = 170
        panel_height = 300
        gap_width = deck_rect.x - table_rect.right - panel_width
        panel_x = table_rect.right + max(0, gap_width // 2)
        actions_rect = self._layout_rect("actions_panel", pygame.Rect(panel_x, deck_rect.y, panel_width, panel_height))
        table_cards_rect = self._layout_rect("table_cards_area", pygame.Rect(WIDTH // 2 - 500, 190, 560, 310))

        left_hand_rect = self._layout_rect(
            "left_hand_area",
            pygame.Rect(left_rect.x + 12, left_rect.y + 224, BOT_CARD_WIDTH + 52, 9 * 25 + BOT_CARD_HEIGHT),
        )
        top_hand_rect = self._layout_rect("top_hand_area", pygame.Rect(top_rect.x + 250, top_rect.y + 20, 260, 118))
        right_hand_rect = self._layout_rect(
            "right_hand_area",
            pygame.Rect(right_rect.x + 12, right_rect.y + 224, BOT_CARD_WIDTH + 52, 9 * 25 + BOT_CARD_HEIGHT),
        )
        bottom_hand_rect = self._layout_rect(
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

    def _main_menu_preview_rects(self) -> dict[str, pygame.Rect]:
        root_w, root_h = 1024, 840
        root_x, root_y = (WIDTH - root_w) // 2, (HEIGHT - root_h) // 2
        root_rect = self._layout_rect("menu_root", pygame.Rect(root_x, root_y, root_w, root_h))
        deck_rect = self._layout_rect("deck_panel", pygame.Rect(root_rect.x + 32, root_rect.y + 80, 960, 360))
        game_rect = self._layout_rect("game_settings_panel", pygame.Rect(root_rect.x + 32, deck_rect.bottom + 20, 960, 270))
        start_rect = self._layout_rect("start_button", pygame.Rect(root_rect.x + (root_rect.width - 240) // 2, game_rect.bottom + 25, 240, 50))
        exit_rect = self._layout_rect("exit_button", pygame.Rect(start_rect.right + 20, start_rect.y, 180, 50))
        return {
            "menu_root": root_rect,
            "deck_panel": deck_rect,
            "game_settings_panel": game_rect,
            "start_button": start_rect,
            "exit_button": exit_rect,
        }

    def _modal_intro_preview_rects(self) -> dict[str, pygame.Rect]:
        panel_rect = self._layout_rect("panel", pygame.Rect(WIDTH // 2 - 290, HEIGHT // 2 - 190, 580, 380))
        return {
            "overlay": self._layout_rect("overlay", pygame.Rect(0, 0, WIDTH, HEIGHT)),
            "panel": panel_rect,
            "title": self._layout_rect("title", pygame.Rect(panel_rect.x + 34, panel_rect.y + 24, 500, 40)),
            "trump_label": self._layout_rect("trump_label", pygame.Rect(panel_rect.x + 36, panel_rect.y + 82, 500, 24)),
            "tips_section": self._layout_rect("tips_section", pygame.Rect(panel_rect.x + 36, panel_rect.y + 184, 200, 28)),
            "continue_button": self._layout_rect("continue_button", pygame.Rect(panel_rect.x + (panel_rect.width - 140) // 2, panel_rect.y + panel_rect.height - 70, 140, 42)),
        }

    def _modal_endgame_preview_rects(self) -> dict[str, pygame.Rect]:
        panel_rect = self._layout_rect("panel", pygame.Rect(WIDTH // 2 - 330, HEIGHT // 2 - 250, 660, 500))
        return {
            "overlay": self._layout_rect("overlay", pygame.Rect(0, 0, WIDTH, HEIGHT)),
            "panel": panel_rect,
            "title": self._layout_rect("title", pygame.Rect(panel_rect.x + 34, panel_rect.y + 24, 560, 42)),
            "loser_name": self._layout_rect("loser_name", pygame.Rect(panel_rect.x + 36, panel_rect.y + 132, 320, 30)),
            "score_panel": self._layout_rect("score_panel", pygame.Rect(panel_rect.x + 36, panel_rect.y + 258, panel_rect.width - 72, 134)),
            "continue_button": self._layout_rect("continue_button", pygame.Rect(panel_rect.x + panel_rect.width // 2 - 220, panel_rect.y + panel_rect.height - 72, 180, 42)),
            "end_button": self._layout_rect("end_button", pygame.Rect(panel_rect.x + panel_rect.width // 2 + 40, panel_rect.y + panel_rect.height - 72, 180, 42)),
        }

    def _build_ui(self) -> None:
        self.context_panel = UIPanel(
            relative_rect=CONTEXT_RECT,
            manager=self.manager,
            object_id="#win95_panel",
        )
        self._section_title(self.context_panel, "ПАНЕЛЬ КОНТЕКСТА", CONTEXT_RECT.width - 2)
        self.screen_label = UILabel(
            relative_rect=pygame.Rect(12, 34, 58, 24),
            text="Экран:",
            manager=self.manager,
            container=self.context_panel,
            object_id="#win95_label",
        )
        self.screen_dropdown = UIDropDownMenu(
            options_list=[SCREEN_LABELS[screen_id] for screen_id in SUPPORTED_SCREEN_IDS],
            starting_option=SCREEN_LABELS[self.current_screen_id],
            relative_rect=pygame.Rect(CONTEXT_RECT.x + 72, CONTEXT_RECT.y + 32, 220, 28),
            manager=self.manager,
        )
        self.status_label = UILabel(
            relative_rect=pygame.Rect(312, 34, 210, 24),
            text="Статус: saved",
            manager=self.manager,
            container=self.context_panel,
            object_id="#win95_label",
        )
        self.apply_button = UIButton(
            relative_rect=pygame.Rect(1198, 32, 108, 28),
            text="Apply",
            manager=self.manager,
            container=self.context_panel,
            object_id="#win95_button",
        )
        self.reset_button = UIButton(
            relative_rect=pygame.Rect(1316, 32, 138, 28),
            text="Reset session",
            manager=self.manager,
            container=self.context_panel,
            object_id="#win95_button",
        )
        self.help_button = UIButton(
            relative_rect=pygame.Rect(1464, 32, 92, 28),
            text="Help",
            manager=self.manager,
            container=self.context_panel,
            object_id="#win95_button",
        )
        self.filter_buttons: dict[str, UIButton] = {}
        x = 12
        for filter_id, label in [
            ("visible", "visible"),
            ("panel", "panel"),
            ("button", "button"),
            ("helper", "helper"),
            ("changed", "changed"),
        ]:
            button = UIButton(
                relative_rect=pygame.Rect(x, 68, 112, 24),
                text=self._filter_text(filter_id, label),
                manager=self.manager,
                container=self.context_panel,
                object_id="#win95_button",
            )
            self.filter_buttons[filter_id] = button
            x += 120
        self.preview_mode = UILabel(
            relative_rect=pygame.Rect(748, 70, 230, 22),
            text="Режим preview: Hover select",
            manager=self.manager,
            container=self.context_panel,
            object_id="#win95_label",
        )
        self.hitboxes_button = UIButton(
            relative_rect=pygame.Rect(990, 66, 160, 28),
            text="[ ] Show hitboxes",
            manager=self.manager,
            container=self.context_panel,
            object_id="#win95_button",
        )

        self.navigator_panel = UIPanel(
            relative_rect=NAVIGATOR_RECT,
            manager=self.manager,
            object_id="#win95_panel",
        )
        self._section_title(self.navigator_panel, "НАВИГАТОР ОБЪЕКТОВ", NAVIGATOR_RECT.width - 2)
        self.navigator_body = UITextBox(
            html_text=self._navigator_html(),
            relative_rect=pygame.Rect(10, 34, NAVIGATOR_RECT.width - 42, NAVIGATOR_RECT.height - 66),
            manager=self.manager,
            container=self.navigator_panel,
            object_id="#win95_textbox",
        )

        self.inspector_panel = UIPanel(
            relative_rect=INSPECTOR_RECT,
            manager=self.manager,
            object_id="#win95_panel",
        )
        self._section_title(self.inspector_panel, "ИНСПЕКТОР", INSPECTOR_RECT.width - 2)
        self._build_inspector()

        self.preview_panel = UIPanel(
            relative_rect=PREVIEW_RECT,
            manager=self.manager,
            object_id="#win95_panel",
        )
        self._section_title(self.preview_panel, "PREVIEW AREA", PREVIEW_RECT.width - 2)

        self.todo_panel = UIPanel(
            relative_rect=TODO_RECT,
            manager=self.manager,
            object_id="#win95_panel",
        )
        self._section_title(self.todo_panel, "TO DO", TODO_RECT.width - 2)
        self._build_todo()

        self.status_bar = UIPanel(
            relative_rect=STATUS_RECT,
            manager=self.manager,
            object_id="#win95_panel",
        )
        self.status_bar_label = UILabel(
            relative_rect=pygame.Rect(8, 2, WINDOW_SIZE[0] - 32, 20),
            text=self.layout_summary,
            manager=self.manager,
            container=self.status_bar,
            object_id="#win95_label",
        )

    def _section_title(self, container: UIPanel, text: str, width: int) -> None:
        title_panel = UIPanel(
            relative_rect=pygame.Rect(1, 1, width, 22),
            manager=self.manager,
            container=container,
            object_id="#win95_section_title",
        )
        UILabel(
            relative_rect=pygame.Rect(8, 1, width - 16, 18),
            text=text,
            manager=self.manager,
            container=title_panel,
            object_id="#win95_title_label",
        )

    def _build_inspector(self) -> None:
        self.inspector_object_label = UILabel(
            pygame.Rect(INSPECTOR_CONTENT_X, 34, 300, 22),
            "Object:",
            self.manager,
            container=self.inspector_panel,
            object_id="#win95_object_label",
        )
        self.inspector_type_label = UILabel(
            pygame.Rect(INSPECTOR_CONTENT_X, 60, 300, 22),
            "Type:",
            self.manager,
            container=self.inspector_panel,
            object_id="#win95_object_label",
        )
        self.inspector_fields: dict[str, UITextEntryLine] = {}
        self.inspector_field_names_by_element: dict[UITextEntryLine, str] = {}
        self._inspector_group(
            "GEOMETRY",
            96,
            INSPECTOR_GROUP_HEIGHT,
            [("x", "0"), ("y", "0"), ("width", "0"), ("height", "0")],
        )
        self._inspector_group(
            "LAYOUT DELTAS",
            184,
            INSPECTOR_GROUP_HEIGHT,
            [("delta_x", "0"), ("delta_y", "0"), ("width_delta", "0"), ("height_delta", "0")],
        )
        self._inspector_group(
            "VISUAL",
            272,
            INSPECTOR_GROUP_HEIGHT,
            [("color", "#c0c0c0"), ("font", "Arial"), ("font_size", "14")],
        )
        self._build_inspector_controls(360)
        self._update_inspector()

        self.dismiss_button = UIButton(
            pygame.Rect(10, INSPECTOR_ACTION_Y, 94, 24),
            "Dismiss",
            self.manager,
            container=self.inspector_panel,
            object_id="#win95_button",
        )
        self.cancel_button = UIButton(
            pygame.Rect(114, INSPECTOR_ACTION_Y, 86, 24),
            "Cancel",
            self.manager,
            container=self.inspector_panel,
            object_id="#win95_button",
        )
        UIButton(
            pygame.Rect(210, INSPECTOR_ACTION_Y, 106, 24),
            "Copy id",
            self.manager,
            container=self.inspector_panel,
            object_id="#win95_button",
        )

    def _inspector_group(self, title: str, y: int, height: int, fields: list[tuple[str, str]]) -> None:
        panel = UIPanel(
            relative_rect=pygame.Rect(INSPECTOR_GROUP_X, y, INSPECTOR_GROUP_WIDTH, height),
            manager=self.manager,
            container=self.inspector_panel,
            object_id="#win95_sunken_panel",
        )
        UILabel(
            pygame.Rect(8, 6, 140, 16),
            title,
            self.manager,
            container=panel,
            object_id="#win95_label",
        )
        row_y = 28
        for idx, (label, value) in enumerate(fields):
            px = 8 + (idx % 2) * 150
            py = row_y + (idx // 2) * 20
            label_width = 86 if len(label) > 6 else 50
            input_x = px + label_width
            input_w = 136 - label_width
            UILabel(
                pygame.Rect(px, py, label_width - 4, 16),
                f"{label}:",
                self.manager,
                container=panel,
                object_id="#win95_small_label",
            )
            entry = UITextEntryLine(
                relative_rect=pygame.Rect(input_x, py, input_w, 16),
                manager=self.manager,
                container=panel,
                initial_text=value,
                object_id="#win95_input",
            )
            self.inspector_fields[label] = entry
            self.inspector_field_names_by_element[entry] = label

    def _update_inspector(self) -> None:
        if not hasattr(self, "inspector_fields"):
            return
        layout_object = self._selected_layout_object()
        rect = self._selected_preview_rect()

        if layout_object is None:
            self.inspector_object_label.set_text("Object: -")
            self.inspector_type_label.set_text("Type: -")
            values = {
                "x": "0",
                "y": "0",
                "width": "0",
                "height": "0",
                "delta_x": "0",
                "delta_y": "0",
                "width_delta": "0",
                "height_delta": "0",
                "color": "",
                "font": "",
                "font_size": "0",
            }
        else:
            self.inspector_object_label.set_text(f"Object: {layout_object.object_id}")
            self.inspector_type_label.set_text(f"Type: {layout_object.object_type}")
            values = {
                "x": str(rect.x),
                "y": str(rect.y),
                "width": str(rect.width),
                "height": str(rect.height),
                "delta_x": str(layout_object.delta_x),
                "delta_y": str(layout_object.delta_y),
                "width_delta": str(layout_object.width_delta),
                "height_delta": str(layout_object.height_delta),
                "color": layout_object.color or "#c0c0c0",
                "font": layout_object.font or "Arial",
                "font_size": str(layout_object.font_size or 14),
            }

        for field_name, value in values.items():
            field = self.inspector_fields.get(field_name)
            if field is not None:
                field.set_text(value)

    def _build_inspector_controls(self, y: int) -> None:
        panel = UIPanel(
            relative_rect=pygame.Rect(INSPECTOR_GROUP_X, y, INSPECTOR_GROUP_WIDTH, INSPECTOR_CONTROL_HEIGHT),
            manager=self.manager,
            container=self.inspector_panel,
            object_id="#win95_sunken_panel",
        )
        UILabel(pygame.Rect(8, 8, 120, 16), "CONTROL", self.manager, container=panel, object_id="#win95_label")
        UILabel(pygame.Rect(8, 32, 42, 16), "Step:", self.manager, container=panel, object_id="#win95_label")
        self.step_field = UITextEntryLine(
            relative_rect=pygame.Rect(56, 30, 58, 20),
            manager=self.manager,
            container=panel,
            initial_text="10",
            object_id="#win95_input",
        )

        UILabel(pygame.Rect(8, 62, 50, 16), "Move:", self.manager, container=panel, object_id="#win95_label")
        for idx, (text, delta) in enumerate([("<-", (-1, 0, 0, 0)), ("^", (0, -1, 0, 0)), ("v", (0, 1, 0, 0)), ("->", (1, 0, 0, 0))]):
            button = UIButton(pygame.Rect(62 + idx * 42, 58, 36, 24), text, self.manager, container=panel, object_id="#win95_button")
            self.control_buttons[button] = delta

        UILabel(pygame.Rect(8, 96, 42, 16), "Size:", self.manager, container=panel, object_id="#win95_label")
        for idx, (text, delta) in enumerate([("-W", (0, 0, -1, 0)), ("+W", (0, 0, 1, 0)), ("-H", (0, 0, 0, -1)), ("+H", (0, 0, 0, 1))]):
            button = UIButton(pygame.Rect(62 + idx * 42, 92, 36, 24), text, self.manager, container=panel, object_id="#win95_button")
            self.control_buttons[button] = delta

    def _build_todo(self) -> None:
        existing_panel = UIPanel(
            relative_rect=pygame.Rect(8, 34, 760, 188),
            manager=self.manager,
            container=self.todo_panel,
            object_id="#win95_sunken_panel",
        )
        new_panel = UIPanel(
            relative_rect=pygame.Rect(778, 34, 790, 188),
            manager=self.manager,
            container=self.todo_panel,
            object_id="#win95_sunken_panel",
        )

        UILabel(
            pygame.Rect(8, 12, 300, 18),
            "ПРОСМОТР СОЗДАННЫХ ЗАДАЧ",
            self.manager,
            container=existing_panel,
            object_id="#win95_label",
        )
        self.todo_list = UITextBox(
            html_text=(
                "<font face=consolas size=3>"
                "[ ] game_table.player_left_panel<br>"
                "&nbsp;&nbsp;&nbsp;&nbsp;Поднять выше<br><br>"
                "[!] game_ui.pass_button<br>"
                "&nbsp;&nbsp;&nbsp;&nbsp;Сдвинуть ближе к Take<br><br>"
                "[ ] modal_intro.panel<br>"
                "&nbsp;&nbsp;&nbsp;&nbsp;Уменьшить ширину"
                "</font>"
            ),
            relative_rect=pygame.Rect(8, 36, 286, 116),
            manager=self.manager,
            container=existing_panel,
            object_id="#win95_textbox",
        )
        UILabel(
            pygame.Rect(330, 12, 386, 18),
            "ВЫБРАННАЯ ЗАДАЧА",
            self.manager,
            container=existing_panel,
            object_id="#win95_label",
        )
        self.todo_text = UITextBox(
            html_text="Поднять панель выше и выровнять относительно верхней панели игрока.",
            relative_rect=pygame.Rect(330, 36, 386, 116),
            manager=self.manager,
            container=existing_panel,
            object_id="#win95_textbox",
        )
        for idx, text in enumerate(["Edit", "Copy"]):
            UIButton(
                pygame.Rect(407 + idx * 124, 160, 112, 22),
                text,
                self.manager,
                container=existing_panel,
                object_id="#win95_button",
            )

        UILabel(
            pygame.Rect(8, 12, 360, 18),
            "СОЗДАТЬ НОВУЮ ЗАДАЧУ",
            self.manager,
            container=new_panel,
            object_id="#win95_label",
        )
        UITextBox(
            html_text="Описание новой задачи для выбранного объекта.",
            relative_rect=pygame.Rect(8, 36, 600, 138),
            manager=self.manager,
            container=new_panel,
            object_id="#win95_textbox",
        )
        UIButton(
            pygame.Rect(628, 68, 128, 30),
            "Add task",
            self.manager,
            container=new_panel,
            object_id="#win95_button",
        )
        UIButton(
            pygame.Rect(628, 112, 128, 30),
            "Clean",
            self.manager,
            container=new_panel,
            object_id="#win95_button",
        )

    def _filter_text(self, filter_id: str, label: str) -> str:
        mark = "x" if filter_id in self.selected_filter_types else " "
        return f"[{mark}] {label}"

    def _layout_preview_viewport(self) -> pygame.Rect:
        panel_rect = self.preview_panel.get_abs_rect().inflate(-24, -56)
        panel_rect.y += 22
        ratio = GAME_CANVAS_SIZE[0] / GAME_CANVAS_SIZE[1]
        if panel_rect.width / panel_rect.height > ratio:
            height = panel_rect.height
            width = int(height * ratio)
        else:
            width = panel_rect.width
            height = int(width / ratio)
        return pygame.Rect(
            panel_rect.x + (panel_rect.width - width) // 2,
            panel_rect.y + (panel_rect.height - height) // 2,
            width,
            height,
        )

    def _canvas_to_viewport_rect(self, rect: pygame.Rect, viewport: pygame.Rect) -> pygame.Rect:
        scale_x = viewport.width / GAME_CANVAS_SIZE[0]
        scale_y = viewport.height / GAME_CANVAS_SIZE[1]
        return pygame.Rect(
            viewport.x + int(rect.x * scale_x),
            viewport.y + int(rect.y * scale_y),
            max(1, int(rect.width * scale_x)),
            max(1, int(rect.height * scale_y)),
        )

    def _viewport_to_canvas_pos(self, pos: tuple[int, int], viewport: pygame.Rect) -> tuple[int, int] | None:
        if not viewport.collidepoint(pos):
            return None
        scale_x = GAME_CANVAS_SIZE[0] / viewport.width
        scale_y = GAME_CANVAS_SIZE[1] / viewport.height
        return int((pos[0] - viewport.x) * scale_x), int((pos[1] - viewport.y) * scale_y)

    def _object_at_canvas_pos(self, pos: tuple[int, int]) -> str | None:
        hit_items = [
            (object_id, rect)
            for object_id, rect in self.preview_rects.items()
            if rect.collidepoint(pos)
        ]
        if not hit_items:
            return None
        hit_items.sort(key=lambda item: item[1].width * item[1].height)
        return hit_items[0][0]

    def _set_hover_from_mouse(self, pos: tuple[int, int]) -> None:
        canvas_pos = self._viewport_to_canvas_pos(pos, self._layout_preview_viewport())
        next_hover = self._object_at_canvas_pos(canvas_pos) if canvas_pos is not None else None
        if next_hover == self.hover_layout_object_id:
            return
        self.hover_layout_object_id = next_hover
        self.navigator_body.set_text(self._navigator_html())
        self._update_session_status()

    def _select_hovered_object(self) -> None:
        if self.hover_layout_object_id is None:
            return
        self.selected_layout_object_id = self.hover_layout_object_id
        self.selected_object_snapshot = self._copy_selected_layout_entry()
        self.navigator_body.set_text(self._navigator_html())
        self._update_inspector()
        self._update_session_status()

    def _event_targets_text_entry(self, event: pygame.event.Event) -> bool:
        return getattr(event, "ui_element", None) in self.inspector_field_names_by_element or getattr(event, "ui_element", None) == self.step_field

    def _handle_keyboard_control(self, event: pygame.event.Event) -> bool:
        if event.type != pygame.KEYDOWN:
            return False
        if any(getattr(field, "is_focused", False) for field in self.inspector_fields.values()):
            return False
        if self.step_field is not None and getattr(self.step_field, "is_focused", False):
            return False

        step = self._current_step()
        if event.key == pygame.K_LEFT:
            self._nudge_selected_object(dx=-step)
        elif event.key == pygame.K_RIGHT:
            self._nudge_selected_object(dx=step)
        elif event.key == pygame.K_UP:
            self._nudge_selected_object(dy=-step)
        elif event.key == pygame.K_DOWN:
            self._nudge_selected_object(dy=step)
        else:
            return False
        return True

    def _draw_background(self) -> None:
        self.window.fill(WIN95_FACE)

    def _draw_preview_placeholder(self) -> None:
        panel_rect = self.preview_panel.get_abs_rect()

        viewport = self._layout_preview_viewport()
        draw_sunken_rect(self.window, viewport, PREVIEW_BG)
        felt = viewport.inflate(-80, -70)
        pygame.draw.rect(self.window, PREVIEW_FELT, felt, border_radius=18)
        pygame.draw.rect(self.window, pygame.Color(220, 220, 220), felt, 2, border_radius=18)

        center_lines = [
            "GAME CANVAS 1600 x 900",
            "aspect ratio 16:9",
            "",
            "hover -> подсветка объекта",
            "ЛКМ -> выбор объекта",
            "",
            "только выбор объекта",
            "без drag / resize мышью",
        ]
        y = viewport.y + viewport.height // 2 - 78
        for line in center_lines:
            surface = self.font.render(line, True, WIN95_LIGHT)
            self.window.blit(surface, surface.get_rect(center=(viewport.centerx, y)))
            y += 22

        for object_id, rect in self.preview_rects.items():
            if not self.show_hitboxes and object_id not in {self.hover_layout_object_id, self.selected_layout_object_id}:
                continue
            preview_rect = self._canvas_to_viewport_rect(rect, viewport)
            if object_id == self.selected_layout_object_id:
                color = SELECTED_COLOR
                width = 3
            elif object_id == self.hover_layout_object_id:
                color = HOVER_COLOR
                width = 3
            else:
                color = WIN95_LIGHT
                width = 1
            pygame.draw.rect(self.window, color, preview_rect, width)

        for object_id, label, color in [
            (self.hover_layout_object_id, "hover", HOVER_COLOR),
            (self.selected_layout_object_id, "selected", SELECTED_COLOR),
        ]:
            if object_id is None or object_id not in self.preview_rects:
                continue
            preview_rect = self._canvas_to_viewport_rect(self.preview_rects[object_id], viewport)
            surface = self.small_font.render(label, True, color)
            self.window.blit(surface, (preview_rect.x, max(viewport.y + 4, preview_rect.y - 20)))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
            return
        self.manager.process_events(event)
        if self._handle_keyboard_control(event):
            return
        if event.type == pygame.MOUSEMOTION:
            self._set_hover_from_mouse(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._set_hover_from_mouse(event.pos)
            self._select_hovered_object()
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.ui_element == self.screen_dropdown:
            selected_screen_id = SCREEN_IDS_BY_LABEL.get(event.text)
            if selected_screen_id is not None:
                self.set_current_screen(selected_screen_id)
            return
        if UI_TEXT_ENTRY_FINISHED is not None and event.type == UI_TEXT_ENTRY_FINISHED:
            field_name = self.inspector_field_names_by_element.get(event.ui_element)
            if field_name is not None:
                self._apply_inspector_field_change(field_name, getattr(event, "text", ""))
            return
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.dismiss_button:
                self._dismiss_selected_object_changes()
                return
            if event.ui_element == self.cancel_button:
                self._cancel_selected_object_changes()
                return
            if event.ui_element in self.control_buttons:
                step = self._current_step()
                dx, dy, dw, dh = self.control_buttons[event.ui_element]
                self._nudge_selected_object(dx * step, dy * step, dw * step, dh * step)
                return
            for filter_id, button in self.filter_buttons.items():
                if event.ui_element == button:
                    if filter_id in self.selected_filter_types:
                        self.selected_filter_types.remove(filter_id)
                    else:
                        self.selected_filter_types.add(filter_id)
                    button.set_text(self._filter_text(filter_id, filter_id))
                    return
            if event.ui_element == self.hitboxes_button:
                self.show_hitboxes = not self.show_hitboxes
                self.hitboxes_button.set_text(("[x]" if self.show_hitboxes else "[ ]") + " Show hitboxes")
                return

    def run(self) -> None:
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                self.handle_event(event)

            self.manager.update(time_delta)
            self._draw_background()
            self.manager.draw_ui(self.window)
            self._draw_preview_placeholder()

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    LayoutDebugToolV2Shell().run()
