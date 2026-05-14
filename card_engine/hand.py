from __future__ import annotations

from dataclasses import dataclass, field

from .cards import Card


@dataclass
class Hand:
    cards: list[Card] = field(default_factory=list)

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    def remove_card(self, card: Card) -> None:
        self.cards.remove(card)

    def clear(self) -> None:
        self.cards.clear()

    def __len__(self) -> int:
        return len(self.cards)

    def is_empty(self) -> bool:
        return not self.cards
