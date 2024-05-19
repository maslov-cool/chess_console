WHITE = 1
BLACK = 2


def main():
    # Создаём шахматную доску
    board = Board()
    # Цикл ввода команд игроков
    while not board.mate():
        # Выводим положение фигур на доске
        print(board)
        # Подсказка по командам
        print('Команды:')
        print('    exit                               -- выход')
        print('    move <row> <col> <row1> <row1>     -- ход из клетки (row, col)')
        print('                                          в клетку (row1, col1)')
        # Выводим приглашение игроку нужного цвета
        if board.current_player_color() == WHITE:
            print('Ход белых:')
        else:
            print('Ход чёрных:')
        command = input()
        if command == 'exit':
            break
        move_type, row, col, row1, col1 = command.split()
        row, col, row1, col1 = int(row), int(col), int(row1), int(col1)
        if board.move_piece(row, col, row1, col1):
            print('Ход успешен')
        else:
            print('Координаты некорректы! Попробуйте другой ход!')


def correct_coords(row, col):
    """Функция проверяет, что координаты (row, col) лежат
    внутри доски"""
    return 0 <= row < 8 and 0 <= col < 8


# Удобная функция для вычисления цвета противника
def opponent(color):
    if color == WHITE:
        return BLACK
    return WHITE


class Board:
    def __init__(self):
        self.color = WHITE
        self.field = [[None] * 8 for _ in range(8)]
        self.field[0] = [
            Rook(WHITE), Knight(WHITE), Bishop(WHITE), Queen(WHITE),
            King(WHITE), Bishop(WHITE), Knight(WHITE), Rook(WHITE)
        ]
        self.field[1] = [
            Pawn(WHITE), Pawn(WHITE), Pawn(WHITE), Pawn(WHITE),
            Pawn(WHITE), Pawn(WHITE), Pawn(WHITE), Pawn(WHITE)
        ]
        self.field[6] = [
            Pawn(BLACK), Pawn(BLACK), Pawn(BLACK), Pawn(BLACK),
            Pawn(BLACK), Pawn(BLACK), Pawn(BLACK), Pawn(BLACK)
        ]
        self.field[7] = [
            Rook(BLACK), Knight(BLACK), Bishop(BLACK), Queen(BLACK),
            King(BLACK), Bishop(BLACK), Knight(BLACK), Rook(BLACK)
        ]
        self.not_go_rooks = [[0, 0], [0, 7], [7, 0], [7, 7], [0, 4], [7, 4]]

    def current_player_color(self):
        return self.color

    def __str__(self):
        s = ''
        s += '     +----+----+----+----+----+----+----+----+\n'
        for row in range(7, -1, -1):
            s += '  ' + str(row) + '  '
            for col in range(8):
                s += '| ' + self.cell(row, col) + ' '
            s += '|\n'
            s += '     +----+----+----+----+----+----+----+----+\n'
        s += '        '
        for col in range(8):
            s += str(col) + '    '
        s += '\n'
        return s

    def cell(self, row, col):
        """Возвращает строку из двух символов. Если в клетке (row, col)
        находится фигура, символы цвета и фигуры. Если клетка пуста,
        то два пробела."""
        piece = self.field[row][col]
        if piece is None:
            return '  '
        color = piece.get_color()
        c = 'w' if color == WHITE else 'b'
        return c + piece.char()

    def get_piece(self, row, col):
        if correct_coords(row, col):
            return self.field[row][col]
        else:
            return None

    def move_piece(self, row, col, row1, col1):
        '''Переместить фигуру из точки (row, col) в точку (row1, col1).
        Если перемещение возможно, метод выполнит его и вернёт True.
        Если нет --- вернёт False'''

        if not correct_coords(row, col) or not correct_coords(row1, col1):
            return False
        if row == row1 and col == col1:
            return False  # нельзя пойти в ту же клетку
        piece = self.field[row][col]
        if piece is None:
            return False
        if self.field[row1][col1] is None:
            if not piece.can_move(self, row, col, row1, col1):
                return False
        elif self.field[row1][col1].get_color() == opponent(piece.get_color()):
            if not piece.can_attack(self, row, col, row1, col1):
                return False
        else:
            return False
        self.field[row][col] = None  # Снять фигуру.
        self.field[row1][col1] = piece  # Поставить на новое место.
        self.color = opponent(self.color)
        if isinstance(self.field[row1][col1], Rook) and [row, col] in self.not_go_rooks:
            del self.not_go_rooks[self.not_go_rooks.index([row, col])]
        if isinstance(self.field[row1][col1], King) and [row, col] in self.not_go_rooks:
            del self.not_go_rooks[self.not_go_rooks.index([row, col])]
        return True

    def is_under_attack(self, row, col, color):
        '''Метод должен возврает True, если поле с координатами (row, col) находится под боем хотя
        бы одной фигуры цвета color.'''
        for i in self.field:
            for j in i:
                if j and j.get_color() == color and j.can_move(row, col, self.field):
                    return True
        return False

    def move_and_promote_pawn(self, row, col, row1, col1, char):
        # проверяем пешка ли
        if not isinstance(self.field[row][col], Pawn):
            return False
        # проверяем будет ли при ходе побита фигура
        if (self.field[row1][col1] is None and self.field[row][col].can_move(self, row, col, row1, col1)) or \
                (not self.field[row1][col1] is None and self.field[row][col].can_attack(self, row, col, row1, col1)
                 and self.field[row][col].get_color() != self.field[row1][col1].get_color()):
            if char == 'Q':
                self.field[row1][col1] = Queen(self.field[row][col].get_color())
            elif char == 'R':
                self.field[row1][col1] = Rook(self.field[row][col].get_color())
            elif char == 'B':
                self.field[row1][col1] = Bishop(self.field[row][col].get_color())
            elif char == 'N':
                self.field[row1][col1] = Knight(self.field[row][col].get_color())
            self.field[row][col] = None
            return True
        return False

    def castling0(self):
        if ([0, 0] in self.not_go_rooks and [0, 4] in self.not_go_rooks and isinstance(self.field[0][4], King)
                and isinstance(self.field[0][0], Rook) and
                self.field[0][4].get_color() == self.field[0][0].get_color() == self.color and all(
                    i is None for i in self.field[0][1:4])):
            self.field[0][2] = self.field[0][4]
            self.field[0][3] = self.field[0][0]
            self.field[0][4] = self.field[0][0] = None
            self.color = opponent(self.color)
            return True
        elif ([7, 0] in self.not_go_rooks and [7, 4] in self.not_go_rooks and isinstance(self.field[7][4], King)
              and isinstance(self.field[7][0], Rook) and
              self.field[7][0].get_color() == self.field[7][4].get_color() == self.color and all(
                    i is None for i in self.field[7][1:4])):
            self.field[7][2] = self.field[7][4]
            self.field[7][3] = self.field[7][0]
            self.field[7][4] = self.field[7][0] = None
            self.color = opponent(self.color)
            return True
        return False

    def castling7(self):
        if ([0, 7] in self.not_go_rooks and [0, 4] in self.not_go_rooks and isinstance(self.field[0][4], King)
                and isinstance(self.field[0][7], Rook) and
                self.field[0][4].get_color() == self.field[0][7].get_color() == self.color and all(
                    i is None for i in self.field[0][5:7])):
            self.field[0][6] = self.field[0][4]
            self.field[0][5] = self.field[0][7]
            self.field[0][4] = self.field[0][7] = None
            self.color = opponent(self.color)
            return True
        elif ([7, 7] in self.not_go_rooks and [7, 4] in self.not_go_rooks and isinstance(self.field[7][4], King)
              and isinstance(self.field[7][7], Rook) and
              self.field[7][4].get_color() == self.field[7][7].get_color() == self.color and all(
                    i is None for i in self.field[7][5:7])):
            self.field[7][6] = self.field[7][4]
            self.field[7][5] = self.field[7][7]
            self.field[7][4] = self.field[7][7] = None
            self.color = opponent(self.color)
            return True
        return False

    def shah_or_mate(self):
        r, c = 0, 0
        flag = False
        for i in range(8):
            for j in range(8):
                if isinstance(self.field[i][j], King) and self.field[i][j].get_color() == self.color:
                    r, c = i, j
                    flag = True
                    break
            if flag:
                break
        if not self.is_under_attack(r, c, opponent(self.color)):
            return False
        for i in range(8):
            for j in range(8):
                if (self.field[r][c].can_move(self.field, r, c, i, j) and
                        not self.is_under_attack(i, j, opponent(self.color))):
                    print('Шах!')
                    return False
        for i in range(8):
            for j in range(8):
                if self.field[i][j].get_color() == opponent(self.color) and \
                        self.field[i][j].can_attack(self.field, i, j, r, c):
                    for i1 in range(8):
                        for j1 in range(8):
                            if self.field[i1][j1].get_color() == self.color:
                                for n in range(abs(i - r)):
                                    for k in range(abs(j - c)):
                                        if self.field[i1][j1].can_move(self.field, i1, j1, n, k):
                                            print('Шах!')
                                            return False
        print('Мат!')
        return True


class Figure:
    def __init__(self, color):
        self.color = color

    def set_position(self, row, col):
        self.row = row
        self.col = col

    def get_color(self):
        return self.color

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


class Pawn(Figure):
    def char(self):
        return 'P'

    def can_move(self, board, row, col, row1, col1):
        # Пешка может ходить только по вертикали
        # "взятие на проходе" не реализовано
        if col != col1:
            return False

        # Пешка может сделать из начального положения ход на 2 клетки
        # вперёд, поэтому поместим индекс начального ряда в start_row.
        if self.color == WHITE:
            direction = 1
            start_row = 1
        else:
            direction = -1
            start_row = 6

        # ход на 2 клетки из начального положения
        if row == start_row:
            if row + 2 * direction != row1 and row + direction != row1:
                return False
        else:
            # ход на 1 клетку
            if row + direction != row1:
                return False

        for i in range(row + direction, row1 + direction, direction):
            if not board.get_piece(i, col1) is None:
                return False

        return True

    def can_attack(self, board, row, col, row1, col1):
        direction = 1 if (self.color == WHITE) else -1
        return (row + direction == row1
                and (col + 1 == col1 or col - 1 == col1))


class Knight(Figure):

    def char(self):
        return 'N'

    def can_move(self, board, row, col, row1, col1):
        if 0 <= row <= 7 and 0 <= col <= 7:
            if (row1 == row + 2 and col1 == col + 1) or (row1 == row + 2 and col1 == col - 1) or \
                    (row1 == row - 2 and col1 == col + 1) or (row1 == row - 2 and col1 == col - 1) or \
                    (row1 == row + 1 and col1 == col + 2) or (row1 == row + 1 and col1 == col - 2) or \
                    (row1 == row - 1 and col1 == col + 2) or (row1 == row - 1 and col1 == col - 2):
                return True
        return False


class Bishop(Figure):

    def char(self):
        return 'B'

    def can_move(self, board, row, col, row1, col1):
        if abs(row - row1) == abs(col - col1):
            direction_row = 1 if row1 > row else -1
            direction_col = 1 if col1 > col else -1
            for i in range(1, abs(row1 - row)):
                if not board.get_piece(row + direction_row * i, col + direction_col * i) is None:
                    return False
        return True


class Queen(Figure):

    def char(self):
        return 'Q'

    def can_move(self, board, row, col, row1, col1):
        if row != row1 and col == col1:
            direction = 1 if row1 > row else -1
            for i in range(row + direction, row1, 1 if row1 > row else -1):
                if not board.get_piece(i, col1) is None:
                    return False
        elif row == row1 and col != col1:
            direction = 1 if col1 > col else -1
            for i in range(col + direction, col1, direction):
                if not board.get_piece(row1, i) is None:
                    return False
        elif abs(row - row1) == abs(col - col1):
            direction_row = 1 if row1 > row else -1
            direction_col = 1 if col1 > col else -1
            for i in range(1, abs(row1 - row)):
                if not board.get_piece(row + direction_row * i, col + direction_col * i) is None:
                    return False
        else:
            return False

        if (not board.get_piece(row1, col1) is None and board.get_piece(row, col).get_color() ==
                board.get_piece(row1, col1).get_color()):
            return False

        return True


class Rook(Figure):

    def char(self):
        return 'R'

    def can_move(self, board, row, col, row1, col1):
        # Невозможно сделать ход в клетку, которая не лежит в том же ряду
        # или столбце клеток.
        if row != row1 and col != col1:
            return False

        if row != row1:
            direction = 1 if row1 > row else -1
            for i in range(row + direction, row1, 1 if row1 > row else -1):
                if not board.get_piece(i, col) is None:
                    return False
        else:
            direction = 1 if col1 > col else -1
            for i in range(col + direction, col1, direction):
                if not board.get_piece(row, i) is None:
                    return False

        return True


class King(Figure):

    def char(self):
        return 'K'

    def can_move(self, board, row, col, row1, col1):
        if abs(row - row1) <= 1 and abs(col - col1) <= 1 and board.get_piece(row1, col1) is None:
            return True
        return False


main()
