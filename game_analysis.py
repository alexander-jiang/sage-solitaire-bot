from os import listdir
from os.path import isfile, join
import os
import matplotlib.pyplot as plt
import numpy as np


def main():
    game_records_dir = join("game_records", "random_agent")
    game_files = [f for f in listdir(game_records_dir) if isfile(join(game_records_dir, f))]

    game_scores = []
    game_clears = []

    for game_file in game_files:
        with open(join(game_records_dir, game_file), "rb") as f:
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b'\n':
                f.seek(-2, os.SEEK_CUR)
            last_line = f.readline().decode()

            tokens = last_line.split(", ")
            for token in tokens:
                if token.startswith("final score"):
                    final_score = float(token.split(" = ")[1])
                    game_scores.append(final_score)
                elif token.startswith("table cleared"):
                    board_cleared = token.split(" = ")[1] == "True"
                    if board_cleared:
                        game_clears.append(1)
                    else:
                        game_clears.append(0)

    game_scores = np.array(game_scores)
    game_clears = np.array(game_clears)

    plt.hist(game_scores, bins="auto")
    plt.xlabel("Final Game Score")
    plt.ylabel("# Games")
    plt.title(f"Final Score Distribution (agent=Random, n={len(game_scores)})")
    plt.show()

    max_score = np.max(game_scores)
    print(f"Max Score = {max_score}")

    min_score = np.min(game_scores)
    print(f"Min Score = {min_score}")

    avg_score = np.mean(game_scores)
    print(f"Average Score = {avg_score}")

    score_stddev = np.std(game_scores)
    print(f"Score Standard Deviation = {score_stddev}")

    clear_rate = np.mean(game_clears)
    print(f"Game Clear Rate = {clear_rate}")

    if np.any(np.where(game_clears == 1)):
        cleared_scores = np.take(game_scores, np.where(game_clears == 1))
        print(f"Avg Score for Cleared Games = {np.mean(cleared_scores)}")

    if np.any(np.where(game_clears == 0)):
        uncleared_scores = np.take(game_scores, np.where(game_clears == 0))
        print(f"Avg Score for Uncleared Games = {np.mean(uncleared_scores)}")


if __name__ == "__main__":
    main()
