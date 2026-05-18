# Layout Debug Tool v2: архитектурный аудит кода

Статус: актуализирован после этапа 11.7, 2026-05-18.

Основа анализа: [code_quality_principles.md](code_quality_principles.md).

Связанные backlog:
- [../tasks/architecture/layout_debug_tool_v2_architecture_backlog.md](../tasks/architecture/layout_debug_tool_v2_architecture_backlog.md)
- [../tasks/architecture/layout_debug_tool_v2_stage_11_backlog.md](../tasks/architecture/layout_debug_tool_v2_stage_11_backlog.md)

## 1. Вывод

`Layout Debug Tool v2` больше не является одним большим shell-прототипом. После этапов 1-11.7 основные чистые слои выделены, ключевые сценарии подтверждены пользователем, а минимальные unit-тесты защищают данные, session, clipboard и view-formatting.

Текущая архитектура стала достаточно устойчивой для дальнейшей работы:
- shell остаётся точкой запуска pygame/pygame_gui и сборщиком приложения;
- чтение/сохранение config изолировано;
- RAM-сессия вынесена;
- preview-геометрия вынесена;
- TO DO-логика и clipboard formatter вынесены;
- clipboard IO вынесен в adapter;
- HTML-formatting вынесен из shell;
- event routing разделён по зонам;
- внутренняя геометрия UI-панелей названа через `ShellLayoutMetrics`;
- граница mutable `dict` названа и ограничена совместимостью с `app_config.json` и `LayoutSession`.

Оставшиеся долги уже не выглядят как аварийные. Это управляемые следующие улучшения, которые можно делать маленькими этапами.

## 2. Текущее разбиение кода

```text
tools/layout_debug_tool_v2_shell.py
  pygame window, UI manager, сборка зависимостей, главный цикл, preview drawing

tools/layout_debug/
  models.py
    LayoutObject
    TodoTask
    SelectionState
    ScreenLayoutModel
    LayoutEntryData / ScreenLayoutData / LayoutConfigData

  config_repository.py
    LayoutDataSource
    LayoutConfigRepository
    загрузка app_config.json
    атомарное сохранение layout

  session.py
    LayoutSession
    dirty-state
    selected snapshot
    nudge/update/cancel/reset

  preview_geometry.py
    PreviewGeometryProvider
    PreviewViewportMapper
    object_at_canvas_pos

  todo.py
    TodoService
    TodoClipboardFormatter

  clipboard.py
    PygameClipboardAdapter
    clipboard_text_bytes

  view_formatters.py
    NavigatorViewFormatter
    TodoViewFormatter

  shell_layout.py
    ShellLayoutMetrics
    внешняя и внутренняя геометрия shell

  ui_panels.py
    построение pygame_gui-панелей

  commands.py
    LayoutDebugCommands
    LayoutDebugCommandTargets
```

Unit-тесты:

```text
tests/layout_debug/
  test_clean_layers.py
  test_commands.py
  test_clipboard.py
  test_view_formatters.py
```

## 3. Что приведено в соответствие с принципами

### 3.1. Один модуль — одна зона ответственности

Закрыто частично, но существенно.

Теперь отдельные модули отвечают за:
- модели;
- config persistence;
- RAM-сессию;
- preview-геометрию;
- TO DO-сервис;
- clipboard IO;
- view-formatting;
- shell layout metrics;
- UI-панели;
- command routing.

Остаток: `tools/layout_debug_tool_v2_shell.py` всё ещё собирает приложение, хранит текущее UI-состояние, обновляет виджеты и рисует preview placeholder. Это допустимо для текущего этапа, но при дальнейшем росте shell нужно будет разделить на app/controller/preview renderer.

### 3.2. UI не должен владеть бизнес-логикой

Сильно улучшено.

Shell больше не редактирует layout произвольными dict-операциями. Основные изменения проходят через:
- `LayoutSession.apply_field_change`;
- `LayoutSession.nudge_selected`;
- `LayoutSession.set_todo_text`;
- `LayoutSession.cancel_selected`;
- `LayoutSession.reset`;
- `LayoutConfigRepository.save_layout`.

Остаток: shell всё ещё координирует сценарии вроде `_add_task_for_selected_object`, `_copy_selected_todo_to_clipboard`, `_refresh_layout_session_view`. Это orchestration, а не низкоуровневая бизнес-логика, но позже её можно вынести в application/controller слой.

### 3.3. Данные должны проходить через явную модель

Улучшено.

Появились:
- `LayoutObject`;
- `ScreenLayoutModel`;
- `TodoTask`;
- `SelectionState`;
- named dict boundary: `LayoutEntryData`, `ScreenLayoutData`, `LayoutConfigData`.

Важно: mutable `dict` сохраняется осознанно как boundary для совместимости с текущим `app_config.json` и `LayoutSession`. Это не финальная модель, но теперь граница названа и покрыта тестами.

Остаток: полная миграция на immutable/typed model для редактирования layout пока не сделана. Это лучше оставить отдельным будущим этапом, потому что он может затронуть `Apply`, `Cancel`, `Reset session` и preview.

### 3.4. Сохранение должно быть изолировано

Закрыто.

`LayoutConfigRepository` отвечает за:
- сохранение layout;
- атомарную запись через temporary file;
- сохранение остальных разделов config.

Shell вызывает repository и показывает результат операции.

### 3.5. Геометрия preview должна быть адаптером

Закрыто для текущего preview.

`PreviewGeometryProvider` и `PreviewViewportMapper` отделяют:
- игровые rect;
- layout deltas;
- hit-test;
- canvas/viewport conversion.

Остаток: текущий preview всё ещё placeholder, а не реальный render игровых экранов. Это уже не архитектурный долг shell, а будущий функциональный этап.

### 3.6. События должны превращаться в команды

Улучшено.

`LayoutDebugCommands` больше не зависит от shell напрямую. Он получает `LayoutDebugCommandTargets` и callbacks.

`handle_event` разделён по зонам:
- preview mouse;
- context;
- inspector;
- todo;
- buttons;
- keyboard control.

Остаток: это ещё не полноценная command bus архитектура. Для текущего масштаба достаточно. Следующий возможный шаг — application controller с явными command classes, если сценарии начнут быстро расти.

### 3.7. Временные решения должны быть явно помечены

Закрыто для известных заглушек.

Решение по `Help`, `Copy id`, `Edit` принято: они остаются disabled-заглушками и считаются будущими функциями. Это зафиксировано в stage 11 backlog.

### 3.8. Костыль допустим, если он ограничен

Основной оставшийся компромисс — mutable layout dict boundary. Он ограничен:
- `LayoutDataSource`;
- `LayoutSession`;
- `LayoutConfigRepository`;
- совместимостью с `app_config.json`.

План удаления: будущая модель layout-editing, когда появится необходимость менять contract `app_config.json` или вводить более строгую schema.

### 3.9. Публичное поведение важнее внутренней красоты

Соблюдено.

Каждый этап проходил через:
- unit-тесты;
- `py_compile`;
- ручную проверку пользователя, если изменение могло быть видно в UI.

### 3.10. Маленькие этапы важнее большого переписывания

Соблюдено.

Рефакторинг был проведён серией маленьких этапов:
- 1-10: первичное выделение слоёв;
- 11.1-11.7: cleanup после свежего аудита.

### 3.11. Документация управляет направлением кода

Соблюдено.

Работа ведётся через:
- принципы качества;
- архитектурный аудит;
- backlog этапов;
- ручные подтверждения пользователя.

### 3.12. Удаление лучше скрытого усложнения

Частично закрыто.

Мёртвые поля и вводящие в заблуждение старые элементы были убраны или disabled. Оставшиеся disabled-кнопки явно задокументированы.

## 4. Что уже закрыто из старого аудита

Закрыто:
- shell больше не содержит `_atomic_write_config`;
- shell больше не содержит preview rect methods по каждому экрану;
- shell больше не формирует structured clipboard text задачи;
- shell больше не импортирует `pygame.scrap`;
- shell больше не строит HTML навигатора и выбранной задачи вручную;
- command router больше не принимает shell и не вызывает приватный `_current_step`;
- `handle_event` разделён на route-методы;
- внутренняя геометрия панелей вынесена из `ui_panels.py` в `ShellLayoutMetrics`;
- минимальные unit-тесты добавлены;
- заглушки `Help`, `Copy id`, `Edit` зафиксированы как осознанный долг.

## 5. Актуальные остаточные долги

### 5.1. Shell остаётся orchestration center

`LayoutDebugToolV2Shell` всё ещё:
- создаёт pygame window;
- создаёт UI manager;
- собирает зависимости;
- хранит выбранный экран/объект/hover/todo;
- обновляет панели;
- рисует preview placeholder;
- содержит главный loop.

Это не срочная проблема, но при росте функций стоит выделить:
- `LayoutDebugApp`;
- `LayoutDebugController`;
- `PreviewRenderer`.

### 5.2. UI-панели пока являются builder functions, не полноценными panel objects

`ui_panels.py` возвращает refs-датаклассы, но панели сами не имеют методов `update_from_state`.

Это нормально для текущего масштаба. Если UI начнёт усложняться, следующий шаг:
- `ContextPanel`;
- `NavigatorPanel`;
- `InspectorPanel`;
- `TodoPanel`;
- `StatusBar`;
- каждая панель обновляется из view model.

### 5.3. Mutable layout dict boundary остаётся переходным слоем

Граница названа, но dict всё ещё изменяемый. Это нужно для совместимости с текущими `app_config.json`, `Apply`, `Cancel`, `Reset session`.

Не стоит ломать это без отдельного backlog, потому что риск затронуть сохранение данных выше пользы от немедленной чистоты.

### 5.4. Preview пока не является реальным render игровых экранов

Preview содержит placeholder canvas и overlays hitboxes. Для layout-debugger это пока допустимо, но будущая цель — подключить реальный preview/adapter игровых экранов, чтобы позиционирование было ближе к игре.

### 5.5. Disabled-заглушки остаются будущими функциями

`Help`, `Copy id`, `Edit` оставлены в UI disabled. Это осознанное решение, но их нужно будет либо реализовать, либо убрать в отдельном UX/backlog этапе.

### 5.6. UX навигатора и TO DO требует отдельной доработки

После выноса formatter пользователь подтвердил, что “как-то работает”, но UX навигатора и TO DO оставлен на будущую доработку. Это не блокер архитектурного cleanup, но важный будущий интерфейсный этап.

## 6. Риски на будущее

1. Если добавлять новые функции прямо в shell, он снова начнёт разрастаться.

2. Если усложнять TODO без отдельной модели редактирования задач, появится риск смешать view, selection и persistence.

3. Если менять `app_config.json` contract без migration plan, можно сломать пользовательские layout-данные.

4. Если реальный preview подключать прямо в shell, будет повтор старой проблемы смешения responsibilities.

## 7. Рекомендованный следующий порядок работ

1. Не продолжать архитектурный cleanup ради cleanup, если нет боли.

2. Перед новыми функциями выбрать один узкий product/backlog этап.

3. Если следующим будет UX:
   - отдельно улучшить navigator;
   - отдельно улучшить TO DO;
   - отдельно решить `Help`, `Copy id`, `Edit`.

4. Если следующим будет real preview:
   - делать через `PreviewGeometryProvider`/новый preview adapter;
   - не переносить render-логику в shell.

5. Если следующим будет строгость данных:
   - проектировать отдельный layout editing model;
   - заранее покрыть `Apply`, `Cancel`, `Reset session` тестами.

## 8. Итоговое решение

Код не нужно переписывать с нуля.

Текущая архитектура достаточно здорова для продолжения разработки, если соблюдать правила:
- не добавлять новые сценарии прямо в shell без слоя service/controller;
- держать IO на границах;
- сохранять manual verification для UI-изменений;
- расширять тесты для чистых слоёв;
- вести новые крупные функции от документации и backlog.
