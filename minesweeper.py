import tkinter as tk
from tkinter import messagebox
import random
import pyautogui
import time
import threading
from enum import Enum

class CellState(Enum):
    HIDDEN = 0
    REVEALED = 1
    FLAGGED = 2

class GameState(Enum):
    PLAYING = 0
    WON = 1
    LOST = 2

class MinesweeperGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Minesweeper cu Bot")
        self.root.geometry("800x600")

        self.difficulties = {
            "Ușor": {"rows": 9, "cols": 9, "mines": 10},
            "Mediu": {"rows": 16, "cols": 16, "mines": 40},
            "Greu": {"rows": 16, "cols": 30, "mines": 99}
        }

        self.current_difficulty = "Ușor"
        self.config = self.difficulties[self.current_difficulty]
        self.bot_speed = 0.5
        self.bot_active = False
        self.bot_stats = {"moves": 0, "flags": 0, "reveals": 0}

        self.reset_game()
        self.setup_ui()

    def reset_game(self):
        self.rows = self.config["rows"]
        self.cols = self.config["cols"]
        self.mine_count = self.config["mines"]

        self.board = [[CellState.HIDDEN for _ in range(self.cols)] for _ in range(self.rows)]
        self.mines = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.numbers = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        self.game_state = GameState.PLAYING
        self.first_click = True
        self.flags_placed = 0
        self.cells_revealed = 0
        self.bot_stats = {"moves": 0, "flags": 0, "reveals": 0}

        if hasattr(self, 'buttons'):
            self.create_board()
            self.update_info()

    def setup_ui(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        tk.Label(control_frame, text="Dificultate:").pack(side=tk.LEFT)
        self.difficulty_var = tk.StringVar(value=self.current_difficulty)
        tk.OptionMenu(control_frame, self.difficulty_var, *self.difficulties.keys(), command=self.change_difficulty).pack(side=tk.LEFT)

        tk.Button(control_frame, text="Restart", command=self.restart_game).pack(side=tk.LEFT)
        self.bot_button = tk.Button(control_frame, text="Start Bot", command=self.toggle_bot, bg="green", fg="white")
        self.bot_button.pack(side=tk.LEFT)

        tk.Label(control_frame, text="Viteza Bot:").pack(side=tk.LEFT)
        self.speed_var = tk.DoubleVar(value=self.bot_speed)
        tk.Scale(control_frame, from_=0.1, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, variable=self.speed_var,
                 command=self.update_bot_speed).pack(side=tk.LEFT)

        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(pady=5)
        self.info_label = tk.Label(self.info_frame, text="", font=("Arial", 12))
        self.info_label.pack()
        self.stats_label = tk.Label(self.info_frame, text="", font=("Arial", 10))
        self.stats_label.pack()

        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack(pady=10)

        self.create_board()
        self.update_info()

    def create_board(self):
        for widget in self.game_frame.winfo_children():
            widget.destroy()

        self.buttons = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                btn = tk.Button(self.game_frame, width=3, height=1,
                                command=lambda r=i, c=j: self.left_click(r, c))
                btn.grid(row=i, column=j, padx=1, pady=1)
                btn.bind("<Button-3>", lambda e, r=i, c=j: self.right_click(r, c))
                row.append(btn)
            self.buttons.append(row)

    def change_difficulty(self, diff):
        self.current_difficulty = diff
        self.config = self.difficulties[diff]
        self.reset_game()

    def restart_game(self):
        self.bot_active = False
        self.bot_button.config(text="Start Bot", bg="green")
        self.reset_game()

    def place_mines(self, skip_row, skip_col):
        count = 0
        while count < self.mine_count:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if not self.mines[row][col] and (row, col) != (skip_row, skip_col):
                self.mines[row][col] = True
                count += 1

        for i in range(self.rows):
            for j in range(self.cols):
                if not self.mines[i][j]:
                    self.numbers[i][j] = self.count_adjacent_mines(i, j)

    def count_adjacent_mines(self, row, col):
        return sum(self.mines[i][j]
                   for i in range(max(0, row - 1), min(self.rows, row + 2))
                   for j in range(max(0, col - 1), min(self.cols, col + 2))
                   if (i, j) != (row, col))

    def get_neighbors(self, row, col):
        return [(i, j)
                for i in range(max(0, row - 1), min(self.rows, row + 2))
                for j in range(max(0, col - 1), min(self.cols, col + 2))
                if (i, j) != (row, col)]

    def left_click(self, row, col):
        if self.game_state != GameState.PLAYING or self.board[row][col] in (CellState.REVEALED, CellState.FLAGGED):
            return

        if self.first_click:
            self.place_mines(row, col)
            self.first_click = False

        if self.mines[row][col]:
            self.end_game()
            return

        self.reveal(row, col)
        self.update_display()
        self.check_win()

    def right_click(self, row, col):
        if self.game_state != GameState.PLAYING or self.board[row][col] == CellState.REVEALED:
            return

        if self.board[row][col] == CellState.HIDDEN:
            self.board[row][col] = CellState.FLAGGED
            self.flags_placed += 1
        else:
            self.board[row][col] = CellState.HIDDEN
            self.flags_placed -= 1

        self.update_info()
        self.update_display()

    def reveal(self, row, col):
        if self.board[row][col] == CellState.REVEALED:
            return

        self.board[row][col] = CellState.REVEALED
        self.cells_revealed += 1

        if self.numbers[row][col] == 0:
            for nr, nc in self.get_neighbors(row, col):
                if self.board[nr][nc] == CellState.HIDDEN:
                    self.reveal(nr, nc)

    def update_display(self):
        for i in range(self.rows):
            for j in range(self.cols):
                btn = self.buttons[i][j]
                state = self.board[i][j]
                if state == CellState.REVEALED:
                    if self.mines[i][j]:
                        btn.config(text="💣", bg="red")
                    else:
                        num = self.numbers[i][j]
                        btn.config(text=str(num) if num > 0 else "", bg="lightgray")
                elif state == CellState.FLAGGED:
                    btn.config(text="🚩", bg="yellow")
                else:
                    btn.config(text="", bg="SystemButtonFace")

    def check_win(self):
        if self.cells_revealed == self.rows * self.cols - self.mine_count:
            self.game_state = GameState.WON
            self.bot_active = False
            self.bot_button.config(text="Start Bot", bg="green")
            messagebox.showinfo("Bravo!", "Ai câștigat!")

    def end_game(self):
        self.game_state = GameState.LOST
        self.bot_active = False
        self.bot_button.config(text="Start Bot", bg="green")
        for i in range(self.rows):
            for j in range(self.cols):
                if self.mines[i][j]:
                    self.buttons[i][j].config(text="💣", bg="red")
        messagebox.showinfo("Game Over", "Ai lovit o mină!")

    def update_info(self):
        remaining = self.mine_count - self.flags_placed
        status = {GameState.PLAYING: "În joc", GameState.WON: "Câștigat", GameState.LOST: "Pierdut"}[self.game_state]
        self.info_label.config(text=f"Mine rămase: {remaining} | Status: {status}")
        if self.bot_stats["moves"]:
            self.stats_label.config(text=f"Bot: Mișcări {self.bot_stats['moves']}, Dezvăluiri {self.bot_stats['reveals']}, Flaguri {self.bot_stats['flags']}")

    def toggle_bot(self):
        if self.first_click:
            messagebox.showwarning("Info", "Fă primul click manual.")
            return
        self.bot_active = not self.bot_active
        self.bot_button.config(text="Stop Bot" if self.bot_active else "Start Bot", bg="red" if self.bot_active else "green")
        if self.bot_active:
            self.run_bot()

    def update_bot_speed(self, val):
        self.bot_speed = float(val)

    def run_bot(self):
        def logic():
            while self.bot_active and self.game_state == GameState.PLAYING:
                if not self.bot_move():
                    self.bot_active = False
                    self.bot_button.config(text="Start Bot", bg="green")
                    break
                time.sleep(self.bot_speed)

        threading.Thread(target=logic, daemon=True).start()

    def bot_move(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != CellState.REVEALED:
                    continue
                neighbors = self.get_neighbors(i, j)
                flagged = [n for n in neighbors if self.board[n[0]][n[1]] == CellState.FLAGGED]
                hidden = [n for n in neighbors if self.board[n[0]][n[1]] == CellState.HIDDEN]

                if len(flagged) == self.numbers[i][j] and hidden:
                    nr, nc = hidden[0]
                    self.root.after(0, lambda r=nr, c=nc: self.left_click(r, c))
                    self.bot_stats["moves"] += 1
                    self.bot_stats["reveals"] += 1
                    self.root.after(0, self.update_info)
                    return True

        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != CellState.REVEALED:
                    continue
                neighbors = self.get_neighbors(i, j)
                flagged = [n for n in neighbors if self.board[n[0]][n[1]] == CellState.FLAGGED]
                hidden = [n for n in neighbors if self.board[n[0]][n[1]] == CellState.HIDDEN]
                if self.numbers[i][j] - len(flagged) == len(hidden) and hidden:
                    nr, nc = hidden[0]
                    self.root.after(0, lambda r=nr, c=nc: self.right_click(r, c))
                    self.bot_stats["moves"] += 1
                    self.bot_stats["flags"] += 1
                    self.root.after(0, self.update_info)
                    return True

        hidden_cells = [(i, j) for i in range(self.rows) for j in range(self.cols)
                        if self.board[i][j] == CellState.HIDDEN]
        if hidden_cells:
            row, col = random.choice(hidden_cells)
            self.root.after(0, lambda r=row, c=col: self.left_click(r, c))
            self.bot_stats["moves"] += 1
            self.bot_stats["reveals"] += 1
            self.root.after(0, self.update_info)
            return True

        return False

    def run(self):
        self.root.mainloop()

# PyAutoGUI (opțional, pentru automatizare externă)
def automate_with_pyautogui():
    print("Așază mouse-ul pe primul buton și apasă Enter...")
    input()
    pos = pyautogui.position()
    print(f"Poziția inițială: {pos}")
    for _ in range(3):
        pyautogui.click()
        time.sleep(0.5)
        pyautogui.move(30, 0)

if __name__ == "__main__":
    game = MinesweeperGame()
    game.run()
