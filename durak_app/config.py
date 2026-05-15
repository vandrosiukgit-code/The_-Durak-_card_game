import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pygame

BASE_DIR = Path(__file__).resolve().parent.parent
APP_CONFIG_PATH = BASE_DIR / "app_config.json"

CARD_SCALE_FACTOR = 0.85
WIDTH, HEIGHT = 1600, 900
FPS = 60

CARD_WIDTH = int(160 * CARD_SCALE_FACTOR)
CARD_HEIGHT = int(240 * CARD_SCALE_FACTOR)
BOT_CARD_WIDTH = int(112 * CARD_SCALE_FACTOR)
BOT_CARD_HEIGHT = int(168 * CARD_SCALE_FACTOR)

PORTRAIT_SIZE = 110
PLAYER_HAND_SIZE = 6
BOTTOM_ZONE_HEIGHT = 340
BOTTOM_ZONE_TOP = HEIGHT - BOTTOM_ZONE_HEIGHT - 100
SIDE_ZONE_TOP = 180
TABLE_RECT = pygame.Rect(280, 170, WIDTH - 560, HEIGHT - 525)
RIGHT_SERVICE_TOP = TABLE_RECT.y + 40
RIGHT_SERVICE_X = WIDTH // 2 + 160

TABLE_COLOR = (22, 96, 58)
FELT_DARK = (16, 68, 42)
PANEL_COLOR = (18, 57, 40)
TEXT_COLOR = (245, 245, 245)
MUTED_TEXT = (215, 224, 215)
BUTTON_COLOR = (231, 194, 87)
BUTTON_HOVER = (244, 210, 114)
BUTTON_TEXT = (35, 30, 24)
SLOT_COLOR = (205, 214, 205)
RESERVED_BG = (38, 82, 62)
SELECTION_COLOR = (255, 223, 120)
ACTION_DISABLED = (120, 121, 118)

PLAYER_NAMES = {
    "left": "Bot Left",
    "top": "Bot Top",
    "right": "Bot Right",
    "bottom": "You",
}

OPENING_MODE_LABELS = {
    "classic": "Classic rules",
    "player": "You first",
    "random": "Random first",
}

ANIMATION_SPEED_LABELS = {
    "slow": "Slow",
    "normal": "Normal",
    "fast": "Fast",
}

ANIMATION_SPEED_FACTORS = {
    "slow": 1.35,
    "normal": 1.0,
    "fast": 0.78,
}

CARD_BACK_OPTIONS = [
    {"id": "default", "label": "Default back", "path": str(BASE_DIR / "assets" / "cards" / "backs" / "default_back.png.png")},
    {"id": "back_2", "label": "Back slot 2", "path": str(BASE_DIR / "assets" / "themes" / "card_backs" / "set_2" / "default_back.png")},
    {"id": "back_3", "label": "Back slot 3", "path": str(BASE_DIR / "assets" / "themes" / "card_backs" / "set_3" / "default_back.png")},
    {"id": "back_4", "label": "Back slot 4", "path": str(BASE_DIR / "assets" / "themes" / "card_backs" / "set_4" / "default_back.png")},
]

CARD_FACE_OPTIONS = [
    {"id": "default", "label": "Default faces", "path": str(BASE_DIR / "assets" / "cards" / "faces" / "set_1")},
    {"id": "faces_2", "label": "Face slot 2", "path": str(BASE_DIR / "assets" / "themes" / "card_faces" / "set_2")},
    {"id": "faces_3", "label": "Face slot 3", "path": str(BASE_DIR / "assets" / "themes" / "card_faces" / "set_3")},
    {"id": "faces_4", "label": "Face slot 4", "path": str(BASE_DIR / "assets" / "themes" / "card_faces" / "set_4")},
]

PORTRAIT_SET_OPTIONS = [
    {"id": "default", "label": "Default portraits", "path": str(BASE_DIR / "assets" / "portraits")},
    {"id": "portraits_2", "label": "Portrait slot 2", "path": str(BASE_DIR / "assets" / "themes" / "portraits" / "set_2")},
    {"id": "portraits_3", "label": "Portrait slot 3", "path": str(BASE_DIR / "assets" / "themes" / "portraits" / "set_3")},
    {"id": "portraits_4", "label": "Portrait slot 4", "path": str(BASE_DIR / "assets" / "themes" / "portraits" / "set_4")},
]


def _deep_merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


class AppConfig:
    def __init__(self, path: Path = APP_CONFIG_PATH) -> None:
        self.path = path
        self.data = self._load_or_create()

    @staticmethod
    def build_base_schema() -> dict[str, Any]:
        return {
            "app": {
                "version": 1,
            },
            "visual": {
                "card_back": "default",
                "card_faces": "default",
                "portrait_set": "default",
                "portrait_files": {
                    "left": "bot_left.png",
                    "top": "bot_top.png",
                    "right": "bot_right.png",
                    "bottom": "player_you.png",
                },
                "custom_back_file": None,
            },
            "defaults": {
                "loss_limit": 3,
                "opening_mode": "classic",
                "animation_speed": "normal",
            },
            "layout": {},
        }

    def _load_or_create(self) -> dict[str, Any]:
        base_schema = self.build_base_schema()
        if not self.path.exists():
            self._write(base_schema)
            return base_schema
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self._write(base_schema)
            return base_schema
        merged = _deep_merge_dicts(base_schema, loaded if isinstance(loaded, dict) else {})
        self._write(merged)
        return merged

    def _write(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def save(self) -> None:
        self._write(self.data)

    def sync_layout_schema(self, layout_providers: dict[str, dict[str, dict[str, int]]]) -> None:
        current_layout = self.data.setdefault("layout", {})
        synced_layout: dict[str, Any] = {}

        for screen_id, blocks in layout_providers.items():
            stored_screen = current_layout.get(screen_id, {})
            synced_screen: dict[str, Any] = {}
            for block_id, defaults in blocks.items():
                block_schema = {
                    "delta_x": 0,
                    "delta_y": 0,
                    "width_delta": 0,
                    "height_delta": 0,
                    "todo_text": "",
                    "module": "",
                    "type": "block",
                    "label": block_id,
                }
                block_schema.update(defaults)
                stored_block = stored_screen.get(block_id, {})
                synced_screen[block_id] = {
                    **block_schema,
                    "delta_x": int(stored_block.get("delta_x", block_schema["delta_x"])),
                    "delta_y": int(stored_block.get("delta_y", block_schema["delta_y"])),
                    "width_delta": int(stored_block.get("width_delta", block_schema["width_delta"])),
                    "height_delta": int(stored_block.get("height_delta", block_schema["height_delta"])),
                    "todo_text": str(stored_block.get("todo_text", block_schema["todo_text"])),
                }
            synced_layout[screen_id] = synced_screen

        self.data["layout"] = synced_layout
        self.save()

    def get_layout_delta(self, screen_id: str, block_id: str) -> tuple[int, int]:
        block = self.data.get("layout", {}).get(screen_id, {}).get(block_id, {})
        return int(block.get("delta_x", 0)), int(block.get("delta_y", 0))

    def get_layout_size_delta(self, screen_id: str, block_id: str) -> tuple[int, int]:
        block = self.data.get("layout", {}).get(screen_id, {}).get(block_id, {})
        return int(block.get("width_delta", 0)), int(block.get("height_delta", 0))

    def get_layout_entry(self, screen_id: str, block_id: str) -> dict[str, Any]:
        return self.data.setdefault("layout", {}).setdefault(screen_id, {}).setdefault(
            block_id,
            {
                "delta_x": 0,
                "delta_y": 0,
                "width_delta": 0,
                "height_delta": 0,
                "todo_text": "",
                "module": "",
                "type": "block",
                "label": block_id,
            },
        )
