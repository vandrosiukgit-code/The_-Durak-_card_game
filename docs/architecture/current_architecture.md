# Current Project Architecture

This document gives a short overview of the current architecture of the project.

## 1. Entry Point

- [main.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/main.py)

`main.py` is intentionally small. It only creates `DurakApp` and starts the main loop.

## 2. Main Layers

The project is currently split into three main layers:

1. `card_engine` - game rules and domain logic
2. `durak_app` - application layer, rendering, UI, configuration
3. `tools` - development utilities

## 3. Game Logic Layer: `card_engine`

- [card_engine/cards.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/card_engine/cards.py)  
  Card models, suits, ranks, and standard playing card structures.

- [card_engine/hand.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/card_engine/hand.py)  
  Player hand container and operations on cards in hand.

- [card_engine/deck.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/card_engine/deck.py)  
  Live deck object: shuffle, draw, deal, discard, refill.

- [card_engine/factories.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/card_engine/factories.py)  
  Factories for standard decks, including the 36-card deck used by Durak.

- [card_engine/durak_state.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/card_engine/durak_state.py)  
  Core Durak rules. This is the main gameplay state machine:
  - new game creation
  - trump setup
  - attack / defend / toss phases
  - bot auto-steps
  - draw logic
  - game over detection

## 4. Application Layer: `durak_app`

- [durak_app/app.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/app.py)  
  Main application controller. It connects game logic, rendering, animation, UI, and persistent configuration.

- [durak_app/config.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/config.py)  
  Shared constants plus persistent app configuration support through `AppConfig`.

- [durak_app/game_table.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/game_table.py)  
  Pure game-table rendering:
  - felt/table background
  - player zones
  - cards on table
  - deck and trump card
  - layout block definitions for debug tooling

- [durak_app/menu.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/menu.py)  
  Main menu screen. Handles match setup and visual customization.

- [durak_app/menu_support.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/menu_support.py)  
  Helper classes for menu rendering, including asset loading and square-grid layout support.

- [durak_app/gui_layer.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/gui_layer.py)  
  Central `pygame_gui` integration layer:
  - owns `UIManager`
  - handles action buttons
  - updates GUI visibility and enabled states
  - routes GUI button events back into `DurakApp`

- [durak_app/modals.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/modals.py)  
  Modal builder for `pygame_gui`. It assembles intro and endgame windows from panels, labels, and buttons.

- [durak_app/ui.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/ui.py)  
  Low-level UI helpers that are still used, mainly card animation.

## 5. Persistent Configuration

- [app_config.json](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/app_config.json)

Persistent app configuration is separated from temporary in-game state.

It currently stores:

- visual settings
- default match settings
- layout deltas for editable UI blocks

This file is the foundation for layout tooling and future editor-style utilities.

## 6. GUI Theme

- [ui_theme/theme.json](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/ui_theme/theme.json)

This file defines the `pygame_gui` visual theme:

- panel styling
- modal styling
- button styling
- label styling

## 7. Development Tools

- [tools/layout_debug_tool.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/tools/layout_debug_tool.py)  
  Standalone utility for moving base UI blocks by editing layout deltas in `app_config.json`.

- `tools/card_image_resize_tool`  
  Image resizing utility for card assets.

- `tools/frame_tool`  
  Asset generation helpers for card frames and deck production workflows.

## 8. Current UI Architecture

The UI is currently in a hybrid but stabilizing state:

- game table and cards are rendered with raw `pygame`
- interactive GUI elements are moving into `pygame_gui`
- modals are now assembled as `pygame_gui` components

Target direction:

- `card_engine` owns rules
- `game_table.py` owns table rendering
- `menu.py` owns menu rendering
- `modals.py` owns modal construction
- `gui_layer.py` owns GUI lifecycle and event routing
- `app.py` owns state transitions and orchestration

## 9. Recommended Reading Order

If you need to re-enter the project quickly, read files in this order:

1. [main.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/main.py)
2. [durak_app/app.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/app.py)
3. [card_engine/durak_state.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/card_engine/durak_state.py)
4. [durak_app/game_table.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/game_table.py)
5. [durak_app/menu.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/menu.py)
6. [durak_app/config.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/durak_app/config.py)
7. [tools/layout_debug_tool.py](C:/Users/Zver/Documents/Codex/2026-04-26/pygame-python/tools/layout_debug_tool.py)
