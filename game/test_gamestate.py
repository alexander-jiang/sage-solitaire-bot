import unittest
import numpy as np
from deck import SUITS, RANKS, Card
from gamestate import GameState

class TestGameState(unittest.TestCase):
    def test_new_game_state(self):
        state = GameState()
        state.start_new_game_from_deck(seed=12345)
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
        state.start_new_game_from_deck(seed=12345)

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
        state.start_new_game_from_deck(seed=12345)

        pile_row, pile_col = (2, 2)
        upcard_num = state.upcard_nums()[pile_row][pile_col]
        assert upcard_num in state.dead_card_nums
        assert state.pile_sizes()[pile_row][pile_col] == 2

        # print(state.full_info())
        # print(state.actions())

        # First discard from the pile
        new_state, reward = state.discard_from_pile(pile_row, pile_col)
        # print(new_state.full_info())
        # print(new_state.actions())

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
        # print(new_state2.full_info())
        # print(new_state2.actions())

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

    def test_actions(self):
        state = GameState()
        card_piles = [
            [[Card("2", "s"), Card("Q", "s")], [Card("K", "h"), Card("7", "d")], [Card("K", "s"), Card("Q", "c")]],
            [[Card("3", "c"), Card("3", "h")], [Card("A", "s"), Card("T", "c")], [Card("6", "s"), Card("6", "c")]],
            [[Card("3", "s"), Card("2", "d")], [Card("A", "c"), Card("9", "c")], [Card("K", "c"), Card("T", "h")]]
        ]
        state.start_new_game(lucky_card=Card("7", "h"), card_piles=card_piles)
        state.discards_remaining = 1

        state_actions = state.actions()
        # print(state_actions)
        assert len(state_actions) == 21

        # 4 pairs (can't pick both Kings on the top row)
        new_state = state.copy()
        new_state.card_num_piles[0][1] = state.card_num_piles[0][1][1:]
        new_state.card_num_piles[2][2] = state.card_num_piles[2][2][1:]
        new_state.discards_remaining = 2
        new_state.dead_card_nums.add(state.card_num_piles[0][1][1])
        new_state.dead_card_nums.add(state.card_num_piles[2][2][1])
        assert (set([(0, 1), (2, 2)]), new_state, 20) in state_actions # note the lucky bonus

        new_state = state.copy()
        new_state.card_num_piles[0][2] = state.card_num_piles[0][2][1:]
        new_state.card_num_piles[2][2] = state.card_num_piles[2][2][1:]
        new_state.discards_remaining = 2
        new_state.dead_card_nums.add(state.card_num_piles[0][2][1])
        new_state.dead_card_nums.add(state.card_num_piles[2][2][1])
        assert (set([(0, 2), (2, 2)]), new_state, 10) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[1][0] = state.card_num_piles[1][0][1:]
        new_state.card_num_piles[2][0] = state.card_num_piles[2][0][1:]
        new_state.discards_remaining = 2
        new_state.dead_card_nums.add(state.card_num_piles[1][0][1])
        new_state.dead_card_nums.add(state.card_num_piles[2][0][1])
        assert (set([(1, 0), (2, 0)]), new_state, 10) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[1][1] = state.card_num_piles[1][1][1:]
        new_state.card_num_piles[2][1] = state.card_num_piles[2][1][1:]
        new_state.discards_remaining = 2
        new_state.dead_card_nums.add(state.card_num_piles[1][1][1])
        new_state.dead_card_nums.add(state.card_num_piles[2][1][1])
        assert (set([(1, 1), (2, 1)]), new_state, 10) in state_actions

        # this isn't a valid hand (the cards are on the same row)
        new_state = state.copy()
        new_state.card_num_piles[0][1] = state.card_num_piles[0][1][1:]
        new_state.card_num_piles[0][2] = state.card_num_piles[0][2][1:]
        new_state.discards_remaining = 2
        new_state.dead_card_nums.add(state.card_num_piles[0][1][1])
        new_state.dead_card_nums.add(state.card_num_piles[0][2][1])
        assert (set([(0, 1), (0, 2)]), new_state, 20) not in state_actions

        # 1 trips
        new_state = state.copy()
        new_state.card_num_piles[0][1] = state.card_num_piles[0][1][1:]
        new_state.card_num_piles[0][2] = state.card_num_piles[0][2][1:]
        new_state.card_num_piles[2][2] = state.card_num_piles[2][2][1:]
        new_state.discards_remaining = 2
        new_state.dead_card_nums.add(state.card_num_piles[0][1][1])
        new_state.dead_card_nums.add(state.card_num_piles[0][2][1])
        new_state.dead_card_nums.add(state.card_num_piles[2][2][1])
        assert (set([(0, 1), (0, 2), (2, 2)]), new_state, 60) in state_actions # note the lucky bonus

        # 2 full houses
        new_state = state.copy()
        new_state.card_num_piles[0][1] = state.card_num_piles[0][1][1:]
        new_state.card_num_piles[0][2] = state.card_num_piles[0][2][1:]
        new_state.card_num_piles[2][2] = state.card_num_piles[2][2][1:]
        new_state.card_num_piles[1][1] = state.card_num_piles[1][1][1:]
        new_state.card_num_piles[2][1] = state.card_num_piles[2][1][1:]
        new_state.discards_remaining = 2
        new_state.dead_card_nums.add(state.card_num_piles[0][1][1])
        new_state.dead_card_nums.add(state.card_num_piles[0][2][1])
        new_state.dead_card_nums.add(state.card_num_piles[2][2][1])
        new_state.dead_card_nums.add(state.card_num_piles[1][1][1])
        new_state.dead_card_nums.add(state.card_num_piles[2][1][1])
        assert (set([(0, 1), (0, 2), (2, 2), (1, 1), (2, 1)]), new_state, 140) in state_actions # note the lucky bonus

        new_state = state.copy()
        new_state.card_num_piles[0][1] = state.card_num_piles[0][1][1:]
        new_state.card_num_piles[0][2] = state.card_num_piles[0][2][1:]
        new_state.card_num_piles[2][2] = state.card_num_piles[2][2][1:]
        new_state.card_num_piles[1][0] = state.card_num_piles[1][0][1:]
        new_state.card_num_piles[2][0] = state.card_num_piles[2][0][1:]
        new_state.discards_remaining = 2
        new_state.dead_card_nums.add(state.card_num_piles[0][1][1])
        new_state.dead_card_nums.add(state.card_num_piles[0][2][1])
        new_state.dead_card_nums.add(state.card_num_piles[2][2][1])
        new_state.dead_card_nums.add(state.card_num_piles[1][0][1])
        new_state.dead_card_nums.add(state.card_num_piles[2][0][1])
        assert (set([(0, 1), (0, 2), (2, 2), (1, 0), (2, 0)]), new_state, 140) in state_actions # note the lucky bonus

        # 4 three-straights
        new_state = state.copy()
        new_state.card_num_piles[0][0] = state.card_num_piles[0][0][1:]
        new_state.card_num_piles[1][0] = state.card_num_piles[1][0][1:]
        new_state.card_num_piles[1][1] = state.card_num_piles[1][1][1:]
        new_state.discards_remaining = 2
        new_state.dead_card_nums.add(state.card_num_piles[0][0][1])
        new_state.dead_card_nums.add(state.card_num_piles[1][0][1])
        new_state.dead_card_nums.add(state.card_num_piles[1][1][1])
        assert (set([(0, 0), (1, 0), (1, 1)]), new_state, 20) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[0][0] = state.card_num_piles[0][0][1:]
        new_state.card_num_piles[2][0] = state.card_num_piles[2][0][1:]
        new_state.card_num_piles[1][1] = state.card_num_piles[1][1][1:]
        new_state.discards_remaining = 2
        new_state.dead_card_nums.add(state.card_num_piles[0][0][1])
        new_state.dead_card_nums.add(state.card_num_piles[2][0][1])
        new_state.dead_card_nums.add(state.card_num_piles[1][1][1])
        assert (set([(0, 0), (2, 0), (1, 1)]), new_state, 20) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[0][0] = state.card_num_piles[0][0][1:]
        new_state.card_num_piles[1][0] = state.card_num_piles[1][0][1:]
        new_state.card_num_piles[2][1] = state.card_num_piles[2][1][1:]
        new_state.discards_remaining = 2
        new_state.dead_card_nums.add(state.card_num_piles[0][0][1])
        new_state.dead_card_nums.add(state.card_num_piles[1][0][1])
        new_state.dead_card_nums.add(state.card_num_piles[2][1][1])
        assert (set([(0, 0), (1, 0), (2, 1)]), new_state, 20) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[0][0] = state.card_num_piles[0][0][1:]
        new_state.card_num_piles[2][0] = state.card_num_piles[2][0][1:]
        new_state.card_num_piles[2][1] = state.card_num_piles[2][1][1:]
        new_state.discards_remaining = 2
        new_state.dead_card_nums.add(state.card_num_piles[0][0][1])
        new_state.dead_card_nums.add(state.card_num_piles[2][0][1])
        new_state.dead_card_nums.add(state.card_num_piles[2][1][1])
        assert (set([(0, 0), (2, 0), (2, 1)]), new_state, 20) in state_actions

        # 1 flush
        new_state = state.copy()
        new_state.card_num_piles[0][0] = state.card_num_piles[0][0][1:]
        new_state.card_num_piles[0][2] = state.card_num_piles[0][2][1:]
        new_state.card_num_piles[1][1] = state.card_num_piles[1][1][1:]
        new_state.card_num_piles[1][2] = state.card_num_piles[1][2][1:]
        new_state.card_num_piles[2][0] = state.card_num_piles[2][0][1:]
        new_state.discards_remaining = 2
        new_state.dead_card_nums.add(state.card_num_piles[0][0][1])
        new_state.dead_card_nums.add(state.card_num_piles[0][2][1])
        new_state.dead_card_nums.add(state.card_num_piles[1][1][1])
        new_state.dead_card_nums.add(state.card_num_piles[1][2][1])
        new_state.dead_card_nums.add(state.card_num_piles[2][0][1])
        assert (set([(0, 0), (0, 2), (1, 1), (1, 2), (2, 0)]), new_state, 90) in state_actions

        # 9 discard actions
        new_state = state.copy()
        new_state.card_num_piles[0][0] = state.card_num_piles[0][0][1:]
        new_state.discards_remaining = 0
        new_state.dead_card_nums.add(state.card_num_piles[0][0][1])
        assert (set([(0, 0)]), new_state, 0) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[0][1] = state.card_num_piles[0][1][1:]
        new_state.discards_remaining = 0
        new_state.dead_card_nums.add(state.card_num_piles[0][1][1])
        assert (set([(0, 1)]), new_state, 0) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[0][2] = state.card_num_piles[0][2][1:]
        new_state.discards_remaining = 0
        new_state.dead_card_nums.add(state.card_num_piles[0][2][1])
        assert (set([(0, 2)]), new_state, 0) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[1][0] = state.card_num_piles[1][0][1:]
        new_state.discards_remaining = 0
        new_state.dead_card_nums.add(state.card_num_piles[1][0][1])
        assert (set([(1, 0)]), new_state, 0) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[1][1] = state.card_num_piles[1][1][1:]
        new_state.discards_remaining = 0
        new_state.dead_card_nums.add(state.card_num_piles[1][1][1])
        assert (set([(1, 1)]), new_state, 0) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[1][2] = state.card_num_piles[1][2][1:]
        new_state.discards_remaining = 0
        new_state.dead_card_nums.add(state.card_num_piles[1][2][1])
        assert (set([(1, 2)]), new_state, 0) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[2][0] = state.card_num_piles[2][0][1:]
        new_state.discards_remaining = 0
        new_state.dead_card_nums.add(state.card_num_piles[2][0][1])
        assert (set([(2, 0)]), new_state, 0) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[2][1] = state.card_num_piles[2][1][1:]
        new_state.discards_remaining = 0
        new_state.dead_card_nums.add(state.card_num_piles[2][1][1])
        assert (set([(2, 1)]), new_state, 0) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[2][2] = state.card_num_piles[2][2][1:]
        new_state.discards_remaining = 0
        new_state.dead_card_nums.add(state.card_num_piles[2][2][1])
        assert (set([(2, 2)]), new_state, 0) in state_actions

    def test_discard_clear_bonus(self):
        state = GameState()
        card_piles = [
            [[Card("2", "s")], [Card("K", "h")], [Card("K", "s")]],
            [[Card("3", "c")], [Card("A", "s")], [Card("6", "s")]],
            [[Card("3", "s")], [Card("A", "c")], [Card("K", "c")]]
        ]
        state.start_new_game(lucky_card=Card("7", "h"), card_piles=card_piles)
        state.discards_remaining = 1

        state_actions = state.actions()
        # print(state_actions)
        assert len(state_actions) == 21

        # 4 pairs (can't pick both Kings on the top row)
        new_state = state.copy()
        new_state.card_num_piles[0][1] = []
        new_state.card_num_piles[2][2] = []
        new_state.discards_remaining = 2
        assert (set([(0, 1), (2, 2)]), new_state, 20) in state_actions # note the lucky bonus

        new_state = state.copy()
        new_state.card_num_piles[0][2] = []
        new_state.card_num_piles[2][2] = []
        new_state.discards_remaining = 2
        assert (set([(0, 2), (2, 2)]), new_state, 10) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[1][0] = []
        new_state.card_num_piles[2][0] = []
        new_state.discards_remaining = 2
        assert (set([(1, 0), (2, 0)]), new_state, 10) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[1][1] = []
        new_state.card_num_piles[2][1] = []
        new_state.discards_remaining = 2
        assert (set([(1, 1), (2, 1)]), new_state, 10) in state_actions

        # this isn't a valid hand (the cards are on the same row)
        new_state = state.copy()
        new_state.card_num_piles[0][1] = []
        new_state.card_num_piles[0][2] = []
        new_state.discards_remaining = 2
        assert (set([(0, 1), (0, 2)]), new_state, 20) not in state_actions

        # 1 trips
        new_state = state.copy()
        new_state.card_num_piles[0][1] = []
        new_state.card_num_piles[0][2] = []
        new_state.card_num_piles[2][2] = []
        new_state.discards_remaining = 2
        assert (set([(0, 1), (0, 2), (2, 2)]), new_state, 60) in state_actions # note the lucky bonus

        # 2 full houses
        new_state = state.copy()
        new_state.card_num_piles[0][1] = []
        new_state.card_num_piles[0][2] = []
        new_state.card_num_piles[2][2] = []
        new_state.card_num_piles[1][1] = []
        new_state.card_num_piles[2][1] = []
        new_state.discards_remaining = 2
        assert (set([(0, 1), (0, 2), (2, 2), (1, 1), (2, 1)]), new_state, 140) in state_actions # note the lucky bonus

        new_state = state.copy()
        new_state.card_num_piles[0][1] = []
        new_state.card_num_piles[0][2] = []
        new_state.card_num_piles[2][2] = []
        new_state.card_num_piles[1][0] = []
        new_state.card_num_piles[2][0] = []
        new_state.discards_remaining = 2
        assert (set([(0, 1), (0, 2), (2, 2), (1, 0), (2, 0)]), new_state, 140) in state_actions # note the lucky bonus

        # 4 three-straights
        new_state = state.copy()
        new_state.card_num_piles[0][0] = []
        new_state.card_num_piles[1][0] = []
        new_state.card_num_piles[1][1] = []
        new_state.discards_remaining = 2
        assert (set([(0, 0), (1, 0), (1, 1)]), new_state, 20) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[0][0] = []
        new_state.card_num_piles[2][0] = []
        new_state.card_num_piles[1][1] = []
        new_state.discards_remaining = 2
        assert (set([(0, 0), (2, 0), (1, 1)]), new_state, 20) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[0][0] = []
        new_state.card_num_piles[1][0] = []
        new_state.card_num_piles[2][1] = []
        new_state.discards_remaining = 2
        assert (set([(0, 0), (1, 0), (2, 1)]), new_state, 20) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[0][0] = []
        new_state.card_num_piles[2][0] = []
        new_state.card_num_piles[2][1] = []
        new_state.discards_remaining = 2
        assert (set([(0, 0), (2, 0), (2, 1)]), new_state, 20) in state_actions

        # 1 flush
        new_state = state.copy()
        new_state.card_num_piles[0][0] = []
        new_state.card_num_piles[0][2] = []
        new_state.card_num_piles[1][1] = []
        new_state.card_num_piles[1][2] = []
        new_state.card_num_piles[2][0] = []
        new_state.discards_remaining = 2
        assert (set([(0, 0), (0, 2), (1, 1), (1, 2), (2, 0)]), new_state, 90) in state_actions

        # 9 discard actions
        new_state = state.copy()
        new_state.card_num_piles[0][0] = []
        new_state.discards_remaining = 0
        assert (set([(0, 0)]), new_state, 150) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[0][1] = []
        new_state.discards_remaining = 0
        assert (set([(0, 1)]), new_state, 150) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[0][2] = []
        new_state.discards_remaining = 0
        assert (set([(0, 2)]), new_state, 150) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[1][0] = []
        new_state.discards_remaining = 0
        assert (set([(1, 0)]), new_state, 100) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[1][1] = []
        new_state.discards_remaining = 0
        assert (set([(1, 1)]), new_state, 100) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[1][2] = []
        new_state.discards_remaining = 0
        assert (set([(1, 2)]), new_state, 100) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[2][0] = []
        new_state.discards_remaining = 0
        assert (set([(2, 0)]), new_state, 50) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[2][1] = []
        new_state.discards_remaining = 0
        assert (set([(2, 1)]), new_state, 50) in state_actions

        new_state = state.copy()
        new_state.card_num_piles[2][2] = []
        new_state.discards_remaining = 0
        assert (set([(2, 2)]), new_state, 50) in state_actions


if __name__ == '__main__':
    unittest.main()
