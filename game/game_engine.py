from datetime import datetime
import random
import os

NUM_ROWS = 4
NUM_COLS = 4
GAME_FILES_DIR = 'games'

class GameState:
    def __init__(self, nrows=NUM_ROWS, ncols=NUM_COLS, tiles=[[0] * NUM_COLS for i in range(NUM_ROWS)], score=0, game_over=False):
        assert len(tiles) == nrows
        assert len(tiles[0]) == ncols
        assert score >= 0
        self.nrows = nrows
        self.ncols = ncols
        self.tiles = tiles
        self.score = score
        self.game_over = game_over

    def copy(self):
        return GameState(nrows=self.nrows, ncols=self.ncols, tiles=[row.copy() for row in self.tiles], score=self.score, game_over=self.game_over)

    ## constructor that takes in a line from the game file csv
    @classmethod
    def from_csv_line(class_obj, line, nrows=NUM_ROWS, ncols=NUM_COLS):
        tokens = line.split(',')
        game_over = tokens[0] == "True"
        score = int(tokens[1])
        tiles = [[0] * ncols for i in range(nrows)]
        for token_idx in range(2, 2 + nrows * ncols):
            tile_idx = token_idx - 2
            tiles[tile_idx // ncols][tile_idx % ncols] = int(tokens[token_idx])
        return class_obj(tiles=tiles, score=score, game_over=game_over)

    def __eq__(self, other):
        if not isinstance(other, GameState):
            return False

        if self.nrows != other.nrows or self.ncols != other.ncols:
            return False
        if self.score != other.score or self.game_over != other.game_over:
            return False
        for i in range(self.nrows):
            for j in range(self.ncols):
                if self.tiles[i][j] != other.tiles[i][j]:
                    return False
        return True

    def max_tile_value(self):
        max_tile = 0
        for i in range(self.nrows):
            for j in range(self.ncols):
                if self.tiles[i][j] > max_tile:
                    max_tile = self.tiles[i][j]
        return 1 << max_tile

    def avg_tile_value(self):
        tile_total = 0
        for i in range(self.nrows):
            for j in range(self.ncols):
                if self.tiles[i][j] > 0:
                    tile_total += 1 << self.tiles[i][j]
        return tile_total / (self.nrows * self.ncols)

    def num_tiles(self):
        tile_total = 0
        for i in range(self.nrows):
            for j in range(self.ncols):
                if self.tiles[i][j] > 0:
                    tile_total += 1
        return tile_total

    def num_empty_tiles(self):
        return self.nrows * self.ncols - self.num_tiles()

    def duplicated_tile_values(self):
        tile_counts = {}
        duplicated_total = 0
        for i in range(self.nrows):
            for j in range(self.ncols):
                if self.tiles[i][j] > 0:
                    if self.tiles[i][j] not in tile_counts:
                        tile_counts[self.tiles[i][j]] = 0
                    else:
                        duplicated_total += self.tiles[i][j]
                    tile_counts[self.tiles[i][j]] += 1
        return duplicated_total

    def reset_state(self, nrows=NUM_ROWS, ncols=NUM_COLS):
        self.tiles = [[0] * ncols for i in range(nrows)]
        self.score = 0
        self.game_over = False

    def move_tiles(self, dir):
        if self.game_over:
            print("Game is over! No more moves allowed")
            return

        # dir is either "Up", "Down", "Left", or "Right"
        assert dir in ["Up", "Down", "Left", "Right"]

        # contains coordinates from rows or columns, ordered based on direction (e.g. if
        # dir is Up, then the groups contains the columns ordered from top-to-bottom)
        groups = []
        if dir == "Up":
            for j in range(self.ncols):
                column = [(i, j) for i in range(self.nrows)]
                groups.append(column)
        elif dir == "Down":
            for j in range(0, self.ncols):
                column = [(i, j) for i in reversed(range(0, self.nrows))]
                groups.append(column)
        elif dir == "Left":
            for i in range(self.nrows):
                row = [(i, j) for j in range(self.ncols)]
                groups.append(row)
        elif dir == "Right":
            for i in range(self.nrows):
                row = [(i, j) for j in reversed(range(0, self.ncols))]
                groups.append(row)
        else:
            print(f"ERROR Invalid direction {dir}!")
            return

        moved_any = False
        for group in groups:
            last_tile_idx = None
            merged_idx = None
            # print(f"Group: {group}")
            for idx in range(len(group)):
                i, j = group[idx]
                if self.tiles[i][j] > 0:
                    # print(f"tile at {group[idx]}, last_tile_idx = {last_tile_idx}")
                    if last_tile_idx is None: # no tiles in front
                        if idx > 0:
                            new_i, new_j = group[0]
                            # print(f"moving tile to front: {group[0]}")
                            self.tiles[new_i][new_j] = self.tiles[i][j]
                            self.tiles[i][j] = 0
                            last_tile_idx = 0
                            moved_any = True
                        else:
                            last_tile_idx = idx
                    else:
                        assert last_tile_idx < idx
                        # check if we can merge
                        tile_i, tile_j = group[last_tile_idx]
                        if self.tiles[tile_i][tile_j] == self.tiles[i][j] and merged_idx != last_tile_idx:
                            # merge and update score
                            # print(f"merging tile on {group[last_tile_idx]}")
                            self.score += (1 << (self.tiles[i][j] + 1))
                            self.tiles[tile_i][tile_j] += 1
                            self.tiles[i][j] = 0
                            merged_idx = last_tile_idx
                            moved_any = True
                        elif last_tile_idx + 1 < idx:
                            # print(f"moving tile to {group[last_tile_idx + 1]}")
                            empty_i, empty_j = group[last_tile_idx + 1]
                            assert self.tiles[empty_i][empty_j] == 0
                            self.tiles[empty_i][empty_j] = self.tiles[i][j]
                            self.tiles[i][j] = 0
                            last_tile_idx += 1
                            moved_any = True
                        else:
                            last_tile_idx = idx
        return moved_any

    def moves_available(self):
        # returns a list containing the valid movement directions from ["Up", "Down", "Left", "Right"]
        dirs = set([])
        up = False
        down = False
        for j in range(self.ncols):
            column = [(i, j) for i in range(self.nrows)]
            prev_val = None
            for coord_idx in range(len(column)):
                i, j = column[coord_idx]
                # if adjacent tiles can be merged, then can merge up or down
                if self.tiles[i][j] == prev_val and self.tiles[i][j] > 0:
                    up = True
                    down = True
                elif prev_val is not None:
                    if self.tiles[i][j] == 0 and prev_val != 0:
                        down = True
                    if self.tiles[i][j] != 0 and prev_val == 0:
                        up = True
                prev_val = self.tiles[i][j]
                if up and down:
                    break
            if up:
                dirs.add("Up")
            if down:
                dirs.add("Down")
            if up and down:
                break

        left = False
        right = False
        for i in range(self.nrows):
            row = [(i, j) for j in range(self.ncols)]
            prev_val = None
            for coord_idx in range(len(row)):
                i, j = row[coord_idx]
                # if adjacent tiles can be merged, then can merge left or right
                if self.tiles[i][j] == prev_val and self.tiles[i][j] > 0:
                    # print(f"can merge: tile at {row[coord_idx]}")
                    left = True
                    right = True
                elif prev_val is not None:
                    if self.tiles[i][j] == 0 and prev_val != 0:
                        # print(f"can shift right to empty tile at {row[coord_idx]}")
                        right = True
                    if self.tiles[i][j] != 0 and prev_val == 0:
                        # print(f"can shift left to empty tile at {row[coord_idx]}")
                        left = True
                prev_val = self.tiles[i][j]
                if left and right:
                    break
            if left:
                dirs.add("Left")
            if right:
                dirs.add("Right")
            if left and right:
                break
        return dirs

    def spawn_tile(self, rand_gen, prob_two_tile=0.9):
        # prob_two_tile is the probability that a 2-tile is spawned (otherwise, a 4-tile is spawned)
        empty_tile_locs = []
        for i in range(self.nrows):
            for j in range(self.ncols):
                if self.tiles[i][j] == 0:
                    empty_tile_locs.append((i, j))
        idx = rand_gen.randrange(len(empty_tile_locs))
        sample = rand_gen.random()
        if sample < prob_two_tile:
            new_tile = 1 # remember that the values in the tile array are log2
        else:
            new_tile = 2
        i, j = empty_tile_locs[idx]
        self.tiles[i][j] = new_tile

    def successor_states(self, move_dir, prob_two_tile=0.9):
        successors = []
        new_state = self.copy()
        moved_any = new_state.move_tiles(move_dir)
        assert moved_any
        reward = new_state.score - self.score
        num_empty_tiles = new_state.num_empty_tiles()
        for i in range(new_state.nrows):
            for j in range(new_state.ncols):
                if new_state.tiles[i][j] == 0:
                    successor = new_state.copy()
                    successor.tiles[i][j] = 1
                    # print(f"before spawning: {new_state.tiles}")
                    # print(f"after spawning: {successor.tiles}")
                    transition_prob = 1.0 / num_empty_tiles
                    successors.append((transition_prob * prob_two_tile, successor, reward))

                    if prob_two_tile < 1.0:
                        successor2 = new_state.copy()
                        successor2.tiles[i][j] = 2
                        successors.append((transition_prob * (1.0 - prob_two_tile), successor2, reward))
        return successors

class Game:
    def __init__(self, game_state=None):
        if game_state is None:
            self.state = GameState()

    def new_game(self, random_seed=None, save_game=True, game_dir=GAME_FILES_DIR):
        self.state.reset_state()

        if random_seed is None:
            random_seed = random.getrandbits(16)

        self.rand_gen = random.Random(random_seed)

        self.state.spawn_tile(self.rand_gen)
        self.state.spawn_tile(self.rand_gen)

        if save_game:
            self.game_filename = os.path.join(game_dir, datetime.now().strftime(f"%Y-%m-%d-%H-%M-%S_{random_seed}.csv"))
            if not os.path.isdir(game_dir):
                os.mkdir(game_dir)
            self.append_game_state()
            print(f"Started a new game! Saving to {self.game_filename}")
        else:
            self.game_filename = None
            print("Started a new game! Not saving the game to a file...")

    def append_game_state(self):
        with open(self.game_filename, 'a') as game_file:
            game_file.write(f"{self.state.game_over},{self.state.score},")
            for i in range(self.state.nrows):
                for j in range(self.state.ncols):
                    # if i == self.state.nrows - 1 and j == self.state.ncols - 1:
                    #     game_file.write(f"{self.state.tiles[i][j]}\n")
                    # else:
                    game_file.write(f"{self.state.tiles[i][j]},")

    def append_game_action(self, dir):
        with open(self.game_filename, 'a') as game_file:
            game_file.write(f"{dir}\n")

    def move(self, dir):
        available_moves = self.state.moves_available()
        moved_any = self.state.move_tiles(dir)

        if moved_any:
            assert dir in available_moves
            self.append_game_action(dir)

            self.state.spawn_tile(self.rand_gen)

            # if there are no valid moves left, then game is over
            if not self.state.moves_available():
                self.state.game_over = True

            self.append_game_state()
