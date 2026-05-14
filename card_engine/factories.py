from __future__ import annotations

from abc import ABC, abstractmethod

from .cards import Card, StandardCard, Suit


class DeckFactory(ABC):
    @abstractmethod
    def create_cards(self) -> list[Card]:
        raise NotImplementedError


class Standard52DeckFactory(DeckFactory):
    RANKS = [
        ("2", 2),
        ("3", 3),
        ("4", 4),
        ("5", 5),
        ("6", 6),
        ("7", 7),
        ("8", 8),
        ("9", 9),
        ("10", 10),
        ("J", 11),
        ("Q", 12),
        ("K", 13),
        ("A", 14),
    ]

    def create_cards(self) -> list[Card]:
        return [
            StandardCard(suit, rank_label, rank_value)
            for suit in Suit
            for rank_label, rank_value in self.RANKS
        ]


class Standard36DeckFactory(DeckFactory):
    MIN_RANK_VALUE = 6

    def create_cards(self) -> list[Card]:
        full_deck = Standard52DeckFactory().create_cards()
        return [card for card in full_deck if card.rank_value >= self.MIN_RANK_VALUE]
