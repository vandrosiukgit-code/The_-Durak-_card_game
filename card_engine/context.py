from __future__ import annotations

from dataclasses import dataclass

from .cards import Suit


@dataclass
class GameContext:
    trump_suit: Suit | None = None
