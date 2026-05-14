# High Card on Pygame

Small training project: player and computer draw one card each, and the higher card wins the round.

## Project structure

- `main.py` - playable Pygame prototype
- `card_engine/cards.py` - abstract card contract and standard card
- `card_engine/factories.py` - factories for 36-card and 52-card decks
- `card_engine/deck.py` - deck operations
- `card_engine/hand.py` - player hand model
- `card_engine/context.py` - game context, for example trump suit

## How to run

1. Open the folder in PyCharm.
2. Select your project interpreter.
3. Install `pygame` in the PyCharm terminal:

```bash
pip install pygame
```

4. Run `main.py`.

## How to update the project in PyCharm

1. In the Project panel, right-click the root folder and choose `Reload from Disk` if new files do not appear.
2. Open `main.py` and run it.
3. Explore the `card_engine` package and use it as the base for new card games.

## Ideas for the next step

- move game logic from `main.py` into a separate game module
- add Russian names for suits and ranks
- load front and back images through an asset manager
- add a second game mode based on the same deck engine
