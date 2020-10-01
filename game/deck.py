import random


SUITS = ["c", "d", "h", "s"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"]


class Card:
    def __init__(self, rank: str, suit: str):
        assert suit in SUITS
        assert rank in RANKS
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return self.rank + self.suit

    def __str__(self):
        return self.rank + self.suit

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))

    def suit_idx(self):
        return SUITS.index(self.suit)

    def rank_idx(self):
        return RANKS.index(self.rank)


def card_to_int(card: Card):
    if card is None:
        return None

    suit_idx = SUITS.index(card.suit)
    rank_idx = RANKS.index(card.rank)
    return suit_idx * len(RANKS) + rank_idx


def int_to_card(card_num: int):
    if card_num is None:
        return None
    
    suit_idx = int(card_num / len(RANKS))
    rank_idx = int(card_num % len(RANKS))
    return Card(rank=RANKS[rank_idx], suit=SUITS[suit_idx])

class Deck:
    def __init__(self, seed=None, cards=None):
        if cards is not None:
            self.cards = cards
        else:
            self.cards = []
            for suit in SUITS:
                for rank in RANKS:
                    self.cards.append(Card(rank, suit))

        if seed is not None:
            random.seed(seed)
        random.shuffle(self.cards)

    def __len__(self):
        return len(self.cards)

    def peek(self, n=1):
        return self.cards[0:n]

    def take(self, n=1):
        n = min(len(self.cards), n)
        taken = self.cards[0:n]
        self.cards = self.cards[n:]
        return taken

    def remove(self, card):
        if card in self.cards:
            self.cards.remove(card)
