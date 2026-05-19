# Layout Debug Tool v2: game_ui composite screen backlog

## Статус

Реализовано и принято пользователем.

## Цель

Сделать UI-надписи игрового экрана доступными в Layout Debug Tool без смешивания layout-разделов.

Проблема: надписи `Durak`, `Classic throw-in Durak` и мета-информация видны в `PREVIEW AREA`, но лежат в `app_config.json` внутри `layout.game_ui`, а не внутри `layout.game_table`.

## Реализованные задачи

### 1. Ввести безопасные layout-ключи

Добавлено различие:

- `screen_id` — preview-экран;
- `layout_screen_id` — реальный layout-раздел;
- `layout_key` — полный ключ объекта.

### 2. Подключить game_ui к preview game_table

Для `game_table` утилита строит композитный список объектов:

- объекты `game_table`;
- объекты `game_ui`.

При этом `game_ui`-объекты сохраняют свой реальный `layout_screen_id = game_ui`.

### 3. Добавить preview-геометрию game_ui

В `PREVIEW AREA` добавлены прямоугольники для:

- `title_label`;
- `subtitle_label`;
- `attacker_label`;
- `meta_label`;
- `party_meta_label`.

### 4. Перевести редактирование на layout_screen_id

Следующие действия используют реальный layout-раздел выбранного объекта:

- инспектор;
- кнопки Move/Size;
- `Dismiss`;
- `Cancel`;
- `Reset session`;
- `Apply`;
- создание TO DO.

### 5. Сгруппировать навигатор

Навигатор `game_table` показывает две служебные ветки:

```text
game_table
    ...

game_ui
    title_label
    subtitle_label
    attacker_label
    meta_label
    party_meta_label
```

Служебные строки `game_table` и `game_ui` не выбираются и не редактируются.

## Проверочный сценарий

1. Открыть `game_table`.
2. Навести курсор на надпись `Durak` в `PREVIEW AREA`.
3. Убедиться, что в навигаторе подсвечивается `game_ui.title_label`.
4. Выбрать `title_label`.
5. Подвинуть объект кнопками управления.
6. Убедиться, что появляется `UNSAVED`.
7. Нажать `Apply`.
8. Убедиться, что изменение сохраняется в `layout.game_ui.title_label`.

## Результат

`game_ui` стал полноценным редактируемым слоем игрового preview-экрана, но архитектурно остался отдельным layout-разделом.
