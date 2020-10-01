import tkinter as tk
from tkinter import filedialog
from game_engine import Game, GameState

tile_bkgrd_color = {
    0: "#cdc1b4",
    1: "#eee4da",
    2: "#ede0c8",
    3: "#f2b179",
    4: "#f59563",
    5: "#f67c5f",
    6: "#f65e3b",
    7: "#edcf72",
    8: "#edcc61",
    9: "#edc850",
    10: "#edc53f",
    11: "#edc22e",
    12: "#3c3a32"
}

class GameTiles(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master, bd=1, relief=tk.SOLID)
        self.master = master
        for i in range(4):
            self.rowconfigure(i, minsize=100)
            self.columnconfigure(i, minsize=100)
        self.tiles = [
            [tk.Label(
                self, anchor=tk.CENTER,
                fg="#776e65", bg="#cdc1b4", font=('Helvetica', '15', 'bold'),
                bd=1, relief=tk.SOLID
            ),
            tk.Label(
                self, anchor=tk.CENTER,
                fg="#776e65", bg="#cdc1b4", font=('Helvetica', '15', 'bold'),
                bd=1, relief=tk.SOLID
            ),
            tk.Label(
                self, anchor=tk.CENTER,
                fg="#776e65", bg="#cdc1b4", font=('Helvetica', '15', 'bold'),
                bd=1, relief=tk.SOLID
            ),
            tk.Label(
                self, anchor=tk.CENTER,
                fg="#776e65", bg="#cdc1b4", font=('Helvetica', '15', 'bold'),
                bd=1, relief=tk.SOLID
            )] for i in range(4)
        ]
        for i in range(4):
            for j in range(4):
                self.tiles[i][j].grid(row=i, column=j, sticky=tk.N+tk.S+tk.W+tk.E)
        # self.grid()

    def draw_tiles(self, game):
        for i in range(4):
            for j in range(4):
                if game.state.tiles[i][j] > 0:
                    value = 1 << game.state.tiles[i][j]
                    text = f"{value}"
                else:
                    text = ""

                # different tile background/text color for different valued tiles
                if game.state.tiles[i][j] > 12:
                    bg_color = '#3c3a32'
                else:
                    bg_color = tile_bkgrd_color[game.state.tiles[i][j]]

                if game.state.tiles[i][j] > 2:
                    text_color = "#f9f6f2"
                else:
                    text_color = "#776e65"

                self.tiles[i][j]['text'] = text
                self.tiles[i][j]['bg'] = bg_color
                self.tiles[i][j]['fg'] = text_color

class GameWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        self.game = Game()
        self.game_tiles = GameTiles(master=self)
        self.draw_game_tiles()
        self.game_tiles.grid()

        self.score_strvar = tk.StringVar()
        self.game_score = tk.Label(self, textvariable=self.score_strvar)
        self.draw_score()
        self.game_score.grid()

        self.new_game_button = tk.Button(self, text="New Game", command=self.new_game)
        self.new_game_button.grid()

        self.load_game_button = tk.Button(self, text="Load Game", command=self.load_game)
        self.load_game_button.grid()

        self.quit = tk.Button(self, text="Quit", fg="red", command=self.master.destroy)
        self.quit.grid()

    def draw_game_tiles(self):
        self.game_tiles.draw_tiles(self.game)

    def draw_score(self):
        self.score_strvar.set(f"Score: {self.game.state.score}")

    def new_game(self):
        self.master.bind('<Up>', self.move)
        self.master.bind('<Down>', self.move)
        self.master.bind('<Left>', self.move)
        self.master.bind('<Right>', self.move)

        self.game.new_game()
        self.draw_game_tiles()
        self.draw_score()

    def load_game(self):
        fname = filedialog.askopenfilename(filetypes=(("CSV files", "*.csv"),))
        if fname:
            # TODO add instructions to the GUI?
            self.master.unbind('<Up>')
            self.master.unbind('<Down>')
            self.master.bind('<Left>', self.decrement_turn_number)
            self.master.bind('<Right>', self.increment_turn_number)
            print(f"Loading game from {fname}!")
            with open(fname, 'r') as game_file:
                self.game_states = game_file.readlines()
                self.turn_number = 0
            self.load_game_state()

    def load_game_state(self):
        print(f"turn number = {self.turn_number}")
        self.game.state = GameState.from_csv_line(self.game_states[self.turn_number])

        next_action = self.game_states[self.turn_number].split(',')[-1].strip()
        print(f"action from this state: {next_action}")

        self.draw_game_tiles()
        self.draw_score()

    def increment_turn_number(self, event):
        if self.turn_number < len(self.game_states) - 1:
            self.turn_number += 1
            self.load_game_state()

    def decrement_turn_number(self, event):
        if self.turn_number > 0:
            self.turn_number -= 1
            self.load_game_state()

    def move(self, event):
        print(f"moving in dir {event.keysym}")
        self.game.move(event.keysym)
        self.draw_game_tiles()
        self.draw_score()
        if self.game.state.game_over:
            # TODO display a message on GUI
            print("Game over! no moves available")
        # else:
            # print(f"moves available: {self.game.state.moves_available()}")

root = tk.Tk()
root.geometry("500x600")

app = GameWindow(master=root)
app.mainloop()
