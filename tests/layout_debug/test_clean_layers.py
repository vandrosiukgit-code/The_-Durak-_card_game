from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.layout_debug.config_repository import LayoutConfigRepository, LayoutDataSource
from tools.layout_debug.models import LayoutObject, ScreenLayoutModel
from tools.layout_debug.session import LayoutSession
from tools.layout_debug.todo import TodoClipboardFormatter


SCREEN_IDS = ("game_table", "main_menu", "modal_intro", "modal_endgame")


class LayoutObjectTests(unittest.TestCase):
    def test_from_config_entry_normalizes_safe_values(self) -> None:
        layout_object = LayoutObject.from_config_entry(
            "game_table",
            "player_left_panel",
            {
                "type": "panel",
                "x": "12",
                "y": None,
                "width": "bad",
                "height": 140,
                "delta_x": 3,
                "delta_y": "4",
                "width_delta": None,
                "height_delta": "5",
                "color": "#c0c0c0",
                "font": 123,
                "font_size": "16",
                "todo_text": "Поднять выше",
            },
        )

        self.assertEqual(layout_object.path, "game_table.player_left_panel")
        self.assertEqual(layout_object.object_type, "panel")
        self.assertEqual(layout_object.x, 12)
        self.assertEqual(layout_object.y, 0)
        self.assertEqual(layout_object.width, 0)
        self.assertEqual(layout_object.height, 140)
        self.assertEqual(layout_object.delta_x, 3)
        self.assertEqual(layout_object.delta_y, 4)
        self.assertEqual(layout_object.width_delta, 0)
        self.assertEqual(layout_object.height_delta, 5)
        self.assertEqual(layout_object.color, "#c0c0c0")
        self.assertEqual(layout_object.font, "")
        self.assertEqual(layout_object.font_size, 16)
        self.assertEqual(layout_object.todo_text, "Поднять выше")


class ScreenLayoutModelTests(unittest.TestCase):
    def test_from_config_layout_normalizes_entries_and_sorts_objects(self) -> None:
        screen_model = ScreenLayoutModel.from_config_layout(
            "game_table",
            {
                "z_panel": {"type": "panel", "x": 10},
                "a_button": {"type": "button", "x": 20},
                "broken": "not a dict",
            },
        )

        self.assertEqual(screen_model.object_count(), 3)
        self.assertEqual(screen_model.entries["broken"], {})
        self.assertEqual(
            [layout_object.object_id for layout_object in screen_model.objects()],
            ["broken", "a_button", "z_panel"],
        )


class LayoutDataSourceTests(unittest.TestCase):
    def test_load_reads_known_screens_and_builds_objects(self) -> None:
        config_path = _write_config(
            {
                "window": {"width": 1600},
                "layout": {
                    "game_table": {
                        "deck_panel": {"type": "panel", "x": 10},
                    },
                    "main_menu": {
                        "start_button": {"type": "button", "x": 20},
                    },
                    "unknown_screen": {
                        "ignored": {"type": "panel"},
                    },
                },
            }
        )

        data_source = LayoutDataSource(config_path, SCREEN_IDS)
        data_source.load()

        self.assertIsNone(data_source.load_error)
        self.assertEqual(data_source.screen_ids_found(), ["game_table", "main_menu"])
        self.assertEqual(data_source.total_object_count(), 2)
        self.assertEqual(
            [item.object_id for item in data_source.objects_for_screen("main_menu")],
            ["start_button"],
        )

    def test_load_exposes_named_mutable_config_boundary_for_session(self) -> None:
        config_path = _write_config(
            {
                "layout": {
                    "game_table": {
                        "deck_panel": {"type": "panel", "delta_x": 0},
                    },
                },
            }
        )

        data_source = LayoutDataSource(config_path, SCREEN_IDS)
        data_source.load()

        session = LayoutSession(data_source.layout)
        self.assertTrue(session.nudge_selected("game_table", "deck_panel", dx=5))
        self.assertEqual(data_source.layout["game_table"]["deck_panel"]["delta_x"], 5)
        self.assertEqual(data_source.objects_for_screen("game_table")[0].delta_x, 5)

        session.reset()
        self.assertEqual(data_source.layout["game_table"]["deck_panel"]["delta_x"], 0)
        self.assertEqual(data_source.objects_for_screen("game_table")[0].delta_x, 0)


class LayoutConfigRepositoryTests(unittest.TestCase):
    def test_save_layout_preserves_non_layout_config_sections(self) -> None:
        config_path = _write_config(
            {
                "window": {"width": 1600, "height": 900},
                "theme": {"name": "win95"},
                "layout": {"game_table": {"old": {"type": "panel"}}},
            }
        )
        repository = LayoutConfigRepository(config_path)

        next_config = repository.save_layout(
            {
                "window": {"width": 1600, "height": 900},
                "theme": {"name": "win95"},
                "layout": {"game_table": {"old": {"type": "panel"}}},
            },
            {"game_table": {"new": {"type": "button", "x": 42}}},
        )

        saved_config = json.loads(config_path.read_text(encoding="utf-8"))
        self.assertEqual(saved_config["window"], {"width": 1600, "height": 900})
        self.assertEqual(saved_config["theme"], {"name": "win95"})
        self.assertEqual(saved_config["layout"], {"game_table": {"new": {"type": "button", "x": 42}}})
        self.assertEqual(saved_config, next_config)


class LayoutSessionTests(unittest.TestCase):
    def test_dirty_mark_applied_cancel_and_reset(self) -> None:
        layout = {
            "game_table": {
                "deck_panel": {
                    "type": "panel",
                    "x": 10,
                    "y": 20,
                    "delta_x": 0,
                    "delta_y": 0,
                }
            }
        }
        session = LayoutSession(layout)

        self.assertFalse(session.dirty)
        session.snapshot_selected("game_table", "deck_panel")
        self.assertTrue(session.nudge_selected("game_table", "deck_panel", dx=5))
        self.assertTrue(session.dirty)
        self.assertEqual(layout["game_table"]["deck_panel"]["delta_x"], 5)

        self.assertTrue(session.cancel_selected("game_table", "deck_panel"))
        self.assertEqual(layout["game_table"]["deck_panel"]["delta_x"], 0)
        self.assertFalse(session.dirty)

        self.assertTrue(session.nudge_selected("game_table", "deck_panel", dy=7))
        session.mark_applied()
        self.assertFalse(session.dirty)
        self.assertEqual(session.initial_layout["game_table"]["deck_panel"]["delta_y"], 7)

        self.assertTrue(session.nudge_selected("game_table", "deck_panel", dy=3))
        self.assertTrue(session.dirty)
        session.reset()
        self.assertEqual(layout["game_table"]["deck_panel"]["delta_y"], 7)
        self.assertFalse(session.dirty)


class TodoClipboardFormatterTests(unittest.TestCase):
    def test_structured_text_keeps_russian_task_text(self) -> None:
        layout_object = LayoutObject.from_config_entry(
            "game_table",
            "bottom_hand_area",
            {
                "type": "hand_zone",
                "todo_text": "Это тестовая задача!\nПоднять выше.",
            },
        )

        text = TodoClipboardFormatter().structured_text(layout_object)

        self.assertEqual(
            text,
            "Layout Debug Tool task\n"
            "Screen: game_table\n"
            "Object: bottom_hand_area\n"
            "Path: game_table.bottom_hand_area\n"
            "Type: hand_zone\n"
            "\n"
            "Task:\n"
            "Это тестовая задача!\n"
            "Поднять выше.",
        )


def _write_config(data: dict) -> Path:
    temp_dir = tempfile.TemporaryDirectory()
    path = Path(temp_dir.name) / "app_config.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    _TEMP_DIRS.append(temp_dir)
    return path


_TEMP_DIRS: list[tempfile.TemporaryDirectory] = []


if __name__ == "__main__":
    unittest.main()
