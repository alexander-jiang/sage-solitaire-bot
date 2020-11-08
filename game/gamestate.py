import itertools
import random
from pprint import pprint

from deck import SUITS, RANKS, Deck, card_to_int, int_to_card
import numpy as np

INITAL_DISCARD_REMAINING = 2
MAX_DISCARD_REMAINING = 2
INITIAL_PILE_SIZES = [[8, 8, 8], [7, 6, 5], [4, 3, 2]]
PILE_CLEAR_BONUSES = [[150, 150, 150], [100, 100, 100], [50, 50, 50]]
PAIR_REWARD = 10
THREE_STRAIGHT_REWARD = 20
TRIP_REWARD = 30
FIVE_STRAIGHT_REWARD = 50
FULL_HOUSE_REWARD = 70
FLUSH_REWARD = 90
QUAD_REWARD = 100
STRAIGHT_FLUSH_REWARD = 150
LUCKY_SUIT_MULTIPLIER = 2.0

class GameState:
    def __init__(self):
        self.card_num_piles = [[[] for c in range(3)] for r in range(3)]
        self.pile_clear_bonus = [[None for c in range(3)] for r in range(3)]
        self.lucky_suit_idx = None
        self.lucky_suit = None
        self.discards_remaining = 0
        self.dead_card_nums = set([])

    def start_new_game_from_deck(self, seed=None):
        deck = Deck(seed=seed)

        # Remove one card to choose the "lucky" suit
        lucky_card = deck.take(n=1)[0]

        # Deal the cards for each pile
        card_piles = []
        for r in range(3):
            row = []
            for c in range(3):
                pile_cards = deck.take(n=INITIAL_PILE_SIZES[r][c])
                row.append(pile_cards)
            card_piles.append(row)
        # print(f"card_piles = {card_piles}")
        self.start_new_game(lucky_card=lucky_card, card_piles=card_piles)

    def start_new_game(self, lucky_card, card_piles):
        self.lucky_suit_idx = lucky_card.suit_idx()
        self.lucky_suit = lucky_card.suit

        upcard_nums = []
        for r in range(3):
            for c in range(3):
                if len(card_piles[r][c]) > 0:
                    pile_card_nums = [card_to_int(card) for card in card_piles[r][c]]
                    self.card_num_piles[r][c] = pile_card_nums
                    upcard_nums.append(pile_card_nums[0])

        # The reward for clearing each pile
        self.pile_clear_bonus = [[PILE_CLEAR_BONUSES[r][c] for c in range(3)] for r in range(3)]

        # How many discards are remaining
        self.discards_remaining = INITAL_DISCARD_REMAINING

        # The dead cards (includes upcards and the lucky card) i.e. all cards
        # that cannot be one of the hidden/unrevealed cards in each pile
        self.dead_card_nums = set([card_to_int(lucky_card)])
        self.dead_card_nums.update(upcard_nums)

    def __eq__(self, other):
        return (
            self.card_num_piles == other.card_num_piles and
            self.pile_clear_bonus == other.pile_clear_bonus and
            self.lucky_suit_idx == other.lucky_suit_idx and
            self.discards_remaining == other.discards_remaining and
            self.dead_card_nums == other.dead_card_nums
        )

    def is_game_over(self):
        if self.discards_remaining > 0:
            for r in range(3):
                for c in range(3):
                    if not self.is_pile_empty(r, c):
                        return False

        # check whether there are any actions available
        return len(self.actions()) == 0

    def pile_sizes(self):
        sizes = np.zeros((3, 3))
        for r in range(3):
            for c in range(3):
                sizes[r, c] = len(self.card_num_piles[r][c])
        return sizes

    def is_pile_empty(self, r, c):
        return len(self.card_num_piles[r][c]) == 0

    def upcard_nums(self):
        upcard_nums = [[None] * 3 for r in range(3)]
        for r in range(3):
            for c in range(3):
                if not self.is_pile_empty(r, c):
                    upcard_nums[r][c] = self.card_num_piles[r][c][0]
        return upcard_nums

    def __repr__(self):
        # Print general game state info
        repr = (
            f"LUCKY SUIT = {SUITS[self.lucky_suit_idx]}\n"
            f"DISCARDS LEFT = {self.discards_remaining}\n"
            f"GAME OVER? = {self.is_game_over()}\n"
        )
        upcard_nums = self.upcard_nums()
        pile_sizes = self.pile_sizes()
        # Print board/piles state
        for r in range(3):
            row_repr = "| "
            for c in range(3):
                if not self.is_pile_empty(r, c):
                    upcard = int_to_card(upcard_nums[r][c])
                    row_repr += str(upcard) + f"(+{pile_sizes[r][c] - 1})" + " | "
                else:
                    row_repr += "--(+0) | "
            row_repr += "\n"
            repr += row_repr

        # Print dead cards
        repr += f"DEAD CARDS = {[int_to_card(card_num) for card_num in self.dead_card_nums]}"
        return repr

    def full_info(self):
        # Print full game state info (including the hidden cards)
        repr = (
            f"LUCKY SUIT = {SUITS[self.lucky_suit_idx]}\n"
            f"DISCARDS LEFT = {self.discards_remaining}\n"
            f"GAME OVER? = {self.is_game_over()}\n"
        )
        upcard_nums = self.upcard_nums()
        pile_sizes = self.pile_sizes()
        # Print board/piles state
        for r in range(3):
            for c in range(3):
                pile_repr = f"pile ({r}, {c}): "
                if not self.is_pile_empty(r, c):
                    pile_cards = [int_to_card(card_num) for card_num in self.card_num_piles[r][c]]
                    pile_repr += str(pile_cards)
                else:
                    pile_repr += "(EMPTY PILE)"
                pile_repr += "\n"
                repr += pile_repr

        # Print dead cards
        repr += f"DEAD CARDS = {[int_to_card(card_num) for card_num in self.dead_card_nums]}"
        return repr

    def copy(self):
        new_state = GameState()
        for r in range(3):
            for c in range(3):
                new_state.card_num_piles[r][c] = list(self.card_num_piles[r][c])
                new_state.pile_clear_bonus[r][c] = self.pile_clear_bonus[r][c]
        new_state.lucky_suit_idx = self.lucky_suit_idx
        new_state.lucky_suit = self.lucky_suit
        new_state.discards_remaining = self.discards_remaining
        new_state.dead_card_nums = set(list(self.dead_card_nums))
        return new_state

    def discard_from_pile(self, r, c):
        """
        One of the possible actions: discards a card from the chosen pile.

        Returns: (new_state, reward) - a tuple containing the new game state and
        the reward for the action
        """
        assert self.discards_remaining > 0
        assert not self.is_pile_empty(r, c)

        # reward is usually 0, unless the chosen pile has only one card (the discarded card),
        # in which case the reward is the pile clear bonus for that tile
        if self.pile_sizes()[r][c] == 1:
            reward = self.pile_clear_bonus[r][c]
        else:
            reward = 0

        new_state = self.copy()
        # resulting state has one fewer discard remaining,
        new_state.discards_remaining = self.discards_remaining - 1
        # the chosen pile has one fewer card (and a new upcard)
        new_state.card_num_piles[r][c] = new_state.card_num_piles[r][c][1:]
        # and the revealed card is added to the dead cards list (revealing a new upcard)
        if not new_state.is_pile_empty(r, c):
            revealed_upcard_num = new_state.card_num_piles[r][c][0]
            new_state.dead_card_nums.add(revealed_upcard_num)

        return (new_state, reward)

    def make_hand(self, piles):
        """
        Returns a new state that is generated by removing one card each from
        the given piles. Note that this function assumes the given piles form
        a valid hand (i.e. the new state will have one more discard remaining).

        But this function will check that the selected piles are not empty, and
        that the selected piles are not all on the same row.

        Returns: new_state - the new game state
        """
        # A hand must be made from at least 2 cards
        assert len(piles) > 1
        selected_rows = set([])
        # All of the selected piles must have at least one card in them
        for pile in piles:
            pile_row, pile_col = pile
            assert not self.is_pile_empty(pile_row, pile_col)
            selected_rows.add(pile_row)
        # The selected piles must not all be on the same row of the board
        assert len(selected_rows) > 1

        new_state = self.copy()
        # resulting state has one more discard remaining (up to the cap)
        new_state.discards_remaining = min(self.discards_remaining + 1, MAX_DISCARD_REMAINING)
        for pile in piles:
            r, c = pile
            # the chosen pile has one fewer card (and a new upcard)
            new_state.card_num_piles[r][c] = new_state.card_num_piles[r][c][1:]
            # and the revealed card is added to the dead cards list (revealing a new upcard)
            if not new_state.is_pile_empty(r, c):
                revealed_upcard_num = new_state.card_num_piles[r][c][0]
                new_state.dead_card_nums.add(revealed_upcard_num)

        return new_state

    def _ignore_invalid_hands(self, hands):
        """
        Returns a list of valid hands from the initial list of hands.

        A hand is invalid iF all of the cards in the hand are on the same row.
        """
        valid_hands = []
        for hand in hands:
            valid_hand = False
            hand_row = None
            for location in hand:
                if hand_row is None:
                    hand_row = location[0]
                elif location[0] != hand_row:
                    valid_hand = True
            if valid_hand:
                valid_hands.append(hand)
        return valid_hands

    def _get_pair_hands(self):
        """
        Returns a list of hands, represented as sets of tuples, where each tuple
        is the location of a card in the hand.
        """
        upcard_nums = self.upcard_nums()

        card_rank_locations = {}
        for r in range(3):
            for c in range(3):
                upcard = int_to_card(upcard_nums[r][c])
                if upcard is not None:
                    upcard_rank = RANKS[upcard.rank_idx()]
                    if upcard_rank not in card_rank_locations:
                        card_rank_locations[upcard_rank] = []
                    card_rank_locations[upcard_rank].append((r, c))

        pair_ranks = set([])
        for card_rank in card_rank_locations:
            if len(card_rank_locations[card_rank]) >= 2:
                pair_ranks.add(card_rank)
        # print(f"pair_ranks = {pair_ranks}")

        pair_hands = []
        for pair_rank in pair_ranks:
            rank_locations = card_rank_locations[pair_rank]
            hands = itertools.combinations(rank_locations, 2)
            pair_hands.extend([set(hand) for hand in hands])

        # the chosen piles must not all be on the same row
        pair_hands = self._ignore_invalid_hands(pair_hands)

        # print(f"pair_hands = {pair_hands}")
        return pair_hands

    def _get_trip_hands(self):
        upcard_nums = self.upcard_nums()

        card_rank_locations = {}
        for r in range(3):
            for c in range(3):
                upcard = int_to_card(upcard_nums[r][c])
                if upcard is not None:
                    upcard_rank = RANKS[upcard.rank_idx()]
                    if upcard_rank not in card_rank_locations:
                        card_rank_locations[upcard_rank] = []
                    card_rank_locations[upcard_rank].append((r, c))

        trip_ranks = set([])
        for card_rank in card_rank_locations:
            if len(card_rank_locations[card_rank]) >= 3:
                trip_ranks.add(card_rank)
        # print(f"trip_ranks = {trip_ranks}")

        trip_hands = []
        for trip_rank in trip_ranks:
            rank_locations = card_rank_locations[trip_rank]
            hands = itertools.combinations(rank_locations, 3)
            trip_hands.extend([set(hand) for hand in hands])

        # the chosen piles must not all be on the same row
        trip_hands = self._ignore_invalid_hands(trip_hands)

        # print(f"trip_hands = {trip_hands}")
        return trip_hands

    def _get_quad_hands(self):
        upcard_nums = self.upcard_nums()

        card_rank_locations = {}
        for r in range(3):
            for c in range(3):
                upcard = int_to_card(upcard_nums[r][c])
                if upcard is not None:
                    upcard_rank = RANKS[upcard.rank_idx()]
                    if upcard_rank not in card_rank_locations:
                        card_rank_locations[upcard_rank] = []
                    card_rank_locations[upcard_rank].append((r, c))

        quad_ranks = set([])
        for card_rank in card_rank_locations:
            if len(card_rank_locations[card_rank]) >= 4:
                quad_ranks.add(card_rank)
        # print(f"quad_ranks = {quad_ranks}")

        quad_hands = []
        for quad_rank in quad_ranks:
            rank_locations = card_rank_locations[quad_rank]
            hands = itertools.combinations(rank_locations, 4)
            quad_hands.extend([set(hand) for hand in hands])

        # the chosen piles must not all be on the same row
        quad_hands = self._ignore_invalid_hands(quad_hands)

        # print(f"quad_hands = {quad_hands}")
        return quad_hands

    def _get_full_house_hands(self):
        upcard_nums = self.upcard_nums()

        card_rank_locations = {}
        for r in range(3):
            for c in range(3):
                upcard = int_to_card(upcard_nums[r][c])
                if upcard is not None:
                    upcard_rank = RANKS[upcard.rank_idx()]
                    if upcard_rank not in card_rank_locations:
                        card_rank_locations[upcard_rank] = []
                    card_rank_locations[upcard_rank].append((r, c))

        pair_ranks = set([])
        trip_ranks = set([])
        for card_rank in card_rank_locations:
            if len(card_rank_locations[card_rank]) >= 2:
                pair_ranks.add(card_rank)
            if len(card_rank_locations[card_rank]) >= 3:
                trip_ranks.add(card_rank)

        full_house_rank_pairs = set([])
        for trip_rank in trip_ranks:
            for pair_rank in pair_ranks:
                if pair_rank == trip_rank:
                    continue
                full_house_ranks = (trip_rank, pair_rank)
                full_house_rank_pairs.add(full_house_ranks)
        # print(f"full_house_rank_pairs = {full_house_rank_pairs}")

        full_house_hands = []
        for trip_rank, pair_rank in full_house_rank_pairs:
            trip_rank_locations = card_rank_locations[trip_rank]
            pair_rank_locations = card_rank_locations[pair_rank]
            trip_hands = itertools.combinations(trip_rank_locations, 3)
            pair_hands = itertools.combinations(pair_rank_locations, 2)
            full_house_combos = itertools.product(trip_hands, pair_hands)
            for combo in full_house_combos:
                hand = set(combo[0]).union(set(combo[1]))
                if len(hand) != 5:
                    continue
                full_house_hands.append(hand)

        # the chosen piles must not all be on the same row
        full_house_hands = self._ignore_invalid_hands(full_house_hands)

        # print("full_house_hands: ")
        # pprint(full_house_hands)
        return full_house_hands

    def _get_sm_straight_hands(self):
        upcard_nums = self.upcard_nums()

        card_rank_locations = {}
        for r in range(3):
            for c in range(3):
                upcard = int_to_card(upcard_nums[r][c])
                if upcard is not None:
                    upcard_rank = RANKS[upcard.rank_idx()]
                    if upcard_rank not in card_rank_locations:
                        card_rank_locations[upcard_rank] = []
                    card_rank_locations[upcard_rank].append((r, c))

        wrapping_card_ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

        # looking for 3-straights, check every rank for a possible low-end of the straight: A to Q (A-2-3 to Q-K-A)
        sm_straight_hands = []
        for rank_idx in range(len(wrapping_card_ranks) - (3 - 1)):
            straight_ranks = wrapping_card_ranks[rank_idx:rank_idx + 3]
            straight_possible = True
            for rank in straight_ranks:
                if rank not in card_rank_locations or len(card_rank_locations[rank]) == 0:
                    straight_possible = False
            if not straight_possible:
                continue
            straight_rank_locations = [card_rank_locations[rank] for rank in straight_ranks]
            hands = itertools.product(*straight_rank_locations)
            sm_straight_hands.extend([set(hand) for hand in hands])

        # the chosen piles must not all be on the same row
        sm_straight_hands = self._ignore_invalid_hands(sm_straight_hands)

        # print(f"sm_straight_hands = {sm_straight_hands}")
        return sm_straight_hands

    def _get_lg_straight_hands(self):
        upcard_nums = self.upcard_nums()

        card_rank_locations = {}
        for r in range(3):
            for c in range(3):
                upcard = int_to_card(upcard_nums[r][c])
                if upcard is not None:
                    upcard_rank = RANKS[upcard.rank_idx()]
                    if upcard_rank not in card_rank_locations:
                        card_rank_locations[upcard_rank] = []
                    card_rank_locations[upcard_rank].append((r, c))

        wrapping_card_ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

        # looking for 5-straights, check every rank for a possible low-end of the straight: A to T (A-2-3-4-5 to T-J-Q-K-A)
        lg_straight_hands = []
        for rank_idx in range(len(wrapping_card_ranks) - (5 - 1)):
            straight_ranks = wrapping_card_ranks[rank_idx:rank_idx + 5]
            straight_possible = True
            for rank in straight_ranks:
                if rank not in card_rank_locations or len(card_rank_locations[rank]) == 0:
                    straight_possible = False
            if not straight_possible:
                continue
            straight_rank_locations = [card_rank_locations[rank] for rank in straight_ranks]
            hands = itertools.product(*straight_rank_locations)
            lg_straight_hands.extend([set(hand) for hand in hands])

        # the chosen piles must not all be on the same row
        lg_straight_hands = self._ignore_invalid_hands(lg_straight_hands)

        # print(f"lg_straight_hands = {lg_straight_hands}")
        return lg_straight_hands

    def _get_flush_hands(self):
        upcard_nums = self.upcard_nums()

        card_suit_locations = {}
        for r in range(3):
            for c in range(3):
                upcard = int_to_card(upcard_nums[r][c])
                if upcard is not None:
                    upcard_suit = SUITS[upcard.suit_idx()]
                    if upcard_suit not in card_suit_locations:
                        card_suit_locations[upcard_suit] = []
                    card_suit_locations[upcard_suit].append((r, c))

        flush_suits = set([])
        for card_suit in card_suit_locations:
            if len(card_suit_locations[card_suit]) >= 5:
                flush_suits.add(card_suit)
        # print(f"flush_suits = {flush_suits}")

        flush_hands = []
        for flush_suit in flush_suits:
            suit_locations = card_suit_locations[flush_suit]
            hands = itertools.combinations(suit_locations, 5)
            flush_hands.extend([set(hand) for hand in hands])

        # print(f"flush_hands = {flush_hands}")
        return flush_hands

    def _get_straight_flush_hands(self):
        upcard_nums = self.upcard_nums()

        lg_straight_hands = self._get_lg_straight_hands()

        straight_flush_hands = []
        for hand in lg_straight_hands:
            hand_suit = None
            valid_hand = True
            for location in hand:
                row, col = location
                card = int_to_card(upcard_nums[row][col])
                if hand_suit is None:
                    hand_suit = card.suit
                elif card.suit != hand_suit:
                    valid_hand = False
            if valid_hand:
                straight_flush_hands.append(hand)

        # print(f"straight_flush_hands = {straight_flush_hands}")
        return straight_flush_hands

    def _is_lucky_hand(self, piles):
        upcard_nums = self.upcard_nums()

        for pile in piles:
            pile_row, pile_col = pile
            assert not self.is_pile_empty(pile_row, pile_col)
            card = int_to_card(upcard_nums[pile_row][pile_col])

            if card.suit == self.lucky_suit:
                return True
        return False

    def actions(self):
        action_state_rewards = []
        if self.discards_remaining > 0:
            # can discard from each pile with at least one card in it
            for r in range(3):
                for c in range(3):
                    if not self.is_pile_empty(r, c):
                        new_state, reward = self.discard_from_pile(r, c)
                        action_state_rewards.append((set([(r, c)]), new_state, reward))

        # generate filters for upcard ranks & suits
        upcard_nums = self.upcard_nums()
        # upcard_rank_idxs = np.zeros((3, 3)) - 1
        # upcard_suit_idxs = np.zeros((3, 3)) - 1
        # for r in range(3):
        #     for c in range(3):
        #         upcard = int_to_card(upcard_nums[r][c])
        #         if upcard is not None:
        #             upcard_rank_idxs[r, c] = upcard.rank_idx()
        #             upcard_suit_idxs[r, c] = upcard.suit_idx()

        # generate a list of possible hands given the current board state
        # and for each hand, generate the (hand locations, successor state, reward) tuple
        # TODO account for lucky suit

        pair_hands = self._get_pair_hands()
        for hand_piles in pair_hands:
            new_state = self.make_hand(hand_piles)
            reward = PAIR_REWARD
            if self._is_lucky_hand(hand_piles):
                reward *= LUCKY_SUIT_MULTIPLIER
            action_state_rewards.append((hand_piles, new_state, reward))

        trip_hands = self._get_trip_hands()
        for hand_piles in trip_hands:
            new_state = self.make_hand(hand_piles)
            reward = TRIP_REWARD
            if self._is_lucky_hand(hand_piles):
                reward *= LUCKY_SUIT_MULTIPLIER
            action_state_rewards.append((hand_piles, new_state, reward))

        quad_hands = self._get_quad_hands()
        for hand_piles in quad_hands:
            new_state = self.make_hand(hand_piles)
            reward = QUAD_REWARD
            if self._is_lucky_hand(hand_piles):
                reward *= LUCKY_SUIT_MULTIPLIER
            action_state_rewards.append((hand_piles, new_state, reward))

        full_house_hands = self._get_full_house_hands()
        for hand_piles in full_house_hands:
            new_state = self.make_hand(hand_piles)
            reward = FULL_HOUSE_REWARD
            if self._is_lucky_hand(hand_piles):
                reward *= LUCKY_SUIT_MULTIPLIER
            action_state_rewards.append((hand_piles, new_state, reward))

        sm_straight_hands = self._get_sm_straight_hands()
        for hand_piles in sm_straight_hands:
            new_state = self.make_hand(hand_piles)
            reward = THREE_STRAIGHT_REWARD
            if self._is_lucky_hand(hand_piles):
                reward *= LUCKY_SUIT_MULTIPLIER
            action_state_rewards.append((hand_piles, new_state, reward))

        lg_straight_hands = self._get_lg_straight_hands()
        for hand_piles in lg_straight_hands:
            new_state = self.make_hand(hand_piles)
            reward = FIVE_STRAIGHT_REWARD
            if self._is_lucky_hand(hand_piles):
                reward *= LUCKY_SUIT_MULTIPLIER
            action_state_rewards.append((hand_piles, new_state, reward))

        flush_hands = self._get_flush_hands()
        for hand_piles in flush_hands:
            new_state = self.make_hand(hand_piles)
            reward = FLUSH_REWARD
            if self._is_lucky_hand(hand_piles):
                reward *= LUCKY_SUIT_MULTIPLIER
            action_state_rewards.append((hand_piles, new_state, reward))

        straight_flush_hands = self._get_straight_flush_hands()
        for hand_piles in straight_flush_hands:
            new_state = self.make_hand(hand_piles)
            reward = STRAIGHT_FLUSH_REWARD
            if self._is_lucky_hand(hand_piles):
                reward *= LUCKY_SUIT_MULTIPLIER
            action_state_rewards.append((hand_piles, new_state, reward))

        return action_state_rewards
