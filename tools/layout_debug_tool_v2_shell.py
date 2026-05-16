from __future__ import annotations

import sys
from pathlib import Path

import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIDropDownMenu, UILabel, UIPanel, UITextBox, UITextEntryLine


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

THEME_PATH = PROJECT_ROOT / "ui_theme" / "layout_debug_tool_win95.json"

WINDOW_SIZE = (1600, 1000)
GAME_CANVAS_SIZE = (1600, 900)

CONTEXT_RECT = pygame.Rect(12, 8, 1576, 104)
NAVIGATOR_RECT = pygame.Rect(12, 122, 330, 420)
INSPECTOR_RECT = pygame.Rect(350, 122, 330, 420)
PREVIEW_RECT = pygame.Rect(688, 122, 900, 420)
TODO_RECT = pygame.Rect(12, 552, 1576, 396)
STATUS_RECT = pygame.Rect(4, WINDOW_SIZE[1] - 28, WINDOW_SIZE[0] - 8, 24)

INSPECTOR_CONTENT_X = 10
INSPECTOR_GROUP_X = 8
INSPECTOR_GROUP_WIDTH = 314
INSPECTOR_ACTION_Y = 384
INSPECTOR_GROUP_HEIGHT = 54
INSPECTOR_CONTROL_HEIGHT = 112

WIN95_FACE = pygame.Color(192, 192, 192)
WIN95_DARK = pygame.Color(128, 128, 128)
WIN95_DARKER = pygame.Color(64, 64, 64)
WIN95_LIGHT = pygame.Color(255, 255, 255)
PREVIEW_BG = pygame.Color(18, 70, 44)
PREVIEW_FELT = pygame.Color(24, 104, 62)
HOVER_COLOR = pygame.Color(255, 255, 170)
SELECTED_COLOR = pygame.Color(255, 210, 80)


def draw_sunken_rect(surface: pygame.Surface, rect: pygame.Rect, fill: pygame.Color) -> None:
    pygame.draw.rect(surface, fill, rect)
    pygame.draw.line(surface, WIN95_DARKER, rect.topleft, rect.topright)
    pygame.draw.line(surface, WIN95_DARKER, rect.topleft, rect.bottomleft)
    pygame.draw.line(surface, WIN95_LIGHT, rect.bottomleft, rect.bottomright)
    pygame.draw.line(surface, WIN95_LIGHT, rect.topright, rect.bottomright)


def draw_sunken_frame(surface: pygame.Surface, rect: pygame.Rect) -> None:
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
        self.inspector_group_frames: list[pygame.Rect] = []

        self._build_ui()

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
            options_list=["Игровой стол", "Главное меню", "Стартовая модалка", "Финальная модалка"],
            starting_option="Игровой стол",
            relative_rect=pygame.Rect(72, 32, 220, 28),
            manager=self.manager,
            container=self.context_panel,
        )
        self.status_label = UILabel(
            relative_rect=pygame.Rect(312, 34, 210, 24),
            text="Статус: UNSAVED",
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
            ("TODO", "TODO"),
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
            html_text=(
                "<font face=consolas size=3>"
                "<b>Выбранный путь:</b><br><br>"
                "game_table<br>"
                "`- players<br>"
                "&nbsp;&nbsp;&nbsp;`- left<br>"
                "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`- panel<br>"
                "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- portrait<br>"
                "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- <b>name_label &lt;</b><br>"
                "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- role_label<br>"
                "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`- loss_label"
                "</font>"
            ),
            relative_rect=pygame.Rect(10, 34, 306, 372),
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
            text=f"Ready. Hover: {self.hover_object}. Selected: {self.selected_object}",
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
        self.inspector_group_frames.clear()
        UILabel(
            pygame.Rect(INSPECTOR_CONTENT_X, 34, 150, 20),
            "Object:",
            self.manager,
            container=self.inspector_panel,
            object_id="#win95_label",
        )
        UILabel(
            pygame.Rect(82, 34, 286, 20),
            "player_left_panel",
            self.manager,
            container=self.inspector_panel,
            object_id="#win95_label",
        )
        UILabel(
            pygame.Rect(INSPECTOR_CONTENT_X, 56, 150, 20),
            "Type:",
            self.manager,
            container=self.inspector_panel,
            object_id="#win95_label",
        )
        UILabel(
            pygame.Rect(82, 56, 286, 20),
            "player_panel",
            self.manager,
            container=self.inspector_panel,
            object_id="#win95_label",
        )
        self._inspector_group(
            "GEOMETRY",
            78,
            INSPECTOR_GROUP_HEIGHT,
            [("x", "32"), ("y", "180"), ("width", "170"), ("height", "620")],
        )
        self._inspector_group(
            "LAYOUT DELTAS",
            136,
            INSPECTOR_GROUP_HEIGHT,
            [("delta_x", "0"), ("delta_y", "0"), ("width_delta", "0"), ("height_delta", "0")],
        )
        self._inspector_group(
            "VISUAL",
            194,
            INSPECTOR_GROUP_HEIGHT,
            [("color", "#c0c0c0"), ("font", "Arial"), ("font_size", "14")],
        )
        self._build_inspector_controls(258)

        UIButton(
            pygame.Rect(10, INSPECTOR_ACTION_Y, 94, 24),
            "Dismiss",
            self.manager,
            container=self.inspector_panel,
            object_id="#win95_button",
        )
        UIButton(
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
        self.inspector_group_frames.append(pygame.Rect(INSPECTOR_GROUP_X, y, INSPECTOR_GROUP_WIDTH, height))
        UILabel(
            pygame.Rect(8, 2, 140, 18),
            title,
            self.manager,
            container=panel,
            object_id="#win95_label",
        )
        row_y = 20
        for idx, (label, value) in enumerate(fields):
            px = 8 + (idx % 2) * 150
            py = row_y + (idx // 2) * 18
            label_width = 86 if len(label) > 6 else 50
            input_x = px + label_width
            input_w = 136 - label_width
            UILabel(
                pygame.Rect(px, py, label_width - 4, 18),
                f"{label}:",
                self.manager,
                container=panel,
                object_id="#win95_small_label",
            )
            UITextEntryLine(
                relative_rect=pygame.Rect(input_x, py, input_w, 18),
                manager=self.manager,
                container=panel,
                initial_text=value,
                object_id="#win95_input",
            )

    def _build_inspector_controls(self, y: int) -> None:
        panel = UIPanel(
            relative_rect=pygame.Rect(INSPECTOR_GROUP_X, y, INSPECTOR_GROUP_WIDTH, INSPECTOR_CONTROL_HEIGHT),
            manager=self.manager,
            container=self.inspector_panel,
            object_id="#win95_sunken_panel",
        )
        self.inspector_group_frames.append(pygame.Rect(INSPECTOR_GROUP_X, y, INSPECTOR_GROUP_WIDTH, INSPECTOR_CONTROL_HEIGHT))
        UILabel(pygame.Rect(8, 2, 120, 18), "CONTROL", self.manager, container=panel, object_id="#win95_label")
        UILabel(pygame.Rect(8, 26, 42, 20), "Step:", self.manager, container=panel, object_id="#win95_label")
        UITextEntryLine(
            relative_rect=pygame.Rect(56, 24, 58, 22),
            manager=self.manager,
            container=panel,
            initial_text="10",
            object_id="#win95_input",
        )

        UILabel(pygame.Rect(8, 56, 50, 20), "Move:", self.manager, container=panel, object_id="#win95_label")
        for idx, text in enumerate(["<-", "^", "v", "->"]):
            UIButton(pygame.Rect(62 + idx * 42, 52, 36, 24), text, self.manager, container=panel, object_id="#win95_button")

        UILabel(pygame.Rect(8, 86, 42, 20), "Size:", self.manager, container=panel, object_id="#win95_label")
        for idx, text in enumerate(["-W", "+W", "-H", "+H"]):
            UIButton(pygame.Rect(62 + idx * 42, 82, 36, 24), text, self.manager, container=panel, object_id="#win95_button")

    def _build_todo(self) -> None:
        self.todo_list = UITextBox(
            html_text=(
                "<font face=consolas size=3>"
                "<b>СПИСОК ЗАДАЧ</b><br><br>"
                "[ ] game_table.player_left_panel<br>"
                "&nbsp;&nbsp;&nbsp;&nbsp;Поднять выше<br><br>"
                "[!] game_ui.pass_button<br>"
                "&nbsp;&nbsp;&nbsp;&nbsp;Сдвинуть ближе к Take<br><br>"
                "[ ] modal_intro.panel<br>"
                "&nbsp;&nbsp;&nbsp;&nbsp;Уменьшить ширину"
                "</font>"
            ),
            relative_rect=pygame.Rect(10, 38, 720, 338),
            manager=self.manager,
            container=self.todo_panel,
            object_id="#win95_textbox",
        )
        UILabel(
            pygame.Rect(748, 38, 430, 24),
            "ЗАДАЧА ВЫБРАННОГО ОБЪЕКТА",
            self.manager,
            container=self.todo_panel,
            object_id="#win95_label",
        )
        UILabel(
            pygame.Rect(748, 64, 500, 22),
            "Object: game_table.player_left_panel",
            self.manager,
            container=self.todo_panel,
            object_id="#win95_label",
        )
        self.todo_text = UITextBox(
            html_text="Поднять панель выше и выровнять относительно верхней панели игрока.",
            relative_rect=pygame.Rect(748, 92, 520, 176),
            manager=self.manager,
            container=self.todo_panel,
            object_id="#win95_textbox",
        )
        for idx, text in enumerate(["Save TO DO", "Clear TO DO", "Go to obj", "Copy task"]):
            UIButton(
                pygame.Rect(748 + idx * 132, 282, 122, 28),
                text,
                self.manager,
                container=self.todo_panel,
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

        hover_rect = pygame.Rect(viewport.x + 66, viewport.y + 88, 130, 190)
        selected_rect = pygame.Rect(viewport.x + 210, viewport.y + 92, 110, 26)
        pygame.draw.rect(self.window, HOVER_COLOR, hover_rect, 2)
        pygame.draw.rect(self.window, SELECTED_COLOR, selected_rect, 3)
        hover = self.small_font.render("hover", True, HOVER_COLOR)
        selected = self.small_font.render("selected", True, SELECTED_COLOR)
        self.window.blit(hover, (hover_rect.x, hover_rect.y - 20))
        self.window.blit(selected, (selected_rect.x, selected_rect.y - 20))

    def _draw_inspector_group_frames(self) -> None:
        inspector_rect = self.inspector_panel.get_abs_rect()
        for rect in self.inspector_group_frames:
            draw_sunken_frame(self.window, rect.move(inspector_rect.topleft))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
            return
        self.manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
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
            self._draw_inspector_group_frames()
            self._draw_preview_placeholder()

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    LayoutDebugToolV2Shell().run()
