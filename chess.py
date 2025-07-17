import random
import copy

class ChessBot:
    def __init__(self):
        self.board = self.initialize_board()
        self.current_player = 'white'
        self.game_over = False
        self.winner = None
        
    def initialize_board(self):
        board = [[None for _ in range(8)] for _ in range(8)]
        for i in range(8):
            board[1][i] = 'bp'
            board[6][i] = 'wp'
        pieces = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
        for i, piece in enumerate(pieces):
            board[0][i] = 'b' + piece
            board[7][i] = 'w' + piece
        return board

    def print_board(self):
        piece_symbols = {
            'wk': '♔', 'wq': '♕', 'wr': '♖', 'wb': '♗', 'wn': '♘', 'wp': '♙',
            'bk': '♚', 'bq': '♛', 'br': '♜', 'bb': '♝', 'bn': '♞', 'bp': '♟'
        }
        print("\n  a b c d e f g h")
        for i in range(8):
            print(f"{8-i} ", end="")
            for j in range(8):
                piece = self.board[i][j]
                print(piece_symbols.get(piece, '·') + " ", end="")
            print(f"{8-i}")
        print("  a b c d e f g h\n")

    def pos_to_indices(self, pos):
        if len(pos) != 2:
            return None
        col = ord(pos[0].lower()) - ord('a')
        row = 8 - int(pos[1])
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None

    def indices_to_pos(self, row, col):
        return chr(ord('a') + col) + str(8 - row)

    def get_piece_color(self, piece):
        if piece is None:
            return None
        return 'white' if piece[0] == 'w' else 'black'

    # ========================= VALIDĂRI DE MUTARE =========================

    def is_valid_move(self, from_pos, to_pos):
        from_indices = self.pos_to_indices(from_pos)
        to_indices = self.pos_to_indices(to_pos)
        if not from_indices or not to_indices:
            return False

        from_row, from_col = from_indices
        to_row, to_col = to_indices
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]

        if piece is None:
            return False
        if self.get_piece_color(piece) != self.current_player:
            return False
        if target and self.get_piece_color(target) == self.current_player:
            return False

        piece_type = piece[1]
        if piece_type == 'p':
            if not self.is_valid_pawn_move(from_row, from_col, to_row, to_col, piece):
                return False
        elif piece_type == 'r' and not self.is_valid_rook_move(from_row, from_col, to_row, to_col):
            return False
        elif piece_type == 'n' and not self.is_valid_knight_move(from_row, from_col, to_row, to_col):
            return False
        elif piece_type == 'b' and not self.is_valid_bishop_move(from_row, from_col, to_row, to_col):
            return False
        elif piece_type == 'q' and not (self.is_valid_rook_move(from_row, from_col, to_row, to_col) or
                                        self.is_valid_bishop_move(from_row, from_col, to_row, to_col)):
            return False
        elif piece_type == 'k' and not self.is_valid_king_move(from_row, from_col, to_row, to_col):
            return False

        # NU permite mutări care își lasă regele în șah
        simulated_board = copy.deepcopy(self.board)
        simulated_board[to_row][to_col] = simulated_board[from_row][from_col]
        simulated_board[from_row][from_col] = None
        if self.is_king_in_check(self.current_player, simulated_board):
            return False

        return True

    def is_valid_pawn_move(self, fr, fc, tr, tc, piece):
        direction = -1 if piece[0] == 'w' else 1
        start_row = 6 if piece[0] == 'w' else 1
        if fc == tc:
            if tr == fr + direction and self.board[tr][tc] is None:
                return True
            if fr == start_row and tr == fr + 2 * direction and self.board[fr + direction][fc] is None and self.board[tr][tc] is None:
                return True
        elif abs(fc - tc) == 1 and tr == fr + direction and self.board[tr][tc] is not None:
            return True
        return False

    def is_valid_rook_move(self, fr, fc, tr, tc):
        if fr != tr and fc != tc:
            return False
        if fr == tr:
            for c in range(min(fc, tc) + 1, max(fc, tc)):
                if self.board[fr][c] is not None:
                    return False
        else:
            for r in range(min(fr, tr) + 1, max(fr, tr)):
                if self.board[r][fc] is not None:
                    return False
        return True

    def is_valid_knight_move(self, fr, fc, tr, tc):
        return (abs(fr - tr), abs(fc - tc)) in [(2, 1), (1, 2)]

    def is_valid_bishop_move(self, fr, fc, tr, tc):
        if abs(fr - tr) != abs(fc - tc):
            return False
        rdir = 1 if tr > fr else -1
        cdir = 1 if tc > fc else -1
        for i in range(1, abs(fr - tr)):
            if self.board[fr + i * rdir][fc + i * cdir] is not None:
                return False
        return True

    def is_valid_king_move(self, fr, fc, tr, tc):
        return abs(fr - tr) <= 1 and abs(fc - tc) <= 1

    # ========================= DETECȚIE ȘAH / MAT =========================

    def find_king(self, color, board=None):
        if board is None:
            board = self.board
        for r in range(8):
            for c in range(8):
                if board[r][c] == ('w' if color == 'white' else 'b') + 'k':
                    return r, c
        return None

    def is_king_in_check(self, color, board=None):
        if board is None:
            board = self.board
        king_pos = self.find_king(color, board)
        if not king_pos:
            return False
        kr, kc = king_pos
        enemy_color = 'black' if color == 'white' else 'white'
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece and self.get_piece_color(piece) == enemy_color:
                    from_pos = self.indices_to_pos(r, c)
                    to_pos = self.indices_to_pos(kr, kc)
                    old_player = self.current_player
                    self.current_player = enemy_color
                    if self.is_valid_move(from_pos, to_pos):
                        self.current_player = old_player
                        return True
                    self.current_player = old_player
        return False

    def is_checkmate(self, color):
        if not self.is_king_in_check(color):
            return False
        return len(self.get_all_valid_moves(color)) == 0

    # ========================= MUTĂRI, MINIMAX, AI =========================

    def make_move(self, from_pos, to_pos):
        if not self.is_valid_move(from_pos, to_pos):
            return False
        fr, fc = self.pos_to_indices(from_pos)
        tr, tc = self.pos_to_indices(to_pos)
        self.board[tr][tc] = self.board[fr][fc]
        self.board[fr][fc] = None
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        return True

    def get_all_valid_moves(self, color):
        moves = []
        old_player = self.current_player
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and self.get_piece_color(piece) == color:
                    from_pos = self.indices_to_pos(r, c)
                    self.current_player = color
                    for tr in range(8):
                        for tc in range(8):
                            to_pos = self.indices_to_pos(tr, tc)
                            if from_pos != to_pos and self.is_valid_move(from_pos, to_pos):
                                moves.append((from_pos, to_pos))
        self.current_player = old_player
        return moves

    def evaluate_board(self):
        piece_values = {'p': 1, 'n': 3, 'b': 3.2, 'r': 5, 'q': 9, 'k': 100}
        score = 0
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece:
                    val = piece_values[piece[1]]
                    if piece[0] == 'w':
                        score += val
                    else:
                        score -= val
        return score

    def minimax(self, depth, maximizing, alpha=-float('inf'), beta=float('inf')):
        if depth == 0 or self.is_checkmate('white') or self.is_checkmate('black'):
            return self.evaluate_board()
        color = 'white' if maximizing else 'black'
        moves = self.get_all_valid_moves(color)
        if not moves:
            return self.evaluate_board()
        if maximizing:
            max_eval = -float('inf')
            for f, t in moves:
                old_board = copy.deepcopy(self.board)
                old_player = self.current_player
                self.make_move(f, t)
                eval_score = self.minimax(depth - 1, False, alpha, beta)
                self.board = old_board
                self.current_player = old_player
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for f, t in moves:
                old_board = copy.deepcopy(self.board)
                old_player = self.current_player
                self.make_move(f, t)
                eval_score = self.minimax(depth - 1, True, alpha, beta)
                self.board = old_board
                self.current_player = old_player
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self, color, depth=3):
        moves = self.get_all_valid_moves(color)
        if not moves:
            return None
        best_move = None
        best_score = -float('inf') if color == 'white' else float('inf')
        for f, t in moves:
            old_board = copy.deepcopy(self.board)
            old_player = self.current_player
            self.make_move(f, t)
            score = self.minimax(depth - 1, color == 'black')
            self.board = old_board
            self.current_player = old_player
            if color == 'white' and score > best_score:
                best_score = score
                best_move = (f, t)
            elif color == 'black' and score < best_score:
                best_score = score
                best_move = (f, t)
        return best_move

    def play_game(self):
        print("Chess Bot Started! You are White. Format: e2 e4")
        while not self.game_over:
            self.print_board()
            if self.current_player == 'white':
                move = input("Your move: ")
                if move.lower() == 'quit':
                    break
                try:
                    f, t = move.split()
                    if not self.make_move(f, t):
                        print("Invalid move!")
                        continue
                except:
                    print("Wrong format!")
                    continue
                if self.is_checkmate('black'):
                    print("You won! Checkmate!")
                    break
            else:
                print("AI thinking...")
                move = self.get_best_move('black', 3)
                if move:
                    f, t = move
                    self.make_move(f, t)
                    print(f"AI moved: {f} -> {t}")
                    if self.is_checkmate('white'):
                        print("AI wins! Checkmate!")
                        break
                else:
                    print("AI resigns, you win!")
                    break


if __name__ == "__main__":
    ChessBot().play_game()
