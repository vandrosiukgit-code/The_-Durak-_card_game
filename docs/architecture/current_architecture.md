# Текущая архитектура проекта

Этот документ даёт короткую справку по текущему состоянию проекта `Durak`.

## 1. Точка входа

- [main.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/main.py)

Файл минимальный: он создаёт `DurakApp` и запускает приложение.

## 2. Основные слои проекта

Проект разделён на три уровня:

1. `card_engine` — игровая логика и правила.
2. `durak_app` — приложение, интерфейс и рендер.
3. `tools` — вспомогательные инструменты разработки.

## 3. Игровое ядро: `card_engine`

Ключевые модули:

- [card_engine/cards.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/card_engine/cards.py) — карты, масти и достоинства;
- [card_engine/hand.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/card_engine/hand.py) — рука игрока;
- [card_engine/deck.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/card_engine/deck.py) — живая колода;
- [card_engine/factories.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/card_engine/factories.py) — фабрики колод;
- [card_engine/durak_state.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/card_engine/durak_state.py) — основное состояние игры и правила подкидного дурака.

## 4. Слой приложения: `durak_app`

### [durak_app/app.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/app.py)

Главный координатор приложения.

Отвечает за:

- запуск `pygame`;
- загрузку конфига и ассетов;
- создание меню, игрового стола, GUI-слоя и модалок;
- главный цикл приложения;
- связку интерфейса с `card_engine`.

### [durak_app/game_table.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/game_table.py)

Отвечает за сцену игрового стола на чистом `pygame`:

- сукно;
- зоны игроков;
- руки;
- карты на столе;
- колоду и козырь;
- портреты;
- layout-геометрию сценических блоков.

Этот модуль больше не содержит ручных игровых кнопок и не владеет текстовым GUI.

### [durak_app/gui_layer.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/gui_layer.py)

Центральный слой `pygame_gui` для игрового режима.

Отвечает за:

- `UIManager`;
- панель `Actions`;
- кнопки `Pass`, `Take`, `Restart`, `Surrender`;
- заголовок и служебные строки игрового стола;
- подписи игроков;
- счётчики поражений;
- маршрутизацию GUI-событий.

### [durak_app/menu.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/menu.py)

Главное меню проекта.

Собрано на `pygame_gui` и отвечает за:

- настройки матча;
- выбор рубашек карт;
- выбор наборов лиц карт;
- выбор портретов;
- overlay и dropdown-интерфейсы меню.

### [durak_app/modals.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/modals.py)

Отвечает за модальные окна на `pygame_gui`:

- стартовое окно;
- финальное окно;
- overlay;
- panel;
- labels;
- кнопки действий;
- блоки статистики.

### [durak_app/ui.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/ui.py)

Содержит только низкоуровневые утилиты анимации. На текущем этапе модуль нужен в первую очередь для `CardAnimation`.

### [durak_app/config.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/config.py)

Содержит:

- константы интерфейса;
- класс `AppConfig`;
- работу с постоянным конфигом проекта.

## 5. Текущая модель интерфейса

На текущем этапе проект использует постоянную схему:

- сцена игры остаётся на `pygame`;
- весь интерфейсный и интерактивный слой живёт в `pygame_gui`.

Это означает:

- карты и стол рисуются как игровая сцена;
- кнопки, панели, подписи, меню и модалки живут в одной GUI-системе.

## 6. Постоянная конфигурация

- [app_config.json](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/app_config.json)

Файл хранит:

- визуальные настройки;
- значения по умолчанию для новых матчей;
- layout-дельты интерфейсных объектов.

Он используется как основа для отладки интерфейса и для `layout_debug_tool.py`.

## 7. Инструменты разработки

- [tools/layout_debug_tool.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/tools/layout_debug_tool.py) — отдельная графическая утилита настройки layout;
- [tools/card_image_resize_tool](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/tools/card_image_resize_tool) — инструменты подготовки изображений карт;
- [tools/frame_tool](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/tools/frame_tool) — инструменты для рамок и карточных ассетов.

## 8. Рекомендуемый порядок чтения кода

Если нужно быстро восстановить картину проекта, удобнее читать файлы так:

1. [main.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/main.py)
2. [durak_app/app.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/app.py)
3. [card_engine/durak_state.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/card_engine/durak_state.py)
4. [durak_app/game_table.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/game_table.py)
5. [durak_app/gui_layer.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/gui_layer.py)
6. [durak_app/menu.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/menu.py)
7. [durak_app/modals.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/modals.py)
8. [durak_app/config.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/config.py)
9. [tools/layout_debug_tool.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/tools/layout_debug_tool.py)
