"""Assignment 2 - Blocky

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This file contains the player class hierarchy.
"""

import random
from typing import Optional
import pygame
from renderer import Renderer
from block import Block
from goal import Goal

TIME_DELAY = 600


class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    renderer:
        The object that draws our Blocky board on the screen
        and tracks user interactions with the Blocky board.
    id:
        This player's number.  Used by the renderer to refer to the player,
        for example as "Player 2"
    goal:
        This player's assigned goal for the game.
    """
    renderer: Renderer
    id: int
    goal: Goal

    def __init__(self, renderer: Renderer, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.renderer = renderer
        self.id = player_id

    def make_move(self, board: Block) -> int:
        """Choose a move to make on the given board, and apply it, mutating
        the Board as appropriate.

        Return 0 upon successful completion of a move, and 1 upon a QUIT event.
        """
        raise NotImplementedError


class HumanPlayer(Player):
    """A human player.

    A HumanPlayer can do a limited number of smashes.

    === Public Attributes ===
    num_smashes:
        number of smashes which this HumanPlayer has performed
    renderer:
        The object that draws our Blocky board on the screen
        and tracks user interactions with the Blocky board.
    id:
        This player's number.  Used by the renderer to refer to the player,
        for example as "Player 2"
    goal:
        This player's assigned goal for the game.
    === Representation Invariants ===
    num_smashes >= 0
    """
    # === Private Attributes ===
    # _selected_block
    #     The Block that the user has most recently selected for action;
    #     changes upon movement of the cursor and use of arrow keys
    #     to select desired level.
    # _level:
    #     The level of the Block that the user selected
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0

    # The total number of 'smash' moves a HumanPlayer can make during a game.
    MAX_SMASHES = 1

    num_smashes: int
    _selected_block: Optional[Block]
    _level: int

    def __init__(self, renderer: Renderer, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        super().__init__(renderer, player_id, goal)
        self.num_smashes = 0

        # This HumanPlayer has done no smashes yet.
        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._selected_block = None

    def process_event(self, board: Block,
                      event: pygame.event.Event) -> Optional[int]:
        """Process the given pygame <event>.

        Identify the selected block and mark it as highlighted.  Then identify
        what it is that <event> indicates needs to happen to <board>
        and do it.

        Return
           - None if <event> was not a board-changing move (that is, if was
             a change in cursor position, or a change in _level made via
            the arrow keys),
           - 1 if <event> was a successful move, and
           - 0 if <event> was an unsuccessful move (for example in the case of
             trying to smash in an invalid location or when the player is not
             allowed further smashes).
        """
        # Get the new "selected" block from the position of the cursor
        block = board.get_selected_block(pygame.mouse.get_pos(), self._level)
        # Remove the highlighting from the old "_selected_block"
        # before highlighting the new one
        if self._selected_block is not None:
            self._selected_block.highlighted = False
        self._selected_block = block
        self._selected_block.highlighted = True

        # Since get_selected_block may have not returned the block at
        # the requested level (due to the level being too low in the tree),
        # set the _level attribute to reflect the level of the block which
        # was actually returned.
        self._level = block.level
        if event.type == pygame.MOUSEBUTTONDOWN:
            block.rotate(event.button)
            return 1
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if block.parent is not None:
                    self._level -= 1
                return None

            elif event.key == pygame.K_DOWN:
                if len(block.children) != 0:
                    self._level += 1
                return None

            elif event.key == pygame.K_h:
                block.swap(0)
                return 1

            elif event.key == pygame.K_v:
                block.swap(1)
                return 1

            elif event.key == pygame.K_s:
                if self.num_smashes >= self.MAX_SMASHES:
                    print('Can\'t smash again!')
                    return 0
                if block.smash():
                    self.num_smashes += 1
                    return 1
                else:
                    print('Tried to smash at an invalid depth!')
                    return 0

    def make_move(self, board: Block) -> int:
        """Choose a move to make on the given board, and apply it, mutating
        the Board as appropriate.

        Return 0 upon successful completion of a move, and 1 upon a QUIT event.

        This method will hold focus until a valid move is performed.
        """
        self._level = 0
        self._selected_block = board

        # Remove all previous events from the queue in case the other players
        # have added events to the queue accidentally.
        pygame.event.clear()

        # Keep checking the moves performed by the player until a valid move
        # has been completed. Draw the board on every loop to draw the
        # selected block properly on screen.
        while True:
            self.renderer.draw(board, self.id)
            # loop through all of the events within the event queue
            # (all pending events from the user input)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 1

                result = self.process_event(board, event)
                self.renderer.draw(board, self.id)
                if result is not None and result > 0:
                    # un-highlight the selected block
                    self._selected_block.highlighted = False
                    return 0


class RandomPlayer(Player):
    """
    A random player.

    This player makes random choices, and has no limit on the number of smash
    operations.

    === Public Attributes ===
    num_smashes:
        number of smashes which this RandomPlayer has available.
    renderer:
        The object that draws our Blocky board on the screen
        and tracks user interactions with the Blocky board.
    id:
        This player's number.  Used by the renderer to refer to the player,
        for example as "Player 2"
    goal:
        This player's assigned goal for the game.

    === Representation Invariants ===
        nums_smashes == 1

    """
    def __init__(self, renderer: Renderer, player_id: int, goal: Goal) -> None:
        Player.__init__(self, renderer, player_id, goal)
        self.num_smashes = 1

    def make_move(self, board: Block):
        """
        randomly chooses a move to make on the given board, and apply it
        mutating the Board as appropriate. Return 0 upon successful completion
        of a move.
        """
        # select a random block and highlight it.
        rand_block = select_random_block(board)
        rand_block.highlighted = True
        self.renderer.draw(board, self.id)
        pygame.time.wait(TIME_DELAY)
        choice = random.randint(0, 4)

        if rand_block.level == rand_block.max_depth or rand_block.level == 0:
            # Random player has chosen to smash an invalid block thus its move
            # is forfeited
            if choice == 4:
                pass
            else:
                perform_move(rand_block, choice)
        else:
            perform_move(rand_block, choice)
        rand_block.highlighted = False
        self.renderer.draw(board, self.id)
        return 0


class SmartPlayer(Player):
    """
        A Smart player.

        This player makes 'smart' decisions based on testing out a number of
        random , this number is determined by the <difficulty> of the smart
        player. A smartplayer is not allowed to perform a smash move.

        === Public Attributes ===
        num_smashes:
            number of smashes which this SmartPlayer has available
        renderer:
            The object that draws our Blocky board on the screen
            and tracks user interactions with the Blocky board.
        id:
            This player's number.  Used by the renderer to refer to the player,
            for example as "Player 2"
        goal:
            This player's assigned goal for the game.
        moves_to_check:
            This is the number of moves that the smart player checks before
            selecting the optimal move.
        === Representaion Invariant ===
            num_smashes == 0

        """
    def __init__(self, renderer: 'Renderer', player_id: int,
                 goal: 'Goal', difficulty: int):

        Player.__init__(self, renderer, player_id, goal)
        self.num_smashes = 0
        self.moves_to_check = set_moves(difficulty)

    def make_move(self, board: Block) -> int:
        """
        Make a move based off testing a number of random moves based on the
        smart players difficulty level, and picking the best move. Returns
        0 when it makes a successful move.
        """
        best_block = None
        best_move = None
        best_score = -(2 ** 5)  # lower bound on the score.

        curr_score = self.goal.score(board)

        for _ in range(self.moves_to_check):

            temp_block = select_random_block(board)
            move = random.randint(0, 3)  # 4 not included as no smash allowed
            perform_move(temp_block, move)
            new_score = self.goal.score(board)
            if (new_score - curr_score) >= best_score:
                best_block = temp_block
                best_move = move
                best_score = new_score - curr_score
            undo_move(temp_block, move)

        # Apply the visual changes on the board
        best_block.highlighted = True
        self.renderer.draw(board, self.id)
        pygame.time.wait(TIME_DELAY)
        perform_move(best_block, best_move)
        best_block.highlighted = False
        self.renderer.draw(board, self.id)

        return 0


def undo_move(board: 'Block', option: int):
    """
    This is a helper fucnction for the make_move method for SmartPlayer.
    given a <board>, and a move represented by <option> this function perform
    the opposite to restore the board back to its original state.
    """
    if option == 0:
        perform_move(board, 0)
    elif option == 1:
        perform_move(board, 1)
    elif option == 2:
        perform_move(board, 3)
    elif option == 3:
        perform_move(board, 2)


def set_moves(difficulty: int) -> int:
    """
    This a helper function for the constructor of the SmartPLayer class.
    It returns an int which represents the number of moves the SmartPlayer
    checks before making a move based on its <difficulty>

    precondition:
        0 <= difficulty
    """
    if difficulty == 0:
        return 5
    elif difficulty == 1:
        return 10
    elif difficulty == 2:
        return 25
    elif difficulty == 3:
        return 50
    elif difficulty == 4:
        return 100
    else:
        return 150


def perform_move(block: 'Block', option: int) -> None:
    """
    This is a helper function for make_move in the RandomPlayer class, and it
    makes a move on <block> based on the value of option.

    preconditions:
        0 <= option <= 4
    """
    if option == 0:  # vertical swap
        block.swap(0)
    elif option == 1:  # horizontal swap
        block.swap(1)
    elif option == 2:  # rotate clockwise
        block.rotate(1)
    elif option == 3:  # rotate counter clockwise
        block.rotate(3)
    else:  # perform smash operation.
        block.smash()


def select_random_block(board: 'Block') -> 'Block':
    """
    This is a helper function for the method make_move in the RandomPlayer class
    it returns a random Block located in <board>
    """
    if len(board.children) > 0 or board.level == 0:
        # if the block is subdivided or is the main block.
        choice = random.randint(0, 4)
        if 0 <= choice <= 3:  # pick possibly one of boards children
            return select_random_block(board.children[choice])
        else:  # return the parent block
            return board
    else:
        # block is not subdivided.
        return board

if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing',
            'block', 'goal', 'player', 'renderer',
            'pygame'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
