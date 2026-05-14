from __future__ import annotations

import random
from dataclasses import dataclass, field

from .cards import Card
from .factories import DeckFactory
from .hand import Hand


@dataclass
class Deck:
    cards: list[Card] = field(default_factory=list)
    discard_pile: list[Card] = field(default_factory=list)

    @classmethod
    def from_factory(cls, factory: DeckFactory) -> "Deck":
        return cls(cards=factory.create_cards())

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw(self) -> Card | None:
        if not self.cards:
            return None
        return self.cards.pop()

    def draw_many(self, count: int) -> list[Card]:
        if count < 0:
            raise ValueError("count must be non-negative")

        drawn_cards: list[Card] = []
        for _ in range(count):
            card = self.draw()
            if card is None:
                break
            drawn_cards.append(card)
        return drawn_cards

    def deal_to_hands(self, hands: list[Hand], cards_per_hand: int) -> None:
        if cards_per_hand < 0:
            raise ValueError("cards_per_hand must be non-negative")
        if not hands:
            raise ValueError("hands must not be empty")

        for _ in range(cards_per_hand):
            for hand in hands:
                card = self.draw()
                if card is None:
                    return
                hand.add_card(card)

    def discard(self, card: Card) -> None:
        self.discard_pile.append(card)

    def discard_many(self, cards: list[Card]) -> None:
        self.discard_pile.extend(cards)

    def reset_from_factory(self, factory: DeckFactory, shuffle: bool = True) -> None:
        self.cards = factory.create_cards()
        self.discard_pile.clear()
        if shuffle:
            self.shuffle()

    def refill_from_discard(self, shuffle: bool = True) -> None:
        if not self.discard_pile:
            return

        self.cards.extend(self.discard_pile)
        self.discard_pile.clear()
        if shuffle:
            self.shuffle()

    def put_on_top(self, card: Card) -> None:
        self.cards.append(card)

    def put_on_bottom(self, card: Card) -> None:
        self.cards.insert(0, card)

    def cards_left(self) -> int:
        return len(self.cards)

    def discard_size(self) -> int:
        return len(self.discard_pile)

    def is_empty(self) -> bool:
        return not self.cards

    def __len__(self) -> int:
        return len(self.cards)
