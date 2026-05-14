from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto


class Suit(Enum):
    HEARTS = ("Hearts", "H")
    DIAMONDS = ("Diamonds", "D")
    CLUBS = ("Clubs", "C")
    SPADES = ("Spades", "S")

    @property
    def label(self) -> str:
        return self.value[0]

    @property
    def short_label(self) -> str:
        return self.value[1]


class CardStatus(Enum):
    NORMAL = auto()
    TRUMP = auto()
    SPECIAL = auto()


class Card(ABC):
    @property
    @abstractmethod
    def suit(self) -> Suit | None:
        raise NotImplementedError

    @property
    @abstractmethod
    def rank_label(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def rank_value(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def image_key(self) -> str:
        raise NotImplementedError

    @property
    def display_name(self) -> str:
        if self.suit is None:
            return self.rank_label
        return f"{self.rank_label} of {self.suit.label}"

    @property
    def short_name(self) -> str:
        if self.suit is None:
            return self.rank_label
        return f"{self.rank_label}{self.suit.short_label}"

    def get_status(self, context: "GameContext") -> CardStatus:
        if self.suit is not None and context.trump_suit == self.suit:
            return CardStatus.TRUMP
        return CardStatus.NORMAL


@dataclass(frozen=True)
class StandardCard(Card):
    _suit: Suit
    _rank_label: str
    _rank_value: int

    @property
    def suit(self) -> Suit:
        return self._suit

    @property
    def rank_label(self) -> str:
        return self._rank_label

    @property
    def rank_value(self) -> int:
        return self._rank_value

    @property
    def image_key(self) -> str:
        return f"{self.rank_label.lower()}_of_{self.suit.label.lower()}"


from .context import GameContext
