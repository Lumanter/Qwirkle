from tile import Tile
from position import Position
from restriction_tile import TileRestriction


class Board:
    """ The game board manages the state of the board and the played
        positions.

        Attributes:
            board(:obj:`list` of :obj:`Tile`): Two-dimensional list of tiles or zeros.
            played_positions(:obj:`list` of :obj:`Position`): List of the positions played.

    """

    def __init__(self, board = [[0]]):
        """ The constructor can receive a board. Default board is empty.

            Args:
                board(:obj:`list` of :obj:`Tile`): Two-dimensional list of tiles or zeros.

        """
        self.board = board
        self.played_positions = []
        if board != [[0]]:
            self.played_positions = self.get_played_positions(board)

    def get_played_positions(self, board):
        """ Returns all played positions in a board.

            Args:
                board(:obj:`list` of :obj:`Tile`): Two-dimensional list of tiles or zeros.

            Returns:
                :obj:`list` of :obj:`Position`: List of played  positions.

        """
        played_positions = []
        for row in range(len(board)):
            for col in range(len(board[0])):
                if board[row][col]:
                    played_position = Position(row, col)
                    played_positions.append(played_position)
        return played_positions

    def get_playable_positions(self, play_steps):
        """ Returns all playable positions of the board, given the player
            tile moves in the turn.

            Args:
                play_steps(:obj:`PlaySteps`): Tile movements made by a player.

            Returns:
                :obj:`list` of :obj:`Position`: List of playable  positions.

        """
        restriction = None
        if len(play_steps) == 1:
            restriction = TileRestriction('same row or col')
            restriction.row = play_steps.positions[0].row
            restriction.col = play_steps.positions[0].col
        if len(play_steps) >= 2:
            if play_steps.positions[0].row == play_steps.positions[1].row:
                restriction = TileRestriction('same row')
                restriction.row = play_steps.positions[0].row
            else:
                restriction = TileRestriction('same col')
                restriction.row = play_steps.positions[0].col

        playable_positions = []
        for played_position in self.played_positions:
            adjacent_empty_positions = self.get_adjacent_empty_positions(self.board, played_position)
            playable_positions.extend(adjacent_empty_positions)

        playable_positions = self.filter_positions(playable_positions, restriction)

        return playable_positions

    def filter_positions(self, positions, tile_restriction):
        """ Filters a list of positions based on a tile restriction.

            Args:
                positions(:obj:`list` of :obj:`Position`): List of positions to filter.
                position(:obj:'TileRestriction'): Restriction reference to filter.

            Returns:
                :obj:`list` of :obj:`Position`: List of filtered positions.

        """
        # not need to filter when restriction is None
        if not tile_restriction:
            return positions

        restriction = tile_restriction.restriction

        filtered_positions = []
        for position in positions:
            valid_tile = False

            if restriction == 'same row':
                valid_tile = (position.row == tile_restriction.row)
            elif restriction == 'same col':
                valid_tile = (position.col == tile_restriction.col)
            elif restriction == 'same row or col':
                valid_tile = (position.row == tile_restriction.row or position.col == tile_restriction.col)

            if valid_tile:
                filtered_positions.append(position)
        return filtered_positions

    def get_adjacent_empty_positions(self, board, position):
        """ Returns the empty positions adjacent to a position.
            Looks up, down, right and left of the position.

            Args:
                board(:obj:`list` of :obj:`Tile`): Two-dimensional list of tiles or zeros.
                position(:obj:'Position'): Board position of row and column.

            Returns:
                :obj:`list` of :obj:`Position`: List of adjacent empty positions.

        """
        adjacent_empty_positions = []
        row, col = position.row, position.col

        # left empty position?
        if col > 0 and not self.board[row][col - 1]:
            adjacent_empty_positions.append(Position(row, col - 1))

        # right empty position?
        if col < len(self.board[0]) - 1 and not self.board[row][col + 1]:
            adjacent_empty_positions.append(Position(row, col + 1))

        # up empty position?
        if row > 0 and not self.board[row - 1][col]:
            adjacent_empty_positions.append(Position(row - 1, col))

        rows = len(self.board)
        # down empty position?
        if row < len(self.board) - 1 and not self.board[row + 1][col]:
            adjacent_empty_positions.append(Position(row + 1, col))

        return adjacent_empty_positions

    def play_tile(self, tile, position):
        """ Determines if a tile move if valid. Checks vertically and horizontally.

            Args:
                tile(:obj:'Tile'): Played tile.
                position(:obj:'Position'): Board row and column to insert the tile.

        """
        self.board[position.row][position.col] = tile
        self.played_positions.append(position)

    def adjust_padding(self):
        """ Inserts padding to the board if needed. Is needed when a tile is in
            at the most outer layer of the board (first or last column or row).
            Void spaces are needed always at the outer layer to make be able to
            make moves.

        """
        top = first = 0

        # check top padding
        if any(self.board[top]):  # any tile in first row?
            self.board.insert(0, [0] * len(self.board[0]))

        # check bottom padding
        bottom = len(self.board) - 1
        if any(self.board[bottom]):  # any tile in last row?
            self.board.append([0] * len(self.board[0]))

        # check left padding
        for row in self.board:
            if row[first]:  # any tile in first column?
                for i in range(len(self.board)):
                    self.board[i].insert(0, 0)
                break;

        # check right padding
        last = len(self.board[0]) - 1
        for row in self.board:
            if row[last]:  # any tile in last column?
                for i in range(len(self.board)):
                    self.board[i].append(0)
                break;

    def is_valid_move(self, tile, position):
        """ Determines if a tile move if valid. Checks vertically and horizontally.

            Args:
                tile(:obj:'Tile'): Tile used to know its shape and color.
                position(:obj:'Position'): Board position of row and column.

            Returns:
                bool: True if the move is valid, false otherwise.

        """
        board = self.board
        row = position.row
        col = position.col

        if len(board[0]) == 1:
            valid_position = (row == 0 and col == 0)
            return valid_position

        rows = len(board)
        cols = len(board[0])

        out_of_index = (row < 0) or (row >= rows) or (col < 0) or (col >= cols)
        if out_of_index:
            #print("out of index")
            return False

        space_taken = board[row][col]
        if space_taken:
            #print("space taken")
            return False

        # at least 1 adjacent tile?
        adjacent_tile = row != 0 and board[row - 1][col] or \
                        row != rows - 1 and board[row + 1][col] or \
                        col != 0 and board[row][col - 1] or \
                        col != cols - 1 and board[row][col + 1]
        if not adjacent_tile:
            #print("no adjacent tile")
            return False

        # verify horizontal line
        horizontal_line = self.get_adjacent_horizontal_line(board, tile, row, col)
        if not self.is_valid_line(horizontal_line):
            #print("invalid horizontal line")
            #print(horizontal_line)
            return False

        # verify vertical line
        vertical_line = self.get_adjacent_vertical_line(board, tile, row, col)
        if not self.is_valid_line(vertical_line):
            #print("invalid vertical line")
            #print(vertical_line)
            return False

        # its a valid move, meets all rules
        return True

    def get_adjacent_horizontal_line(self, board, tile, row, col):
        """ Returns the tiles linked vertically to a tile and its position.
            Searches up and down from the given position.

            Args:
                board(:obj:`list` of :obj:`Tile`): Two-dimensional list of tiles or zeros.
                tile(:obj:'Tile'): Reference tile to determine the adjacent tiles.
                row(int): Board row to determine the adjacent tiles.
                col(int): Board column to determine the adjacent tiles.

            Returns:
                :obj:`list` of :obj:`Tile`: List of tiles linked vertically to the tile.

        """
        horizontal_line = [tile]

        # append right side
        col_index = col + 1
        while col_index < len(board[0]) and board[row][col_index]:
            horizontal_line.append(board[row][col_index])
            col_index += 1

        # append left side
        col_index = col - 1
        while col_index >= 0 and board[row][col_index]:
            horizontal_line.append(board[row][col_index])
            col_index -= 1
        return horizontal_line

    def get_adjacent_vertical_line(self, board, tile, row, col):
        """ Returns the tiles linked horizontally to a tile and its position.
            Searches to the right and left from the given position

            Args:
                board(:obj:`list` of :obj:`Tile`): Two-dimensional list of tiles or zeros.
                tile(:obj:'Tile'): Reference tile to determine the adjacent tiles.
                row(int): Board row to determine the adjacent tiles.
                col(int): Board column to determine the adjacent tiles.

            Returns:
                :obj:`list` of :obj:`Tile`: List of tiles linked horizontally to the tile.

        """
        vertical_line = [tile]

        # append upper side
        row_index = row + 1
        while row_index < len(board) and board[row_index][col]:
            vertical_line.append(board[row_index][col])
            row_index += 1

        # append lower side
        row_index = row - 1
        while row_index >= 0 and board[row_index][col]:
            vertical_line.append(board[row_index][col])
            row_index -= 1
        return vertical_line

    def is_valid_line(self, line):
        """ Indicates if a line of tiles is valid. A line is valid when
            all the tiles share either shape or color.

            Args:
                line(:obj:`list` of :obj:`Tile`): The first parameter.

            Returns:
                True if the line is valid, false otherwise.

        """
        # lines of 1 or 0 tiles are valid
        if len(line) <= 1:
            return True

        # use first two tiles to determine common aspect
        common_aspect = None
        common_value = None
        if line[0].shape == line[1].shape:
            common_aspect = 'shape'
            common_value = line[0].shape
        if line[0].color == line[1].color:
            common_aspect = 'color'
            common_value = line[0].color

        # first 2 tiles are incompatible
        if not common_aspect:
            return False

        # set to look for duplicates
        seen_tiles = set()
        for tile in line:
            # duplicate tile?
            duplicate = str(tile) in seen_tiles

            # has same color or shape as the rest of the line?
            invalid_tile = False
            if common_aspect == 'shape':
                invalid_tile = tile.shape != common_value
            else:
                invalid_tile = tile.color != common_value

            if duplicate or invalid_tile:
                return False
            else:
                seen_tiles.add(str(tile))
        return True

    def __str__(self):
        to_string = ""
        for row in self.board:
            to_string += str(row) + "\n"
        return to_string

    def __len__(self):
        return len(self.board)