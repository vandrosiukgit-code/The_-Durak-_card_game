# Текущая архитектура проекта

Этот документ даёт краткую справку по текущей архитектуре проекта `Durak` и помогает быстро восстановить картину после паузы в работе.

## 1. Точка входа

- [main.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/main.py)

Файл намеренно оставлен минимальным. Он только создаёт экземпляр `DurakApp` и запускает главный цикл приложения.

## 2. Основные слои проекта

Сейчас проект разделён на три основных слоя:

1. `card_engine` — игровые правила и доменная логика.
2. `durak_app` — слой приложения, рендер, GUI, конфигурация и связка с игровым ядром.
3. `tools` — вспомогательные инструменты разработки.

## 3. Игровое ядро: `card_engine`

- [card_engine/cards.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/card_engine/cards.py)  
  Описывает карты, масти, достоинства и базовую модель стандартной игральной карты.

- [card_engine/hand.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/card_engine/hand.py)  
  Хранит руку игрока и базовые операции с картами в руке.

- [card_engine/deck.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/card_engine/deck.py)  
  Реализует живую колоду: перемешивание, добор, раздачу, сброс и повторное использование сброса.

- [card_engine/factories.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/card_engine/factories.py)  
  Содержит фабрики стандартных колод. Для текущей реализации дурака используется 36-карточная колода.

- [card_engine/durak_state.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/card_engine/durak_state.py)  
  Главный state machine игры. Отвечает за:
  - создание новой партии;
  - выбор козыря;
  - фазы `attack / defend / toss / toss_after_take / game_over`;
  - правила отбоя и подкидывания;
  - добор карт;
  - автоходы ботов;
  - определение проигравшего (`durak`);
  - служебные данные для анимаций, например `recent_deck_draws`.

## 4. Слой приложения: `durak_app`

- [durak_app/app.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/app.py)  
  Главный контроллер приложения. Связывает игровую логику, рендер, анимации, постоянную конфигурацию, меню, GUI и модальные окна.

- [durak_app/config.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/config.py)  
  Хранит общие константы интерфейса и реализует `AppConfig`, который работает с `app_config.json`.

- [durak_app/game_table.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/game_table.py)  
  Отвечает за отрисовку игрового стола на чистом `pygame`:
  - фон и сукно;
  - зоны игроков;
  - колоду и козырь;
  - карты на столе;
  - руку игрока;
  - layout-блоки для отладочной утилиты.

- [durak_app/menu.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/menu.py)  
  Экран главного меню. Сохраняет текущий визуальный стиль проекта, но интерактивность меню уже переведена на `pygame_gui`.
  Отвечает за:
  - параметры матча;
  - выбор рубашек карт;
  - выбор набора лиц карт;
  - выбор портретов;
  - overlay-режимы настройки.

- [durak_app/menu_support.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/menu_support.py)  
  Вспомогательные классы для меню. Здесь находятся загрузка ассетов и работа с сетками предпросмотра.

- [durak_app/gui_layer.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/gui_layer.py)  
  Центральный слой интеграции `pygame_gui`. Отвечает за:
  - `UIManager`;
  - панель `Actions`;
  - интерактивные кнопки игрового интерфейса;
  - обновление видимости и доступности GUI-элементов;
  - маршрутизацию GUI-событий обратно в `DurakApp`;
  - подключение модальных окон.

- [durak_app/modals.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/modals.py)  
  Сборщик модальных окон на `pygame_gui`. Здесь больше нет ручной отрисовки модалок через `pygame.draw`.  
  Модуль собирает:
  - стартовое модальное окно;
  - финальное модальное окно;
  - панели, подписи, статистику и кнопки.

- [durak_app/ui.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/ui.py)  
  Низкоуровневые UI-утилиты старого слоя. На текущем этапе здесь особенно важна анимация карт.

## 5. Текущая модель GUI

На данном этапе проект использует смешанную, но уже стабилизированную модель интерфейса:

- `pygame` отвечает за:
  - игровой стол;
  - карты;
  - анимации карт;
  - декоративную часть меню.

- `pygame_gui` отвечает за:
  - все интерактивные GUI-элементы;
  - панель `Actions`;
  - кнопки модальных окон;
  - интерактивность главного меню;
  - общую систему GUI-событий.

Это означает, что интерактивные элементы проекта приведены к одной системе обработки событий, даже если часть визуальной отрисовки ещё остаётся на чистом `pygame`.

## 6. Постоянная конфигурация

- [app_config.json](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/app_config.json)

`app_config.json` хранит постоянную конфигурацию приложения, которая не относится к состоянию конкретной игровой партии.

Сейчас в нём хранятся:

- визуальные настройки;
- параметры матча по умолчанию;
- layout-дельты для редактируемых UI-блоков.

Этот файл является основой для отладочных layout-инструментов и будущей автоматизации настройки интерфейса.

## 7. Тема `pygame_gui`

- [ui_theme/theme.json](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/ui_theme/theme.json)

Файл темы определяет внешний вид элементов `pygame_gui`:

- панелей;
- кнопок;
- текстовых элементов;
- модальных окон;
- невидимых hotspot-кнопок, которые используются для интерактивности меню.

## 8. Инструменты разработки

- [tools/layout_debug_tool.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/tools/layout_debug_tool.py)  
  Отдельная графическая утилита для настройки layout-блоков через изменение `delta_x` и `delta_y` в `app_config.json`.

- [tools/card_image_resize_tool](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/tools/card_image_resize_tool)  
  Утилиты для подготовки и изменения размеров карточных изображений.

- [tools/frame_tool](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/tools/frame_tool)  
  Вспомогательные инструменты для генерации карточных рамок и подготовки ассетов колод.

## 9. Распределение ответственности

На текущем этапе целевая ответственность модулей выглядит так:

- `card_engine` владеет правилами игры;
- `game_table.py` владеет отрисовкой игрового стола;
- `menu.py` владеет экраном меню;
- `modals.py` владеет сборкой модальных окон;
- `gui_layer.py` владеет жизненным циклом `pygame_gui` и обработкой GUI-событий;
- `app.py` владеет переходами состояний и общей оркестрацией приложения.

## 10. Рекомендуемый порядок чтения проекта

Если нужно быстро снова войти в кодовую базу, лучше читать файлы в таком порядке:

1. [main.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/main.py)
2. [durak_app/app.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/app.py)
3. [card_engine/durak_state.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/card_engine/durak_state.py)
4. [durak_app/game_table.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/game_table.py)
5. [durak_app/gui_layer.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/gui_layer.py)
6. [durak_app/menu.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/menu.py)
7. [durak_app/modals.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/modals.py)
8. [durak_app/config.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/config.py)
9. [tools/layout_debug_tool.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/tools/layout_debug_tool.py)
