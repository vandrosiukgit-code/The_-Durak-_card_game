from __future__ import annotations

from dataclasses import dataclass, field

from .cards import Card
from .deck import Deck
from .factories import DeckFactory, Standard52DeckFactory
from .hand import Hand


SEAT_ORDER = ("bottom", "left", "top", "right")


@dataclass
class GameState:
    deck: Deck
    hands: dict[str, Hand]
    active_seats: tuple[str, str] = ("bottom", "top")
    table_cards: dict[str, Card | None] = field(default_factory=lambda: {"bottom": None, "top": None})
    scores: dict[str, int] = field(default_factory=lambda: {"bottom": 0, "top": 0})
    round_number: int = 0
    cards_per_player: int = 9

    @classmethod
    def new_round_table(
        cls,
        factory: DeckFactory | None = None,
        cards_per_player: int = 9,
        active_seats: tuple[str, str] = ("bottom", "top"),
    ) -> "GameState":
        factory = factory or Standard52DeckFactory()
        deck = Deck.from_factory(factory)
        deck.shuffle()
        hands = {seat: Hand() for seat in SEAT_ORDER}
        deck.deal_to_hands([hands[seat] for seat in SEAT_ORDER], cards_per_player)
        return cls(
            deck=deck,
            hands=hands,
            active_seats=active_seats,
            cards_per_player=cards_per_player,
            table_cards={seat: None for seat in active_seats},
            scores={seat: 0 for seat in active_seats},
        )

    def hand_for(self, seat: str) -> Hand:
        return self.hands[seat]

    def hand_size(self, seat: str) -> int:
        return len(self.hands[seat])

    def play_high_card_round(self) -> tuple[Card | None, Card | None]:
        first_seat, second_seat = self.active_seats
        first_card = self._play_from_hand(first_seat)
        second_card = self._play_from_hand(second_seat)

        self.table_cards[first_seat] = first_card
        self.table_cards[second_seat] = second_card
        self.round_number += 1

        if first_card is None or second_card is None:
            return first_card, second_card

        if first_card.rank_value > second_card.rank_value:
            self.scores[first_seat] += 1
        elif first_card.rank_value < second_card.rank_value:
            self.scores[second_seat] += 1

        return first_card, second_card

    def _play_from_hand(self, seat: str) -> Card | None:
        hand = self.hands[seat]
        if hand.is_empty():
            return None
        return hand.cards.pop()

