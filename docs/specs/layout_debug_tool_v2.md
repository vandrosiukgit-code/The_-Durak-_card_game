# Layout Debug Tool v2

Статус: рабочая живая версия v2 после архитектурного cleanup, 2026-05-18.

Каноническая карта экрана: [layout_debug_tool_v2_screen_map.md](layout_debug_tool_v2_screen_map.md).

Рабочий backlog v2 закрыт: [layout_debug_tool_backlog.md](layout_debug_tool_backlog.md).

## 1. Назначение

`Layout Debug Tool v2` — отдельная графическая dev-утилита для настройки layout проекта `Durak`.

Утилита нужна, чтобы:
- выбирать реальные layout-объекты без ручного чтения JSON;
- видеть объект в контексте игрового экрана;
- менять безопасный набор layout-свойств;
- держать изменения в RAM-сессии до явного `Apply`;
- вести задачи по объектам через встроенный `TO DO`;
- копировать задачу в чат как структурированный текст.

## 2. Реализация

Точка входа:
- `tools/layout_debug_tool_v2_shell.py`

Внутренние модули:
- `tools/layout_debug/models.py`;
- `tools/layout_debug/config_repository.py`;
- `tools/layout_debug/session.py`;
- `tools/layout_debug/preview_geometry.py`;
- `tools/layout_debug/todo.py`;
- `tools/layout_debug/clipboard.py`;
- `tools/layout_debug/view_formatters.py`;
- `tools/layout_debug/shell_layout.py`;
- `tools/layout_debug/ui_panels.py`;
- `tools/layout_debug/commands.py`.

Тема:
- `ui_theme/layout_debug_tool_win95.json`

Окно:
- размер shell: `1600 x 940`;
- игровой canvas внутри preview: `1600 x 900`;
- aspect ratio preview: `16:9`.

Поддерживаемые экраны:
- `game_table`;
- `main_menu`;
- `modal_intro`;
- `modal_endgame`.

## 3. Главный UI-принцип

Shell-интерфейс строится на `pygame_gui` в стиле Windows 95/98.

Ручная pygame-отрисовка допускается только внутри `PREVIEW AREA`. Это правило нужно, чтобы shell утилиты визуально не смешивался со стилем игры.

## 4. Зоны интерфейса

### 4.1. Панель контекста

Содержит:
- выбор экрана;
- статус RAM-сессии;
- `Apply`;
- `Reset session`;
- `Help`;
- фильтры объектов;
- `Show hitboxes`.

`Apply` и `Reset session` работают на уровне всей RAM-сессии.

### 4.2. Навигатор объектов

Навигатор показывает структуру объектов текущего экрана и отмечает:
- выбранный объект;
- hover-объект;
- layout-deltas объекта.

Список обновляется при:
- переключении экрана;
- hover/select в `PREVIEW AREA`;
- изменениях инспектора или control-блока.

### 4.3. Инспектор

Инспектор подключён к выбранному объекту через безопасную property-схему.

Редактируемые свойства:
- `x`;
- `y`;
- `width`;
- `height`;
- `delta_x`;
- `delta_y`;
- `width_delta`;
- `height_delta`;
- `color`;
- `font`;
- `font_size`.

Кнопки:
- `Dismiss`;
- `Cancel`;
- `Copy id`.

Семантика:
- `Dismiss` принимает текущую RAM-точку выбранного объекта как новую локальную точку отката;
- `Cancel` откатывает выбранный объект к snapshot;
- `Copy id` зарезервирована под копирование идентификатора объекта.

### 4.4. Control

Блок `CONTROL` находится внутри инспектора.

Содержит:
- `Step`;
- `Move`: `<-`, `^`, `v`, `->`;
- `Size`: `-W`, `+W`, `-H`, `+H`.

Стрелки клавиатуры дублируют движение объекта и используют текущее значение `Step`.

### 4.5. Preview Area

`PREVIEW AREA` показывает текущий экран в координатах игрового canvas `1600 x 900`.

Поведение:
- hover мышью подсвечивает объект;
- ЛКМ выбирает объект;
- выбранный объект подсвечивается отдельно;
- `Show hitboxes` показывает все hitbox-rect;
- drag/resize мышью запрещены.

Все изменения положения и размера выполняются через инспектор, control-кнопки или стрелки клавиатуры.

### 4.6. TO DO

`TO DO` разделён на две зоны.

`ПРОСМОТР СОЗДАННЫХ ЗАДАЧ`:
- список задач строится из `layout.<screen>.<object>.todo_text`;
- выбранная задача показывается в просмотрщике;
- `Copy` копирует структурированный текст задачи в буфер обмена;
- `Edit` оставлен как кнопка будущего редактирования.

`СОЗДАТЬ НОВУЮ ЗАДАЧУ`:
- многострочное поле описания;
- `Add task` записывает текст в `todo_text` выбранного объекта в RAM-сессии;
- `Clean` очищает поле создания.

## 5. RAM-сессия и сохранение

При запуске утилита загружает `app_config.json` и создаёт рабочую RAM-копию layout.

Правила:
- изменения инспектора, control-блока и `TO DO` сначала живут только в памяти;
- статус показывает, есть ли несохранённые изменения;
- `Reset session` откатывает всю RAM-сессию к состоянию запуска;
- `Apply` сохраняет RAM-layout в `app_config.json`.

`Apply`:
- сохраняет остальные разделы конфига;
- пишет JSON с `ensure_ascii=False`;
- использует временный файл;
- завершает сохранение атомарной заменой файла.

## 6. Copy task

`Copy` в блоке `TO DO` копирует не JSON, а текстовый структурированный объект для передачи в чат.

Формат:

```text
Layout Debug Tool task
Screen: game_table
Object: bottom_hand_area
Path: game_table.bottom_hand_area
Type: hand_zone

Task:
Это тестовая задача!
```

На Windows текст кодируется для системного буфера обмена так, чтобы русские символы не превращались в mojibake.

## 7. Критерии закрытия v2 backlog

Backlog v2 считается закрытым, потому что:

1. Shell собран на `pygame_gui`.
2. Стиль shell соответствует Windows 95/98.
3. Подключены реальные layout-данные.
4. Подключены реальные экраны.
5. Навигатор объектов обновляется от текущего экрана и выбора.
6. Hover/select в `PREVIEW AREA` работают.
7. Инспектор редактирует безопасный набор свойств.
8. Control-кнопки и клавиатурные стрелки меняют объект.
9. RAM-сессия, `Dismiss`, `Cancel`, `Reset session` и `Apply` подключены.
10. `TO DO` умеет создавать, показывать и копировать задачи.

## 8. Архитектурное состояние

После закрытия рабочего v2 backlog был проведён отдельный архитектурный cleanup.

Документы:
- [../architecture/code_quality_principles.md](../architecture/code_quality_principles.md);
- [../architecture/layout_debug_tool_v2_code_audit.md](../architecture/layout_debug_tool_v2_code_audit.md);
- [../tasks/architecture/layout_debug_tool_v2_architecture_backlog.md](../tasks/architecture/layout_debug_tool_v2_architecture_backlog.md);
- [../tasks/architecture/layout_debug_tool_v2_stage_11_backlog.md](../tasks/architecture/layout_debug_tool_v2_stage_11_backlog.md).

Итог:
- чистые слои выделены;
- command routing отделён от прямой зависимости на shell;
- clipboard IO вынесен в adapter;
- HTML-formatting вынесен из shell;
- event routing разделён по зонам;
- внутренняя геометрия UI-панелей названа в `ShellLayoutMetrics`;
- граница mutable layout-`dict` явно названа и покрыта тестами;
- добавлены минимальные unit-тесты чистых слоёв.

## 9. Ограничения текущей версии

Эти пункты не блокируют закрытие v2 backlog и переносятся в следующий backlog:

- `Help`, `Copy id`, `Edit` оставлены как disabled-заглушки и будущие функции;
- `Edit` для существующей задачи пока не реализован;
- UX многострочного поля создания задачи требует полировки;
- визуальный компонент списка задач пока рабочий, но не финальный;
- навигатор объектов пока не полноценное дерево `pygame_gui`;
- preview отображает техническую модель rect-объектов, а не полный визуальный слой игры.
