from __future__ import annotations

import random
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Optional


class Arcana(Enum):
    MAJOR = "Major Arcana"
    MINOR = "Minor Arcana"


class Suit(Enum):
    WANDS      = "Wands"
    CUPS       = "Cups"
    SWORDS     = "Swords"
    PENTACLES  = "Pentacles"


@dataclass
class TarotCard:
    name: str
    arcana: Arcana

    keywords: list[str] = field(default_factory=list)
    light: list[str] = field(default_factory=list)
    shadow: list[str] = field(default_factory=list)
    fortune_telling: list[str] = field(default_factory=list)

    suit: Optional[Suit] = None
    rank: Optional[str] = None
    number: Optional[int] = None

    reversed: bool = False

    @property
    def meaning_upright(self) -> str:
        return "; ".join(self.light)

    @property
    def meaning_reversed(self) -> str:
        return "; ".join(self.shadow)

    def meaning(self) -> str:
        return self.meaning_reversed if self.reversed else self.meaning_upright

    def display(self) -> str:
        orientation = "Reversed" if self.reversed else "Upright"
        if self.arcana == Arcana.MAJOR:
            return f"{self.name} ({self.number}) - {orientation}"
        return f"{self.rank} of {self.suit.value} - {orientation}"


# Cards that read as "No" even when upright. Reversal flips the verdict.
_NEGATIVE_MAJORS = {"The Tower", "The Devil", "Death", "The Hanged Man", "The Moon"}
_NEGATIVE_MINORS_UPRIGHT = {
    ("Swords", "Three"), ("Swords", "Five"), ("Swords", "Eight"),
    ("Swords", "Nine"), ("Swords", "Ten"),
    ("Cups", "Five"), ("Cups", "Eight"),
    ("Pentacles", "Five"),
    ("Wands", "Five"), ("Wands", "Ten"),
}


def is_yes(card: TarotCard) -> bool:
    if card.arcana == Arcana.MAJOR:
        base_yes = card.name not in _NEGATIVE_MAJORS
    else:
        base_yes = (card.suit.value, card.rank) not in _NEGATIVE_MINORS_UPRIGHT
    return base_yes if not card.reversed else not base_yes


class Deck:
    def __init__(self, cards: list[TarotCard], reversal_chance: float = 0.5):
        self._template = cards
        self.reversal_chance = reversal_chance
        self.cards: list[TarotCard] = []
        self.reset()

    def reset(self) -> None:
        self.cards = [replace(c, reversed=False) for c in self._template]

    def shuffle(self, rng: Optional[random.Random] = None) -> None:
        (rng or random).shuffle(self.cards)

    def draw(self, n: int = 1, rng: Optional[random.Random] = None) -> list[TarotCard]:
        if n > len(self.cards):
            raise ValueError(f"Only {len(self.cards)} cards left in deck")
        r = rng or random
        drawn = [self.cards.pop() for _ in range(n)]
        for c in drawn:
            c.reversed = r.random() < self.reversal_chance
        return drawn


@dataclass
class Reading:
    spread: str
    positions: list[tuple[str, TarotCard]]
    verdict: Optional[str] = None

    def display(self) -> str:
        header = f"=== {self.spread} ==="
        if self.verdict:
            header += f"  -> {self.verdict}"
        lines = [header]
        for pos, card in self.positions:
            lines.append(f"[{pos}] {card.display()}")
            lines.append(f"    {card.meaning()}")
        return "\n".join(lines)


def _fresh(deck: Deck, rng: Optional[random.Random]) -> None:
    deck.reset()
    deck.shuffle(rng)


def three_card_spread(deck: Deck, rng: Optional[random.Random] = None) -> Reading:
    _fresh(deck, rng)
    cards = deck.draw(3, rng)
    return Reading(
        spread="Past / Present / Future",
        positions=list(zip(["Past", "Present", "Future"], cards)),
    )


def yes_no_spread(deck: Deck, rng: Optional[random.Random] = None) -> Reading:
    _fresh(deck, rng)
    [card] = deck.draw(1, rng)
    return Reading(
        spread="Yes / No",
        positions=[("Answer", card)],
        verdict="Yes" if is_yes(card) else "No",
    )


def season_spread(deck: Deck, rng: Optional[random.Random] = None) -> Reading:
    _fresh(deck, rng)
    cards = deck.draw(4, rng)
    return Reading(
        spread="Four Seasons",
        positions=list(zip(["Spring", "Summer", "Autumn", "Winter"], cards)),
    )


_CROSS_POSITIONS = [
    "Present",
    "Challenge",
    "Foundation",
    "Recent Past",
    "Crown",
    "Near Future",
    "Self",
    "Environment",
    "Hopes & Fears",
    "Outcome",
]


def cross_spread(deck: Deck, rng: Optional[random.Random] = None) -> Reading:
    _fresh(deck, rng)
    cards = deck.draw(10, rng)
    return Reading(
        spread="Celtic Cross",
        positions=list(zip(_CROSS_POSITIONS, cards)),
    )


def build_deck(reversal_chance: float = 0.5) -> Deck:
    from tarot_data import ALL_CARDS
    return Deck(ALL_CARDS, reversal_chance=reversal_chance)


if __name__ == "__main__":
    # Without this, `from tarot import ...` inside tarot_data.py would load
    # this file a second time under the name "tarot", giving us two distinct
    # Arcana/Suit enum classes and breaking identity comparisons in is_yes.
    import sys
    sys.modules.setdefault("tarot", sys.modules[__name__])

    deck = build_deck()
    rng = random.Random()
    for spread in (three_card_spread, yes_no_spread, season_spread, cross_spread):
        print(spread(deck, rng).display())
        print()
