import pyautogui
import time
import json
from dataclasses import dataclass
from typing import List

@dataclass
class Point:
    x: int
    y: int

class MinimaxTicTacToeBot:
    def __init__(self):
      from dataclasses import dataclass

      @dataclass
      class Point:
        x: int
        y: int

      self.Point = Point  



      with open("coords.json") as f:
          raw_cells = json.load(f)
      self.cells = {
          int(k): {'center': Point(v['center']['x'], v['center']['y'])}
          for k, v in raw_cells.items()
      }

      self.board = [0] * 9
      self.bot_symbol = 1
      self.player_symbol = 2
      self.bot_goes_first = True

      self.winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]

    pyautogui.PAUSE = 0.4


    def ask_who_is_bot(self):
        choice = input("Vrei ca botul să fie X (primul) sau O (al doilea)? [X/O]: ").strip().upper()
        if choice == 'O':
            self.bot_symbol = 2
            self.player_symbol = 1
            self.bot_goes_first = False
            print("Botul va juca cu O (al doilea)")
        else:
            self.bot_symbol = 1
            self.player_symbol = 2
            self.bot_goes_first = True
            print("Botul va juca cu X (primul)")

    def click_cell(self, cell_index: int):
        cell = self.cells[cell_index]['center']
        pyautogui.click(cell.x, cell.y)
        print(f"Botul a mutat pe celula {cell_index}")
        self.board[cell_index] = self.bot_symbol
        time.sleep(0.5)

    def get_empty_cells(self) -> List[int]:
        return [i for i in range(9) if self.board[i] == 0]

    def is_board_full(self) -> bool:
        return all(cell != 0 for cell in self.board)

    def check_winner(self) -> int:
        for combo in self.winning_combinations:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != 0:
                return self.board[combo[0]]
        return 0

    def minimax(self, depth: int, is_maximizing: bool) -> int:
        winner = self.check_winner()
        if winner == self.bot_symbol:
            return 10 - depth
        if winner == self.player_symbol:
            return depth - 10
        if self.is_board_full():
            return 0

        if is_maximizing:
            best_score = -float('inf')
            for cell in self.get_empty_cells():
                self.board[cell] = self.bot_symbol
                score = self.minimax(depth + 1, False)
                self.board[cell] = 0
                best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for cell in self.get_empty_cells():
                self.board[cell] = self.player_symbol
                score = self.minimax(depth + 1, True)
                self.board[cell] = 0
                best_score = min(score, best_score)
            return best_score

    def find_best_move(self) -> int:
        best_score = -float('inf')
        best_move = -1
        for cell in self.get_empty_cells():
            self.board[cell] = self.bot_symbol
            score = self.minimax(0, False)
            self.board[cell] = 0
            if score > best_score:
                best_score = score
                best_move = cell
        return best_move

    def get_player_move(self) -> int:
        input("Pune mouse-ul peste celula în care ai mutat și apasă Enter...")
        pos = pyautogui.position()
        for index, cell in self.cells.items():
            cx, cy = cell['center'].x, cell['center'].y
            if abs(pos.x - cx) < 50 and abs(pos.y - cy) < 50:
                if self.board[index] == 0:
                    self.board[index] = self.player_symbol
                    print(f"Tu ai mutat în celula {index}")
                    return index
                else:
                    print("Celula este deja ocupată. Încearcă din nou.")
                    return self.get_player_move()
        print("Poziție invalidă! Pune mouse-ul pe o celulă.")
        return self.get_player_move()

    def play_game(self):
        print("Apasă Ctrl+C pentru a ieși oricând")
        try:
            while True:
                self.board = [0] * 9
                self.ask_who_is_bot()
                print("Joc început")

                if self.bot_goes_first:
                    move = self.find_best_move()
                    self.click_cell(move)

                while True:
                    self.get_player_move()
                    if self.check_winner() == self.player_symbol:
                        print("Ai câștigat!")
                        break
                    if self.is_board_full():
                        print("Remiză!")
                        break

                    move = self.find_best_move()
                    if move != -1:
                        self.click_cell(move)
                    if self.check_winner() == self.bot_symbol:
                        print("Botul a câștigat!")
                        break
                    if self.is_board_full():
                        print("Remiză!")
                        break

                print("\n--- Meci terminat ---\n")

        except KeyboardInterrupt:
            print("\nJoc oprit manual.")

if __name__ == "__main__":
    bot = MinimaxTicTacToeBot()
    bot.play_game()
