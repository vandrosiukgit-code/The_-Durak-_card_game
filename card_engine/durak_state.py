from __future__ import annotations

import random
from dataclasses import dataclass, field

from .cards import Card, Suit
from .deck import Deck
from .factories import Standard36DeckFactory
from .hand import Hand


SEAT_ORDER = ("bottom", "left", "top", "right")
MAX_TABLE_ATTACKS = 6


@dataclass
class TableAttack:
    attack_card: Card
    defense_card: Card | None = None


@dataclass
class DurakGameState:
    deck: Deck
    hands: dict[str, Hand]
    trump_card: Card
    trump_suit: Suit
    attacker_seat: str
    defender_seat: str
    current_actor: str
    phase: str = "attack"
    table_attacks: list[TableAttack] = field(default_factory=list)
    discard_count: int = 0
    turn_number: int = 1
    last_result: str = "Deal complete."
    cards_per_player: int = 6
    bout_attacker: str = "bottom"
    defender_start_hand_size: int = 6
    defender_taking: bool = False
    consecutive_passes: int = 0
    winner_seats: list[str] = field(default_factory=list)
    loser_seat: str | None = None
    recent_deck_draws: dict[str, list[Card]] = field(default_factory=dict)

    @classmethod
    def new_game(cls, cards_per_player: int = 6, opening_mode: str = "classic") -> "DurakGameState":
        deck = Deck.from_factory(Standard36DeckFactory())
        deck.shuffle()

        hands = {seat: Hand() for seat in SEAT_ORDER}
        deck.deal_to_hands([hands[seat] for seat in SEAT_ORDER], cards_per_player)

        trump_card = deck.cards[0]
        if opening_mode == "player":
            attacker_seat = "bottom"
        elif opening_mode == "random":
            attacker_seat = random.choice(SEAT_ORDER)
        else:
            attacker_seat = cls._find_first_attacker(hands, trump_card.suit)
        defender_seat = cls._next_seat(attacker_seat)

        return cls(
            deck=deck,
            hands=hands,
            trump_card=trump_card,
            trump_suit=trump_card.suit,
            attacker_seat=attacker_seat,
            defender_seat=defender_seat,
            current_actor=attacker_seat,
            phase="attack",
            cards_per_player=cards_per_player,
            bout_attacker=attacker_seat,
            defender_start_hand_size=len(hands[defender_seat]),
            last_result=f"Trump is {trump_card.suit.label}. {attacker_seat.title()} attacks first.",
            recent_deck_draws={seat: [] for seat in SEAT_ORDER},
        )

    @staticmethod
    def _next_seat(seat: str) -> str:
        index = SEAT_ORDER.index(seat)
        return SEAT_ORDER[(index + 1) % len(SEAT_ORDER)]

    @staticmethod
    def _find_first_attacker(hands: dict[str, Hand], trump_suit: Suit) -> str:
        best_seat = SEAT_ORDER[0]
        best_card: Card | None = None

        for seat in SEAT_ORDER:
            for card in hands[seat].cards:
                if card.suit != trump_suit:
                    continue
                if best_card is None or card.rank_value < best_card.rank_value:
                    best_card = card
                    best_seat = seat

        return best_seat

    def hand_for(self, seat: str) -> Hand:
        return self.hands[seat]

    def hand_size(self, seat: str) -> int:
        return len(self.hands[seat])

    def deck_size(self) -> int:
        return self.deck.cards_left()

    def is_game_over(self) -> bool:
        return self.phase == "game_over"

    def is_player_turn(self) -> bool:
        return self.current_actor == "bottom" and not self.is_game_over()

    def deck_trump_visible(self) -> Card:
        return self.trump_card

    def ranks_on_table(self) -> set[str]:
        ranks: set[str] = set()
        for pair in self.table_attacks:
            ranks.add(pair.attack_card.rank_label)
            if pair.defense_card is not None:
                ranks.add(pair.defense_card.rank_label)
        return ranks

    def table_card_count(self) -> int:
        return len(self.table_attacks)

    def max_attacks_for_bout(self) -> int:
        return min(MAX_TABLE_ATTACKS, self.defender_start_hand_size)

    def unresolved_attack(self) -> TableAttack | None:
        for pair in self.table_attacks:
            if pair.defense_card is None:
                return pair
        return None

    def can_beat(self, attack_card: Card, defense_card: Card) -> bool:
        if defense_card.suit == attack_card.suit and defense_card.rank_value > attack_card.rank_value:
            return True
        if defense_card.suit == self.trump_suit and attack_card.suit != self.trump_suit:
            return True
        return False

    def can_attack_with(self, seat: str, card: Card) -> bool:
        if self.is_game_over():
            return False
        if seat != self.current_actor:
            return False
        if self.phase not in {"attack", "toss", "toss_after_take"}:
            return False
        if seat == self.defender_seat:
            return False
        if card not in self.hands[seat].cards:
            return False
        if self.table_card_count() >= self.max_attacks_for_bout():
            return False
        if not self.table_attacks:
            return self.phase == "attack"
        return card.rank_label in self.ranks_on_table()

    def can_defend_with(self, card: Card) -> bool:
        if self.is_game_over():
            return False
        if self.phase != "defend" or self.current_actor != self.defender_seat:
            return False
        if card not in self.hands[self.defender_seat].cards:
            return False
        attack = self.unresolved_attack()
        if attack is None:
            return False
        return self.can_beat(attack.attack_card, card)

    def available_actions_for_player(self) -> dict[str, bool]:
        can_pass = self.phase in {"toss", "toss_after_take"} and self.current_actor == "bottom"
        can_take = self.phase == "defend" and self.current_actor == "bottom"
        return {
            "pass": can_pass,
            "take": can_take,
        }

    def play_attack_card(self, seat: str, card: Card) -> bool:
        if not self.can_attack_with(seat, card):
            return False

        self.hands[seat].remove_card(card)
        self.table_attacks.append(TableAttack(attack_card=card))
        self.consecutive_passes = 0

        if self.defender_taking:
            self.last_result = f"{seat.title()} tosses in {card.short_name}."
            next_actor = self._next_tosser(seat)
            if next_actor is None:
                self._resolve_take()
            else:
                self.phase = "toss_after_take"
                self.current_actor = next_actor
                if self.table_card_count() >= self.max_attacks_for_bout():
                    self._resolve_take()
            return True

        self.phase = "defend"
        self.current_actor = self.defender_seat
        self.last_result = f"{seat.title()} attacks with {card.short_name}."
        return True

    def play_defense_card(self, card: Card) -> bool:
        if not self.can_defend_with(card):
            return False

        attack = self.unresolved_attack()
        assert attack is not None

        self.hands[self.defender_seat].remove_card(card)
        attack.defense_card = card

        if self.table_card_count() >= self.max_attacks_for_bout():
            self._resolve_successful_defense()
            return True

        self.phase = "toss"
        self.current_actor = self.bout_attacker
        self.consecutive_passes = 0
        self.last_result = f"{self.defender_seat.title()} defends with {card.short_name}."
        return True

    def player_take(self) -> bool:
        if self.phase != "defend" or self.current_actor != "bottom":
            return False
        self._start_take()
        return True

    def pass_action(self, seat: str) -> bool:
        if self.phase not in {"toss", "toss_after_take"} or seat != self.current_actor:
            return False

        self.consecutive_passes += 1
        tossers = self._tossers()
        self.last_result = f"{seat.title()} passes."

        if not tossers or self.consecutive_passes >= len(tossers) or self.table_card_count() >= self.max_attacks_for_bout():
            if self.defender_taking:
                self._resolve_take()
            else:
                self._resolve_successful_defense()
            return True

        next_actor = self._next_tosser(seat)
        if next_actor is None:
            if self.defender_taking:
                self._resolve_take()
            else:
                self._resolve_successful_defense()
            return True

        self.current_actor = next_actor
        return True

    def auto_step(self) -> bool:
        if self.is_game_over():
            return False
        if self.current_actor == "bottom":
            return False

        if self.phase == "attack":
            card = self._choose_attack_card(self.current_actor)
            if card is None:
                self._mark_finished_and_check_game_over()
                return False
            return self.play_attack_card(self.current_actor, card)

        if self.phase == "defend":
            card = self._choose_defense_card(self.defender_seat)
            if card is None:
                self._start_take()
                return True
            return self.play_defense_card(card)

        if self.phase in {"toss", "toss_after_take"}:
            card = self._choose_toss_card(self.current_actor)
            if card is None:
                return self.pass_action(self.current_actor)
            return self.play_attack_card(self.current_actor, card)

        return False

    def _start_take(self) -> None:
        self._clear_recent_draws()
        self.defender_taking = True
        self.phase = "toss_after_take"
        self.current_actor = self.bout_attacker
        self.consecutive_passes = 0
        self.last_result = f"{self.defender_seat.title()} takes the cards."

    def _resolve_successful_defense(self) -> None:
        self._clear_recent_draws()
        cards_to_discard: list[Card] = []
        for pair in self.table_attacks:
            cards_to_discard.append(pair.attack_card)
            if pair.defense_card is not None:
                cards_to_discard.append(pair.defense_card)

        self.deck.discard_many(cards_to_discard)
        self.discard_count += len(cards_to_discard)
        defender = self.defender_seat
        self.last_result = f"{defender.title()} beats the attack and moves first next."
        self._refill_hands(self.bout_attacker)
        self._clear_table()

        self.attacker_seat = self._seat_or_next_with_cards(defender)
        self.defender_seat = self._next_seat_with_cards(self.attacker_seat)
        self._start_new_bout(self.attacker_seat, self.defender_seat)
        self.turn_number += 1

        self._mark_finished_and_check_game_over()

    def _resolve_take(self) -> None:
        self._clear_recent_draws()
        for pair in self.table_attacks:
            self.hands[self.defender_seat].add_card(pair.attack_card)
            if pair.defense_card is not None:
                self.hands[self.defender_seat].add_card(pair.defense_card)

        next_attacker = self._next_seat_with_cards(self.defender_seat)
        if next_attacker == self.defender_seat:
            next_attacker = self._next_seat(self.defender_seat)

        self.last_result = f"{self.defender_seat.title()} takes the pile. {next_attacker.title()} attacks next."
        self._refill_hands(self.bout_attacker)
        self._clear_table()

        self.attacker_seat = next_attacker
        self.defender_seat = self._next_seat_with_cards(self.attacker_seat)
        self._start_new_bout(self.attacker_seat, self.defender_seat)
        self.turn_number += 1

        self._mark_finished_and_check_game_over()

    def _clear_table(self) -> None:
        self.table_attacks.clear()
        self.defender_taking = False
        self.consecutive_passes = 0

    def _refill_hands(self, start_seat: str) -> None:
        seat = start_seat
        for _ in range(len(SEAT_ORDER)):
            hand = self.hands[seat]
            needed = max(0, self.cards_per_player - len(hand))
            drawn_cards = self.deck.draw_many(needed)
            self.recent_deck_draws[seat].extend(drawn_cards)
            for card in drawn_cards:
                hand.add_card(card)
            seat = self._next_seat(seat)

    def _clear_recent_draws(self) -> None:
        for seat in SEAT_ORDER:
            self.recent_deck_draws[seat] = []

    def _next_seat_with_cards(self, seat: str) -> str:
        current = seat
        for _ in range(len(SEAT_ORDER)):
            current = self._next_seat(current)
            if len(self.hands[current]) > 0:
                return current
        return seat

    def _seat_or_next_with_cards(self, seat: str) -> str:
        if len(self.hands[seat]) > 0:
            return seat
        return self._next_seat_with_cards(seat)

    def _start_new_bout(self, attacker: str, defender: str) -> None:
        self.attacker_seat = attacker
        self.defender_seat = defender
        self.bout_attacker = attacker
        self.current_actor = attacker
        self.phase = "attack"
        self.defender_start_hand_size = len(self.hands[defender])

    def _choose_attack_card(self, seat: str) -> Card | None:
        cards = [card for card in self.hands[seat].cards if self.can_attack_with(seat, card)]
        if not cards:
            return None
        return min(cards, key=self._attack_sort_key)

    def _choose_defense_card(self, seat: str) -> Card | None:
        attack = self.unresolved_attack()
        if attack is None:
            return None
        candidates = [card for card in self.hands[seat].cards if self.can_beat(attack.attack_card, card)]
        if not candidates:
            return None
        return min(candidates, key=self._defense_sort_key)

    def _choose_toss_card(self, seat: str) -> Card | None:
        cards = [card for card in self.hands[seat].cards if self.can_attack_with(seat, card)]
        if not cards:
            return None
        return min(cards, key=self._attack_sort_key)

    def _attack_sort_key(self, card: Card) -> tuple[int, int]:
        is_trump = 1 if card.suit == self.trump_suit else 0
        return (is_trump, card.rank_value)

    def _defense_sort_key(self, card: Card) -> tuple[int, int, int]:
        attack = self.unresolved_attack()
        same_suit = 0 if attack is not None and card.suit == attack.attack_card.suit else 1
        is_trump = 1 if card.suit == self.trump_suit else 0
        return (same_suit, is_trump, card.rank_value)

    def _tossers(self) -> list[str]:
        tossers: list[str] = []
        seat = self.bout_attacker
        for _ in range(len(SEAT_ORDER)):
            if seat != self.defender_seat and len(self.hands[seat]) > 0:
                tossers.append(seat)
            seat = self._next_seat(seat)
        return tossers

    def _next_tosser(self, seat: str) -> str | None:
        tossers = self._tossers()
        if not tossers:
            return None
        if seat not in tossers:
            return tossers[0]
        index = tossers.index(seat)
        return tossers[(index + 1) % len(tossers)]

    def _mark_finished_and_check_game_over(self) -> None:
        if self.deck_size() > 0:
            return

        self.winner_seats = [seat for seat in SEAT_ORDER if len(self.hands[seat]) == 0]
        losers = [seat for seat in SEAT_ORDER if len(self.hands[seat]) > 0]

        if len(losers) <= 1:
            self.phase = "game_over"
            self.current_actor = "bottom"
            self.loser_seat = losers[0] if losers else None
            if self.loser_seat is None:
                self.last_result = "Draw game. Everyone got rid of their cards."
            else:
                self.last_result = f"{self.loser_seat.title()} is the durak."
