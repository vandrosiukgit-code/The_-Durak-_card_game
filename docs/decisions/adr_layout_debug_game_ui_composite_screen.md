# ADR: Layout Debug Tool v2 — composite game_table preview screen

## Статус

Принято и реализовано.

## Контекст

В игровом экране часть видимых элементов относится не к `game_table`, а к отдельному layout-разделу `game_ui`.

Пример:

- `game_ui.title_label` — надпись `Durak`;
- `game_ui.subtitle_label` — подзаголовок;
- `game_ui.attacker_label`;
- `game_ui.meta_label`;
- `game_ui.party_meta_label`.

Пользователь воспринимает эти элементы как часть игрового стола, потому что они видны в `PREVIEW AREA` вместе с `game_table`. Но до этого навигатор объектов работал только с layout-разделом `game_table`, поэтому UI-надписи нельзя было нормально выбрать и редактировать.

## Решение

Для Layout Debug Tool вводится понятие composite preview screen:

```text
preview screen: game_table
layout layers:
  game_table
  game_ui
```

В выпадающем списке экранов остаётся `game_table`.

Внутри навигатора объектов `game_table` отображается как составной экран:

```text
game_table
    table_area
        - deck_panel
        - trump_panel
    player_left_panel
    ...

game_ui
    title_label
    subtitle_label
    attacker_label
    meta_label
    party_meta_label
```

Служебные строки `game_table` и `game_ui` являются group-узлами. Они не являются layout-объектами, не выбираются и не редактируются.

Реальные объекты под ними остаются обычными объектами навигации.

## Модель ключей

У `LayoutObject` есть два разных смысла экрана:

- `screen_id` — preview-экран, в котором объект виден пользователю;
- `layout_screen_id` — реальный раздел `app_config.json`, куда нужно писать изменения;
- `layout_key` — полный ключ вида `game_ui.title_label`.

Для обычных объектов:

```text
screen_id = game_table
layout_screen_id = game_table
layout_key = game_table.deck_panel
```

Для объектов UI-слоя:

```text
screen_id = game_table
layout_screen_id = game_ui
layout_key = game_ui.title_label
```

## Поведение

- Hover в навигаторе подсвечивает объект в `PREVIEW AREA`.
- Hover в `PREVIEW AREA` подсвечивает строку объекта в навигаторе.
- ЛКМ выбирает реальный layout-объект.
- Инспектор редактирует выбранный объект.
- Move/Size-кнопки применяются к реальному `layout_screen_id`.
- `Apply` сохраняет изменения в правильный раздел `app_config.json`.
- `Cancel`, `Dismiss`, `Reset session` работают с реальным `layout_screen_id`.
- TO DO видит задачи из `game_ui` наравне с задачами остальных layout-разделов.

## Последствия

Плюсы:

- Пользователь получает доступ к надписям игрового UI прямо с экрана `game_table`.
- Утилита не смешивает данные при сохранении: `game_ui` остаётся отдельным layout-разделом.
- Навигатор стал ближе к реальной архитектуре отрисовки: игровой стол и UI-слой видны как разные ветки.

Ограничения:

- Group-узлы пока не имеют собственных действий.
- Collapse/expand по-прежнему не вводится.
- Если в будущем появятся новые UI-слои, их нужно подключать как отдельные layout layers внутри composite preview screen.
