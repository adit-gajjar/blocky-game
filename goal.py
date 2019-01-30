"""Assignment 2 - Blocky

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This file contains the Goal class hierarchy.
"""

from typing import List, Tuple
from block import Block


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class BlobGoal(Goal):
    """A goal to create the largest connected blob of this goal's target
    colour, anywhere within the Block.
    """

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
           -1  if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        size = len(board)
        col = pos[0]
        row = pos[1]

        # first check if the position is valid.
        if validate_position(pos, size):

            # check if its the right colour
            if board[col][row] == self.colour and visited[col][row] == -1:
                visited[col][row] = 1
                blob_size = 0
                # now make recursive calls to each adjacent unit cell
                blob_size += 1 + self._adjacent_blob_size(pos, board, visited)
                return blob_size
            else:
                return 0

        else:
            return 0

    def _adjacent_blob_size(self, pos, board, visited) -> int:
        """ This is a helper method for _undiscovered_blob_size which serves
            the purposes of recersively calling _undiscovered_blob_size on all
            of its adjacent unit cells.
        """
        col, row = pos[0], pos[1]
        total = 0
        total += self._undiscovered_blob_size((col - 1, row), board, visited)
        total += self._undiscovered_blob_size((col, row - 1), board, visited)
        total += self._undiscovered_blob_size((col + 1, row), board, visited)
        total += self._undiscovered_blob_size((col, row + 1), board, visited)
        return total

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.
        The score is always greater than or equal to 0. This score find the
        biggest undiscovered blob and returns the corresponding score.
        """
        board = board.flatten()
        size = len(board)
        visited = duplicate_flatten(size)
        score = 0
        # check every block in every column.
        for col in range(size):
            for row in range(size):
                if board[col][row] == self.colour and visited[col][row] != 1:
                    # recursively call to adjacent cells and returns their score
                    score = update_score(score, self._undiscovered_blob_size((
                        col, row), board, visited))
                # if the current location is not the colour set cell to 0.
                elif board[col][row] != self.colour:
                    visited[col][row] = 0

        return score

    def description(self) -> str:
        """ A description of BlobGoal."""
        return " get many blocks of given colour adjacent"


class PerimeterGoal(Goal):
    """
    Represents a goal, which evaluates a score based on how many blocks
    of a given colour are touching the edge of the board. Additionally
    a unit cell on a corner counts for double points.
    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """

    def score(self, board: Block) -> int:
        """ Returns the score, which is scored by counting all of the block
            of a colour, additionally one in the corner count for double points.
        """
        score = 0
        board = board.flatten()
        size = len(board)
        for col in range(size):
            if col == 0 or col == size - 1:  # check the entire row.
                score += self._check_row(col, board)
            else:  # only check the perimeter if not the top or bottom row.
                if board[col][0] == self.colour:
                    score += 1
                if board[col][size - 1] == self.colour:
                    score += 1
        return score + self.corner_score(size, board)

    def corner_score(self, size: int,
                     board: List[List[Tuple[int, int, int]]]) -> int:
        """
        This a helper method for perimeter goal that checks all of the corners
        as they account for double points.
        """
        score = 0
        bound = size - 1
        corners = [(0, 0), (0, bound), (bound, 0), (bound, bound)]
        for corner in corners:
            if board[corner[0]][corner[1]] == self.colour:
                score += 1
        return score

    def _check_row(self, col, board) -> int:
        """
        This is a helper method for the score method of perimeter goal, which
        checks the row to count how many block are touching the perimeter.
        """
        score = 0
        for row in range(len(board)):
            if board[col][row] == self.colour:
                score += 1
        return score

    def description(self) -> str:
        """ Gives a description of the Perimeter Goal."""
        return "put units of a given colour on the perimeter of the board."


def duplicate_flatten(size: int) -> List[List[int]]:
    """
    This is a helper method of the score method of the BlobGoal, it creates
    a flatten representation on the board of the same <size>, but with -1 as the
    value for each cell.
    """
    duplicate = []
    for _ in range(size):
        temp = [-1] * size
        duplicate.append(temp)
    return duplicate


def validate_position(position: Tuple[int, int], bound: int) -> bool:
    """
    This is a helper function function for the score method of the BlobGoal, it
    returns whether or not the given <position> is a valid coordinate.
    """
    if position[0] < 0 or position[0] >= bound:
        return False
    if position[1] < 0 or position[1] >= bound:
        return False
    return True


def update_score(best_score: int, new_score: int) -> int:
    """
    This is a helper method which returns the updates version of the score,
    depending whether the <new_score> is greater than the current <best_score>
    """
    if new_score > best_score:
        return new_score
    else:
        return best_score


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing',
            'block', 'goal', 'player', 'renderer'
        ],
        'max-attributes': 15
    })
