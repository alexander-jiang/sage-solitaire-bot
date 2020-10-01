import unittest
from deck import Deck

class TestDeck(unittest.TestCase):
    def test_deck_create(self):
        deck = Deck(seed=123)
        assert len(deck) == 52
        first_card = deck.peek(n=2)[0]
        second_card = deck.peek(n=2)[1]
        third_card = deck.peek(n=3)[2]
        assert len(deck) == 52

        first_take = deck.take(n=1)[0]
        assert first_card == first_take
        assert len(deck) == 51
        assert first_take not in deck.cards
        assert second_card in deck.cards

        deck.remove(first_take)
        assert len(deck) == 51

        second_take = deck.take(n=1)[0]
        assert second_card == second_take
        assert len(deck) == 50
        assert second_take not in deck.cards

        deck.remove(third_card)
        assert len(deck) == 49
        assert third_card not in deck.cards

    def test_deck_take(self):
        deck = Deck(seed=123)
        assert len(deck) == 52

        cards = list(deck.cards)

        take_five = deck.take(n=5)
        assert take_five == cards[:5]

        take_five2 = deck.take(n=5)
        assert take_five2 == cards[5:10]

    def test_deck_random_seed(self):
        deck = Deck(seed=123)
        cards = deck.take(n=3)

        deck2 = Deck(seed=123)
        cards2 = deck2.take(n=3)

        assert cards == cards2


if __name__ == '__main__':
    unittest.main()
