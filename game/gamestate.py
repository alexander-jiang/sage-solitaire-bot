import random
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
        self.dead_card_nums = []

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
                pile_card_nums = [card_to_int(card) for card in card_piles[r][c]]
                self.card_num_piles[r][c] = pile_card_nums
                upcard_nums.append(pile_card_nums[0])

        # The reward for clearing each pile
        self.pile_clear_bonus = [[PILE_CLEAR_BONUSES[r][c] for c in range(3)] for r in range(3)]

        # How many discards are remaining
        self.discards_remaining = INITAL_DISCARD_REMAINING

        # The dead cards (includes upcards and the lucky card) i.e. all cards
        # that cannot be one of the hidden/unrevealed cards in each pile
        self.dead_card_nums = [card_to_int(lucky_card)]
        self.dead_card_nums.extend(upcard_nums)

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

        # TODO check whether there are any actions available
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
        new_state.dead_card_nums = list(self.dead_card_nums)
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
            new_state.dead_card_nums.append(revealed_upcard_num)

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
                new_state.dead_card_nums.append(revealed_upcard_num)

        return new_state

    def actions(self):
        action_state_rewards = []
        if self.discards_remaining > 0:
            # TODO can discard from each pile with at least one card in it
            for r in range(3):
                for c in range(3):
                    if not self.is_pile_empty(r, c):
                        new_state, reward = self.discard_from_pile(r, c)
                        action_state_rewards.append(([(r, c)], new_state, reward))

        # TODO generate a list of possible hands given the current board state

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

        # TODO remember that the chosen piles must not all be on the same row

        # don't forget to increase the discards_remaining
        # for pairs/sets/quads and boats, look for enough cards of the same rank
        card_rank_locations = {}
        for r in range(3):
            for c in range(3):
                upcard = int_to_card(upcard_nums[r][c])
                if upcard is not None:
                    upcard_rank = RANKS[upcard.rank_idx()]
                    if upcard_rank not in card_rank_locations:
                        card_rank_locations[upcard_rank] = []
                    card_rank_locations[upcard_rank].append((r, c))
        print(f"card_rank_locations = {card_rank_locations}")

        pair_ranks = set([])
        trip_ranks = set([])
        quad_ranks = set([])
        for card_rank in card_rank_locations:
            if len(card_rank_locations[card_rank]) >= 2:
                pair_ranks.add(card_rank)
            if len(card_rank_locations[card_rank]) >= 3:
                trip_ranks.add(card_rank)
            if len(card_rank_locations[card_rank]) >= 4:
                quad_ranks.add(card_rank)
        full_house_rank_pairs = set([])
        for trip_rank in trip_ranks:
            for pair_rank in pair_ranks:
                if pair_rank == trip_rank:
                    continue
                full_house_ranks = (trip_rank, pair_rank)
                full_house_rank_pairs.add(full_house_ranks)
        print(f"pair_ranks = {pair_ranks}")
        print(f"trip_ranks = {trip_ranks}")
        print(f"quad_ranks = {quad_ranks}")
        print(f"full_house_rank_pairs = {full_house_rank_pairs}")

        # for 3-straights and 5-straights, look for cards of adjacent ranks (remember that Ace can play high or low)

        # for flushes & straight flushes, look for enough cards of the same suit

        return action_state_rewards
