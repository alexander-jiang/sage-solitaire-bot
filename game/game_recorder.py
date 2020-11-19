import os
import uuid
import click
from agent import GameAgent, RandomGameAgent
from deck import int_to_card
from gamestate import GameState

def short_repr_gamestate(gamestate: GameState) -> str:
    board_repr = ""
    upcard_nums = gamestate.upcard_nums()
    for r in range(3):
        for c in range(3):
            if not gamestate.is_pile_empty(r, c):
                upcard = int_to_card(upcard_nums[r][c])
                board_repr += str(upcard) + " "
            else:
                board_repr += "-- "
        if r != 2:
            board_repr += "/ "
        else:
            board_repr += "; "
    board_repr += f"Discards = {gamestate.discards_remaining}, Lucky suit = {gamestate.lucky_suit}"
    board_repr += "\n"
    return board_repr


def play_game(record_filename, agent: GameAgent):
    gamestate = GameState()
    gamestate.start_new_game_from_deck()
    score = 0

    with open(record_filename, "w") as record_file:
        # record the current gamestate
        record_file.write(short_repr_gamestate(gamestate))

        turn_num = 1
        while not gamestate.is_game_over():
            chosen_action = agent.choose_action(gamestate)
            # record the chosen action, reward
            record_file.write(f"\nTurn {turn_num}: {chosen_action[0]}, {chosen_action[2]}\n")

            # update to new game state based on chosen action
            gamestate = chosen_action[1]

            # update score
            score += chosen_action[2]

            # record new gamestate
            record_file.write(short_repr_gamestate(gamestate))

            turn_num += 1

        # once game is over, record game over and total score
        is_board_cleared = gamestate.is_board_empty()
        record_file.write(f"Game over, final score = {score}, table cleared = {is_board_cleared}")
        print(f"final score = {score}, table cleared = {is_board_cleared}")

@click.command()
@click.option("--num-games", "-n", type=int, default=100)
@click.option(
    "--record-directory", "-d", type=str, default="game_records/",
    help="Directory name where the game records will be saved"
)
@click.option(
    "--agent-type", "-a", type=click.Choice(["random", "greedy"]),
    help="Type of agent that will play the games, see game/agent.py for details"
)
def main(num_games: int, record_directory: str, agent_type: str):
    if agent_type == "random":
        agent = RandomGameAgent()
    elif agent_type == "greedy":
        agent = GreedyGameAgent()
    else:
        raise Exception("Invalid agent type! See command documentation")
    for i in range(num_games):
        print(f"playing game {i+1} of {num_games}")
        random_uuid = uuid.uuid4()
        record_filename = os.path.join(record_directory, f"{str(random_uuid)}.txt")
        play_game(record_filename, agent)


if __name__ == "__main__":
    main()
