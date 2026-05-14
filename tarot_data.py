# Card meanings sourced from dariusk/corpora (CC0 collection), with the underlying
# text by Mark McElroy in "A Guide to Tarot Meanings" (madebymark.com).
# Vendored at data/tarot_interpretations.json.
# DAta source: https://raw.githubusercontent.com/dariusk/corpora/master/data/divination/tarot_interpretations.json


import json
from pathlib import Path

from tarot import Arcana, Suit, TarotCard


_DATASET_PATH = Path(__file__).parent / "data" / "tarot_interpretations.json"

_SUIT_MAP = {
    "wands": Suit.WANDS,
    "cups": Suit.CUPS,
    "swords": Suit.SWORDS,
    "coins": Suit.PENTACLES,
}

_INT_TO_RANK = {
    1: "Ace", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
    6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten",
}


def _normalize_rank(raw_rank) -> str:
    if isinstance(raw_rank, int):
        return _INT_TO_RANK[raw_rank]
    return raw_rank.capitalize()


def _load_cards() -> list[TarotCard]:
    payload = json.loads(_DATASET_PATH.read_text(encoding="utf-8"))
    cards: list[TarotCard] = []

    for entry in payload["tarot_interpretations"]:
        common = dict(
            keywords=list(entry["keywords"]),
            light=list(entry["meanings"]["light"]),
            shadow=list(entry["meanings"]["shadow"]),
            fortune_telling=list(entry["fortune_telling"]),
        )

        if entry["suit"] == "major":
            cards.append(TarotCard(
                name=entry["name"],
                arcana=Arcana.MAJOR,
                number=int(entry["rank"]),
                **common,
            ))
        else:
            suit = _SUIT_MAP[entry["suit"]]
            rank = _normalize_rank(entry["rank"])
            cards.append(TarotCard(
                name=f"{rank} of {suit.value}",
                arcana=Arcana.MINOR,
                suit=suit,
                rank=rank,
                **common,
            ))

    return cards


ALL_CARDS: list[TarotCard] = _load_cards()
MAJOR_ARCANA: list[TarotCard] = [c for c in ALL_CARDS if c.arcana == Arcana.MAJOR]
MINOR_ARCANA: list[TarotCard] = [c for c in ALL_CARDS if c.arcana == Arcana.MINOR]


assert len(MAJOR_ARCANA) == 22, f"Expected 22 majors, got {len(MAJOR_ARCANA)}"
assert len(MINOR_ARCANA) == 56, f"Expected 56 minors, got {len(MINOR_ARCANA)}"
assert len(ALL_CARDS) == 78, f"Expected 78 cards, got {len(ALL_CARDS)}"
