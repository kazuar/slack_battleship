
import time
import random
import numpy as np

BOARD_SIZE = 5

WIN = 2
SEA = 0
SHIP = 1
HIT = -1
NO_HIT = -2

SHAPES = [
    np.ones((1,1)),
    np.ones((2,1)),
    np.ones((1,2)),
    np.ones((1,3)),
    np.ones((1,4)),
]

class Player(object):
    def __init__(self, player_name, size = BOARD_SIZE):
        self._player_name = player_name
        self._board = np.zeros((BOARD_SIZE, BOARD_SIZE))

        for shape in SHAPES:
            shape_added = False
            while not shape_added:
                rand_col = random.randint(0, BOARD_SIZE - 1)
                rand_row = random.randint(0, BOARD_SIZE - 1)
                shape_added = self._add_shape(shape, (rand_col, rand_row))

    def _add_shape(self, shape, xy_coord):
        try:
            size_x, size_y = np.shape(shape)
            coor_x, coor_y = xy_coord
            end_x, end_y   = (coor_x + size_x), (coor_y + size_y)
            if int(self._board[coor_x:end_x, coor_y:end_y].sum()) > 0:
                return False
            self._board[coor_x:end_x, coor_y:end_y] = self._board[coor_x:end_x, coor_y:end_y] + shape
            return True
        except Exception:
            return False

    def player_name(self):
        return self._player_name

    def show(self, for_oponen):
        for row in self._board:
            print " ".join([str(int(cell)) for cell in row])

    def guess(self, x, y):
        val = int(self._board[x][y])
        if val == 0:
            self._board[x][y] = NO_HIT
        elif val == 1:
            self._board[x][y] = HIT
        return val

    def has_any_ships(self):
        return SHIP in np.unique(self._board)

    def get_board_rows(self, hide_ships = False):
        rows = []
        for row in self._board:
            values = []
            for cell in row:
                value = int(cell)
                if hide_ships and value == SHIP:
                    value = SEA
                values.append(str(value))
            rows.append(" ".join(values))
        return rows

class BattleshipGame(object):

    def __init__(self):
        self._current_player = None
        return

    def _get_first_player(self):
        players = [self._player1, self._player2]

        print "getting first player"

        return random.choice(players)

    def current_player(self):
        if not self._current_player:
            return None
        return self._current_player

    def _get_current_players(self):
        current_player = self._current_player
        opponent = self._player2 if self._player1.player_name() == self._current_player.player_name() else self._player1
        return self._current_player, opponent

    def start_game(self, player1, player2):
        print "starting game"
        self._player1 = Player(player1)
        self._player2 = Player(player2)

        self._current_player = self._get_first_player()

        print self._current_player

    def get_boards(self):
        # current_player, opponent = self._get_current_players()

        board1_rows = self._player1.get_board_rows()
        board2_rows = self._player2.get_board_rows(hide_ships = True)

        return board1_rows, board2_rows

    def turn(self, x, y):
        # self.print_boards()

        print "-" * 100
        print "\n"

        current_player, opponent = self._get_current_players()
        result = opponent.guess(x, y)

        print "{0} plays against {1}: {2}, {3}".format(current_player.player_name(), opponent.player_name(), x, y)
        print "result:", result, type(result)

        if not opponent.has_any_ships():
            return WIN

        self._current_player = opponent

        print "-" * 100
        print "\n"

        return result

# def main():
#     battle_ship_game = BattleshipGame()

#     battle_ship_game.start_game("x", "y")

#     battle_ship_game.print_boards()

# if __name__ == '__main__':
#     main()
