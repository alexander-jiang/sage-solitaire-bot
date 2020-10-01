import unittest
import numpy as np
from deck import SUITS, RANKS
from gamestate import GameState

class TestGameState(unittest.TestCase):
    def test_new_game_state(self):
        state = GameState()
        state.start_new_game(seed=12345)
        # print(state)
        # print(state.full_info())

        for r in range(3):
            for c in range(3):
                assert not state.is_pile_empty(r, c)
        assert np.array(state.upcard_nums()).shape == (3, 3)
        assert np.array(state.pile_sizes()).shape == (3, 3)
        assert np.array(state.pile_clear_bonus).shape == (3, 3)
        assert state.lucky_suit_idx in range(len(SUITS))
        assert state.discards_remaining == 2
        assert len(state.dead_card_nums) > 0
        assert not state.is_game_over()


    def test_game_state_copy(self):
        state = GameState()
        state.start_new_game(seed=12345)

        # print(state.full_info())

        # Save copies of the info in the original state
        original_card_num = state.card_num_piles[0][0][0]
        original_pile_size = len(state.card_num_piles[0][0])
        original_lucky_suit_idx = state.lucky_suit_idx
        original_discards_remaining = state.discards_remaining

        # New values to set
        new_card_num = state.card_num_piles[0][0][1]
        new_pile_size = original_pile_size - 1
        new_lucky_suit_idx = (original_lucky_suit_idx + 1) % len(SUITS)
        new_discards_remaining = original_discards_remaining - 1

        # Create a copy that shouldn't change (even though the original state is mutated)
        copy_state = state.copy()
        state.card_num_piles[0][0] = state.card_num_piles[0][0][1:]
        state.lucky_suit_idx = new_lucky_suit_idx
        state.discards_remaining = new_discards_remaining

        # print("Updated state")
        # print(state)
        # print("Copy of original state")
        # print(copy_state)

        assert state.upcard_nums()[0][0] == new_card_num
        assert copy_state.upcard_nums()[0][0] == original_card_num
        assert state.pile_sizes()[0][0] == new_pile_size
        assert copy_state.pile_sizes()[0][0] == original_pile_size
        assert state.lucky_suit_idx == new_lucky_suit_idx
        assert copy_state.lucky_suit_idx == original_lucky_suit_idx
        assert state.discards_remaining == new_discards_remaining
        assert copy_state.discards_remaining == original_discards_remaining

        # These properties weren't manually changed
        assert state.lucky_suit == copy_state.lucky_suit
        assert state.dead_card_nums == copy_state.dead_card_nums

    def test_game_state_discard(self):
        state = GameState()
        state.start_new_game(seed=12345)

        pile_row, pile_col = (2, 2)
        upcard_num = state.upcard_nums()[pile_row][pile_col]
        assert upcard_num in state.dead_card_nums
        assert state.pile_sizes()[pile_row][pile_col] == 2

        print(state.full_info())

        # First discard from the pile
        new_state, reward = state.discard_from_pile(pile_row, pile_col)
        print(new_state.full_info())

        new_upcard_num = new_state.upcard_nums()[pile_row][pile_col]
        # check card piles
        assert new_upcard_num != upcard_num
        for r in range(3):
            for c in range(3):
                if r == pile_row and c == pile_col:
                    assert new_state.card_num_piles[r][c] == state.card_num_piles[r][c][1:]
                else:
                    assert new_state.card_num_piles[r][c] == state.card_num_piles[r][c]
        assert new_state.pile_sizes()[pile_row][pile_col] == state.pile_sizes()[pile_row][pile_col] - 1
        # check discards remaining
        assert new_state.discards_remaining == state.discards_remaining - 1
        assert new_state.discards_remaining >= 0
        # check that lucky suit is unchanged
        assert new_state.lucky_suit == state.lucky_suit
        assert new_state.lucky_suit_idx == state.lucky_suit_idx
        # check dead cards in new state
        assert len(new_state.dead_card_nums) == len(state.dead_card_nums) + 1
        assert upcard_num in new_state.dead_card_nums
        assert new_upcard_num in new_state.dead_card_nums
        # check reward
        assert reward == 0

        # second discard from the same pile (should earn the clear bonus)
        new_state2, reward2 = new_state.discard_from_pile(pile_row, pile_col)
        print(new_state2.full_info())

        new_upcard_num2 = new_state2.upcard_nums()[pile_row][pile_col]
        # check card piles
        assert new_upcard_num2 != upcard_num
        assert new_upcard_num2 is None
        for r in range(3):
            for c in range(3):
                if r == pile_row and c == pile_col:
                    assert new_state2.card_num_piles[r][c] == new_state.card_num_piles[r][c][1:]
                else:
                    assert new_state2.card_num_piles[r][c] == new_state.card_num_piles[r][c]
        assert new_state2.pile_sizes()[pile_row][pile_col] == new_state.pile_sizes()[pile_row][pile_col] - 1
        # check discards remaining
        assert new_state2.discards_remaining == new_state.discards_remaining - 1
        assert new_state2.discards_remaining >= 0
        # check that lucky suit is unchanged
        assert new_state2.lucky_suit == new_state.lucky_suit
        assert new_state2.lucky_suit_idx == new_state.lucky_suit_idx
        # check dead cards in new state (no new dead card since the pile was cleared)
        assert new_state2.dead_card_nums == new_state.dead_card_nums
        assert upcard_num in new_state2.dead_card_nums
        assert new_upcard_num in new_state2.dead_card_nums
        # check reward
        assert reward2 == new_state.pile_clear_bonus[pile_row][pile_col]


if __name__ == '__main__':
    unittest.main()