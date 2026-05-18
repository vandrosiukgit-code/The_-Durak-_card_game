from __future__ import annotations

import json
from pathlib import Path

from tools.layout_debug.models import LayoutConfigData, LayoutObject, ScreenLayoutData, ScreenLayoutModel


class LayoutDataSource:
    def __init__(self, config_path: Path, screen_ids: tuple[str, ...]) -> None:
        self.config_path = config_path
        self.screen_ids = screen_ids
        self.data: dict = {}
        # Mutable boundary kept for compatibility with app_config.json and LayoutSession.
        self.layout: LayoutConfigData = {}
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
            screen_model = ScreenLayoutModel.from_config_layout(screen_id, screen_layout)
            self.layout[screen_id] = screen_model.entries
        self.load_error = None

    def screen_ids_found(self) -> list[str]:
        return [
            screen_id
            for screen_id in self.screen_ids
            if self.layout_for_screen(screen_id)
        ]

    def layout_for_screen(self, screen_id: str) -> ScreenLayoutData:
        screen_layout = self.layout.get(screen_id, {})
        return screen_layout if isinstance(screen_layout, dict) else {}

    def screen_model(self, screen_id: str) -> ScreenLayoutModel:
        return ScreenLayoutModel.from_config_layout(screen_id, self.layout_for_screen(screen_id))

    def object_count(self, screen_id: str) -> int:
        return self.screen_model(screen_id).object_count()

    def total_object_count(self) -> int:
        return sum(self.object_count(screen_id) for screen_id in self.screen_ids)

    def objects_for_screen(self, screen_id: str) -> list[LayoutObject]:
        return self.screen_model(screen_id).objects()

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


class LayoutConfigRepository:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path

    def save_layout(self, config_data: dict, layout: LayoutConfigData) -> dict:
        next_config = dict(config_data)
        next_config["layout"] = layout
        self._atomic_write_config(next_config)
        return next_config

    def _atomic_write_config(self, data: dict) -> None:
        temp_path = self.config_path.with_suffix(self.config_path.suffix + ".tmp")
        config_text = json.dumps(data, ensure_ascii=False, indent=2)
        temp_path.write_text(config_text + "\n", encoding="utf-8")
        temp_path.replace(self.config_path)
