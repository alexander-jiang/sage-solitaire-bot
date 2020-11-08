import unittest
import numpy as np
from deck import SUITS, RANKS, Card
from gamestate import GameState

class TestHands(unittest.TestCase):
    def test_pair_hands(self):
        state = GameState()
        card_piles = [
            [[Card("2", "s")], [Card("K", "d")], [Card("K", "s")]],
            [[Card("3", "c")], [Card("A", "s")], [Card("6", "c")]],
            [[Card("3", "s")], [Card("A", "c")], [Card("K", "c")]]
        ]
        state.start_new_game(lucky_card=Card("7", "h"), card_piles=card_piles)

        pair_hands = state._get_pair_hands()
        assert len(pair_hands) == 4
        assert set([(0, 1), (2, 2)]) in pair_hands
        assert set([(0, 2), (2, 2)]) in pair_hands
        assert set([(1, 0), (2, 0)]) in pair_hands
        assert set([(1, 1), (2, 1)]) in pair_hands

        # this isn't a valid hand (the cards are on the same row)
        assert set([(0, 1), (0, 2)]) not in pair_hands

    def test_trip_hands(self):
        state = GameState()
        card_piles = [
            [[Card("K", "h")], [Card("K", "d")], [Card("K", "s")]],
            [[Card("3", "c")], [Card("A", "s")], [Card("A", "d")]],
            [[Card("3", "s")], [Card("A", "c")], [Card("K", "c")]]
        ]
        state.start_new_game(lucky_card=Card("7", "h"), card_piles=card_piles)

        trip_hands = state._get_trip_hands()
        assert len(trip_hands) == 4
        assert set([(0, 0), (0, 1), (2, 2)]) in trip_hands
        assert set([(0, 0), (0, 2), (2, 2)]) in trip_hands
        assert set([(0, 1), (0, 2), (2, 2)]) in trip_hands
        assert set([(1, 1), (1, 2), (2, 1)]) in trip_hands

        # this isn't a valid hand (the cards are on the same row)
        assert set([(0, 0), (0, 1), (0, 2)]) not in trip_hands

    def test_quad_hands(self):
        state = GameState()
        card_piles = [
            [[Card("K", "h")], [Card("K", "d")], [Card("K", "s")]],
            [[Card("3", "c")], [Card("A", "s")], [Card("A", "d")]],
            [[Card("3", "s")], [Card("A", "c")], [Card("K", "c")]]
        ]
        state.start_new_game(lucky_card=Card("7", "h"), card_piles=card_piles)

        quad_hands = state._get_quad_hands()
        assert len(quad_hands) == 1
        assert set([(0, 0), (0, 1), (0, 2), (2, 2)]) in quad_hands

    def test_full_house_hands(self):
        state = GameState()
        card_piles = [
            [[Card("K", "h")], [Card("K", "d")], [Card("K", "s")]],
            [[Card("3", "c")], [Card("A", "s")], [Card("A", "d")]],
            [[Card("3", "s")], [Card("A", "c")], [Card("K", "c")]]
        ]
        state.start_new_game(lucky_card=Card("7", "h"), card_piles=card_piles)

        full_house_hands = state._get_full_house_hands()
        assert len(full_house_hands) == 23

        # three kings and two aces - 12 combos ((4 choose 3) * (3 choose 2))
        assert set([(0, 0), (0, 1), (0, 2), (1, 1), (1, 2)]) in full_house_hands
        assert set([(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)]) in full_house_hands
        assert set([(0, 0), (0, 1), (0, 2), (1, 2), (2, 1)]) in full_house_hands

        assert set([(0, 0), (0, 1), (2, 2), (1, 1), (1, 2)]) in full_house_hands
        assert set([(0, 0), (0, 1), (2, 2), (1, 1), (2, 1)]) in full_house_hands
        assert set([(0, 0), (0, 1), (2, 2), (1, 2), (2, 1)]) in full_house_hands

        assert set([(0, 0), (0, 2), (2, 2), (1, 1), (1, 2)]) in full_house_hands
        assert set([(0, 0), (0, 2), (2, 2), (1, 1), (2, 1)]) in full_house_hands
        assert set([(0, 0), (0, 2), (2, 2), (1, 2), (2, 1)]) in full_house_hands

        assert set([(0, 1), (0, 2), (2, 2), (1, 1), (1, 2)]) in full_house_hands
        assert set([(0, 1), (0, 2), (2, 2), (1, 1), (2, 1)]) in full_house_hands
        assert set([(0, 1), (0, 2), (2, 2), (1, 2), (2, 1)]) in full_house_hands

        # three kings and two threes - 4 combos ((4 choose 3) * (2 choose 2))
        assert set([(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)]) in full_house_hands
        assert set([(0, 0), (0, 1), (2, 2), (1, 0), (2, 0)]) in full_house_hands
        assert set([(0, 0), (0, 2), (2, 2), (1, 0), (2, 0)]) in full_house_hands
        assert set([(0, 1), (0, 2), (2, 2), (1, 0), (2, 0)]) in full_house_hands

        # three aces and two kings - 6 combos ((3 choose 3) * (4 choose 2))
        assert set([(1, 1), (1, 2), (2, 1), (0, 0), (0, 1)]) in full_house_hands
        assert set([(1, 1), (1, 2), (2, 1), (0, 0), (0, 2)]) in full_house_hands
        assert set([(1, 1), (1, 2), (2, 1), (0, 0), (2, 2)]) in full_house_hands
        assert set([(1, 1), (1, 2), (2, 1), (0, 1), (0, 2)]) in full_house_hands
        assert set([(1, 1), (1, 2), (2, 1), (0, 1), (2, 2)]) in full_house_hands
        assert set([(1, 1), (1, 2), (2, 1), (0, 2), (2, 2)]) in full_house_hands

        # three aces and two threes - 1 combo ((3 choose 3) * (2 choose 2))
        assert set([(1, 1), (1, 2), (2, 1), (1, 0), (2, 0)]) in full_house_hands

    def test_small_straight_hands(self):
        state = GameState()
        card_piles = [
            [[Card("K", "h")], [Card("Q", "d")], [Card("A", "s")]],
            [[Card("2", "c")], [Card("A", "d")], [Card("J", "d")]],
            [[Card("3", "s")], [Card("T", "c")], [Card("5", "c")]]
        ]
        state.start_new_game(lucky_card=Card("7", "h"), card_piles=card_piles)

        sm_straight_hands = state._get_sm_straight_hands()
        assert len(sm_straight_hands) == 5
        assert set([(0, 0), (0, 1), (1, 1)]) in sm_straight_hands
        assert set([(0, 0), (0, 1), (1, 2)]) in sm_straight_hands
        assert set([(0, 1), (1, 2), (2, 1)]) in sm_straight_hands
        assert set([(0, 2), (1, 0), (2, 0)]) in sm_straight_hands
        assert set([(1, 0), (1, 1), (2, 0)]) in sm_straight_hands

        # this isn't a valid hand (the cards are on the same row)
        assert set([(0, 0), (0, 1), (0, 2)]) not in sm_straight_hands

        # the small straight can't wrap with K-A-2
        assert set([(0, 0), (0, 2), (1, 0)]) not in sm_straight_hands
        assert set([(0, 0), (1, 0), (1, 1)]) not in sm_straight_hands

    def test_large_straight_hands(self):
        state = GameState()
        card_piles = [
            [[Card("K", "h")], [Card("Q", "d")], [Card("A", "s")]],
            [[Card("2", "c")], [Card("A", "d")], [Card("J", "d")]],
            [[Card("3", "s")], [Card("T", "c")], [Card("5", "c")]]
        ]
        state.start_new_game(lucky_card=Card("7", "h"), card_piles=card_piles)

        lg_straight_hands = state._get_lg_straight_hands()
        assert len(lg_straight_hands) == 2
        assert set([(0, 0), (0, 1), (0, 2), (1, 2), (2, 1)]) in lg_straight_hands
        assert set([(0, 0), (0, 1), (1, 1), (1, 2), (2, 1)]) in lg_straight_hands

        # the small straight can't wrap with J-Q-K-A-2 or Q-K-A-2-3
        assert set([(0, 0), (0, 1), (0, 2), (1, 0), (1, 2)]) not in lg_straight_hands
        assert set([(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)]) not in lg_straight_hands

    def test_flush_hands(self):
        state = GameState()
        card_piles = [
            [[Card("K", "d")], [Card("6", "d")], [Card("A", "s")]],
            [[Card("2", "c")], [Card("A", "d")], [Card("J", "d")]],
            [[Card("3", "s")], [Card("5", "d")], [Card("9", "d")]]
        ]
        state.start_new_game(lucky_card=Card("7", "h"), card_piles=card_piles)

        flush_hands = state._get_flush_hands()
        assert len(flush_hands) == 6
        assert set([(0, 0), (0, 1), (1, 1), (1, 2), (2, 1)]) in flush_hands
        assert set([(0, 0), (0, 1), (1, 1), (1, 2), (2, 2)]) in flush_hands
        assert set([(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)]) in flush_hands
        assert set([(0, 0), (0, 1), (1, 2), (2, 1), (2, 2)]) in flush_hands
        assert set([(0, 0), (1, 1), (1, 2), (2, 1), (2, 2)]) in flush_hands
        assert set([(0, 1), (1, 1), (1, 2), (2, 1), (2, 2)]) in flush_hands

    def test_straight_flush_hands(self):
        state = GameState()
        card_piles = [
            [[Card("K", "d")], [Card("Q", "d")], [Card("A", "s")]],
            [[Card("2", "c")], [Card("A", "d")], [Card("J", "d")]],
            [[Card("3", "s")], [Card("T", "d")], [Card("9", "d")]]
        ]
        state.start_new_game(lucky_card=Card("7", "h"), card_piles=card_piles)

        straight_flush_hands = state._get_straight_flush_hands()
        assert len(straight_flush_hands) == 2
        assert set([(0, 0), (0, 1), (1, 1), (1, 2), (2, 1)]) in straight_flush_hands
        assert set([(0, 0), (0, 1), (1, 2), (2, 1), (2, 2)]) in straight_flush_hands

        # The hand must all be the same suit
        assert set([(0, 0), (0, 1), (0, 2), (1, 2), (2, 1)]) not in straight_flush_hands


if __name__ == '__main__':
    unittest.main()
