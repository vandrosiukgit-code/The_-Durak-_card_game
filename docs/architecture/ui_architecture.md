# Архитектура интерфейса

Этот документ описывает текущую финальную схему интерфейсного слоя проекта `Durak`.

## 1. Общий принцип

Интерфейс проекта разделён на два уровня:

- `pygame` отвечает за игровую сцену;
- `pygame_gui` отвечает за интерфейсные элементы.

На практике это означает следующее:

- через `pygame` рисуются сукно, зоны игроков, карты, колода, козырь, портреты и анимации карт;
- через `pygame_gui` работают панели, кнопки, текстовые подписи, служебные строки, модальные окна и главное меню.

Такое разделение считается постоянной архитектурой проекта.

## 2. Что остаётся в `pygame`

`pygame` используется только для визуального слоя игровой сцены:

- фон и стол;
- панели игроков как часть сцены;
- руки игроков;
- карты на столе;
- колода и козырь;
- портреты;
- анимации полёта карт.

Эти элементы не являются GUI-компонентами и не должны переводиться на `pygame_gui`.

## 3. Что переведено на `pygame_gui`

На `pygame_gui` переведены все интерфейсные элементы проекта:

- панель `Actions`;
- кнопки `Pass`, `Take`, `Restart`, `Surrender`;
- заголовок и служебные строки игрового стола;
- подписи игроков;
- счётчики поражений;
- стартовое модальное окно;
- финальное модальное окно;
- главное меню;
- overlay, dropdown и вспомогательные панели меню.

Это значит, что интерактивный и текстовый интерфейс теперь живёт в одной системе.

## 4. Ответственность основных модулей

### [durak_app/app.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/app.py)

Главный координатор приложения.

Отвечает за:

- запуск окна `pygame`;
- создание экранов и GUI-слоя;
- главный цикл `process_events -> update -> draw`;
- переключение между меню, игрой и модальными окнами;
- передачу данных в UI-модули.

### [durak_app/game_table.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/game_table.py)

Отвечает только за игровую сцену.

Содержит:

- сукно;
- панели игроков;
- карты;
- колоду и козырь;
- портреты;
- геометрию сценических layout-блоков.

Этот модуль больше не владеет текстовыми интерфейсными элементами и не содержит старых ручных игровых кнопок.

### [durak_app/gui_layer.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/gui_layer.py)

Центральный владелец `pygame_gui` в игровом режиме.

Отвечает за:

- `UIManager`;
- панель `Actions`;
- игровые кнопки;
- заголовок и служебные строки стола;
- подписи игроков;
- счёт поражений;
- обновление видимости и доступности GUI;
- маршрутизацию GUI-событий обратно в `DurakApp`.

Именно здесь теперь живут все интерфейсные элементы игрового экрана.

### [durak_app/ui.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/ui.py)

Содержит низкоуровневые утилиты анимации.

На текущем этапе в этом модуле сознательно оставлен только `CardAnimation`. Старый ручной кнопочный слой удалён как устаревший.

### [durak_app/menu.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/menu.py)

Отвечает за главное меню.

Меню собрано из `pygame_gui`-элементов:

- `UIPanel`;
- `UILabel`;
- `UIButton`;
- `UIImage`.

`pygame` в меню используется только как фон экрана.

### [durak_app/modals.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/modals.py)

Отвечает за модальные окна.

Модалки целиком собраны на `pygame_gui`:

- overlay;
- panel;
- labels;
- кнопки действий;
- блоки статистики.

`modals.py` больше не рисует модальные окна вручную через `pygame.draw`.

## 5. Обработка событий

Для интерфейса используется единая модель:

- события GUI проходят через `UIManager`;
- кнопки обрабатываются через `pygame_gui.UI_BUTTON_PRESSED`;
- игровые клики по картам остаются отдельной веткой логики и обрабатываются только если курсор не попал в GUI.

Это даёт единый центр интерактивности и упрощает поддержку проекта.

## 6. Layout и постоянная конфигурация

### [durak_app/config.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/config.py)

`AppConfig` отвечает за постоянную конфигурацию интерфейса:

- загрузку;
- сохранение;
- синхронизацию схем layout-блоков.

### [app_config.json](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/app_config.json)

Файл хранит:

- визуальные настройки;
- значения по умолчанию для новых матчей;
- layout-дельты интерфейсных объектов.

Для layout используются:

- `delta_x`
- `delta_y`
- `width_delta`
- `height_delta`
- `todo_text`

Это основа для тонкой настройки интерфейса и для внешней отладочной утилиты.

## 7. Layout Debug Tool

### [tools/layout_debug_tool.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/tools/layout_debug_tool.py)

Это отдельная утилита разработки, а не часть пользовательского интерфейса игры.

Она должна работать с текущей архитектурой так:

- игровые сцены и модалки показываются как превью;
- поверх них выбираются layout-объекты;
- меняются положение и размеры объектов;
- изменения сохраняются в `app_config.json`.

Поскольку интерфейсные элементы собраны в `pygame_gui`, а сцена отделена в `game_table.py`, отладчик можно строить поверх стабильной архитектуры.

## 8. Рекомендуемый порядок чтения UI-слоя

Если нужно быстро понять только интерфейсную часть проекта, удобнее читать файлы в таком порядке:

1. [durak_app/app.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/app.py)
2. [durak_app/gui_layer.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/gui_layer.py)
3. [durak_app/menu.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/menu.py)
4. [durak_app/modals.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/modals.py)
5. [durak_app/game_table.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/game_table.py)
6. [durak_app/config.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/config.py)
7. [tools/layout_debug_tool.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/tools/layout_debug_tool.py)
