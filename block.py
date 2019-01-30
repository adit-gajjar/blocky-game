""" Assignment 2 - Blocky

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This file contains the Block class, the main data structure used in the game.
"""
from typing import Optional, Tuple, List
import random
import math
from renderer import COLOUR_LIST, TEMPTING_TURQUOISE, BLACK, colour_name


HIGHLIGHT_COLOUR = TEMPTING_TURQUOISE
FRAME_COLOUR = BLACK


class Block:
    """A square block in the Blocky game.

    === Public Attributes ===
    position:
        The (x, y) coordinates of the upper left corner of this Block.
        Note that (0, 0) is the top left corner of the window.
    size:
        The height and width of this Block.  Since all blocks are square,
        we needn't represent height and width separately.
    colour:
        If this block is not subdivided, <colour> stores its colour.
        Otherwise, <colour> is None and this block's sublocks store their
        individual colours.
    level:
        The level of this block within the overall block structure.
        The outermost block, corresponding to the root of the tree,
        is at level zero.  If a block is at level i, its children are at
        level i+1.
    max_depth:
        The deepest level allowed in the overall block structure.
    highlighted:
        True iff the user has selected this block for action.
    children:
        The blocks into which this block is subdivided.  The children are
        stored in this order: upper-right child, upper-left child,
        lower-left child, lower-right child.
    parent:
        The block that this block is directly within.

    === Representation Invariations ===
    - len(children) == 0 or len(children) == 4
    - If this Block has children,
        - their max_depth is the same as that of this Block,
        - their size is half that of this Block,
        - their level is one greater than that of this Block,
        - their position is determined by the position and size of this Block,
          as defined in the Assignment 2 handout, and
        - this Block's colour is None
    - If this Block has no children,
        - its colour is not None
    - level <= max_depth
    """
    position: Tuple[int, int]
    size: int
    colour: Optional[Tuple[int, int, int]]
    level: int
    max_depth: int
    highlighted: bool
    children: List['Block']
    parent: Optional['Block']

    def __init__(self, level: int,
                 colour: Optional[Tuple[int, int, int]] = None,
                 children: Optional[List['Block']] = None) -> None:
        """Initialize this Block to be an unhighlighted root block with
        no parent.

        If <children> is None, give this block no children.  Otherwise
        give it the provided children.  Use the provided level and colour,
        and set everything else (x and y coordinates, size,
        and max_depth) to 0.  (All attributes can be updated later, as
        appropriate.)
        """
        self.position = (0, 0)
        self.size = 0
        self.level = level
        self.max_depth = 0
        self.highlighted = False
        self.parent = None

        # attributes that depend on whether or not block is subdivided
        if children is None:  # if the block is not subdivided
            self.colour = colour
            self.children = []
        else:  # if the block is sub_divided.

            self.children = children
            set_parent(self, self.children)
            self.colour = None

    def rectangles_to_draw(self) -> List[Tuple[Tuple[int, int, int],
                                               Tuple[float, float],
                                               Tuple[float, float],
                                               int]]:
        """
        Return a list of tuples describing all of the rectangles to be drawn
        in order to render this Block.

        This includes (1) for every undivided Block:
            - one rectangle in the Block's colour
            - one rectangle in the FRAME_COLOUR to frame it at the same
              dimensions, but with a specified thickness of 3
        and (2) one additional rectangle to frame this Block in the
        HIGHLIGHT_COLOUR at a thickness of 5 if this block has been
        selected for action, that is, if its highlighted attribute is True.

        The rectangles are in the format required by method Renderer.draw.
        Each tuple contains:
        - the colour of the rectangle
        - the (x, y) coordinates of the top left corner of the rectangle
        - the (height, width) of the rectangle, which for our Blocky game
          will always be the same
        - an int indicating how to render this rectangle. If 0 is specified
          the rectangle will be filled with its colour. If > 0 is specified,
          the rectangle will not be filled, but instead will be outlined in
          the FRAME_COLOUR, and the value will determine the thickness of
          the outline.

        The order of the rectangles does not matter.
        """
        size = (float(self.size), float(self.size))
        position = (float(self.position[0]), float(self.position[1]))

        if len(self.children) == 0:  # if  block is not subdivided.
            rec_in_blocks_colour = (self.colour, position, size, 0)
            frame_colour = (FRAME_COLOUR, position, size, 3)
            rec_in_highlight = (HIGHLIGHT_COLOUR, position, size, 5)

            if self.highlighted:
                return [rec_in_blocks_colour, rec_in_highlight, frame_colour]
            return [rec_in_blocks_colour, frame_colour]

        else:  # Recursive Call
            list_of_rec = []
            for child in self.children:
                list_of_rec.extend(child.rectangles_to_draw())
            if self.highlighted:
                list_of_rec.append((HIGHLIGHT_COLOUR, position, size, 5))
            return list_of_rec

    def swap(self, direction: int) -> None:
        """Swap the child Blocks of this Block.

        If <direction> is 1, swap vertically.  If <direction> is 0, swap
        horizontally. If this Block has no children, do nothing.
        """
        if len(self.children) > 0:
            old = self.children
            if direction == 1:  # vertical swap
                new_children = [old[3], old[2], old[1], old[0]]
            else:  # horizontal swap
                new_children = [old[1], old[0], old[3], old[2]]
            self.children = new_children
            self.update_block_locations(self.position, self.size)

    def rotate(self, direction: int) -> None:
        """Rotate this Block and all its descendants.

        If <direction> is 1, rotate clockwise.  If <direction> is 3, rotate
        counterclockwise. If this Block has no children, do nothing.
        """
        if len(self.children) == 0:  # rotating a solid block does nothing.
            pass
        elif direction == 1:
            for child in self.children:
                child.rotate(direction)
            old = self.children
            new = [old[1], old[2], old[3], old[0]]
            self.children = new
            self.update_block_locations(self.position, self.size)
        elif direction == 3:
            for child in self.children:
                child.rotate(direction)
            old = self.children
            new = [old[3], old[0], old[1], old[2]]
            self.children = new
            self.update_block_locations(self.position, self.size)

    def smash(self) -> bool:
        """Smash this block.

        If this Block can be smashed,
        randomly generating four new child Blocks for it.  (If it already
        had child Blocks, discard them.)
        Ensure that the RI's of the Blocks remain satisfied.

        A Block can be smashed iff it is not the top-level Block and it
        is not already at the level of the maximum depth.

        Return True if this Block was smashed and False otherwise.
        """
        if self.level == 0 or self.level == self.max_depth:
            return False
        else:
            new_upper_left = random_init(self.level + 1, self.max_depth)
            new_upper_right = random_init(self.level + 1, self.max_depth)
            new_low_right = random_init(self.level + 1, self.max_depth)
            new_low_left = random_init(self.level + 1, self.max_depth)
            new_children = [new_upper_right, new_upper_left,
                            new_low_left, new_low_right]
            self.children = new_children
            self.colour = None
            set_parent(self, self.children)
            self.update_block_locations(self.position, self.size)
            return True

    def update_block_locations(self, top_left: Tuple[float, float],
                               size: float) -> None:
        """
        Update the position and size of each of the Blocks within this Block.

        Ensure that each is consistent with the position and size of its
        parent Block.

        <top_left> is the (x, y) coordinates of the top left corner of
        this Block.  <size> is the height and width of this Block.
        """
        if len(self.children) == 0:
            self.size = size
            self.position = top_left
        else:
            self.size = size
            self.position = top_left
            self.update_child_block_locations(top_left, round(size / 2.0))

    def update_child_block_locations(self, top_left: Tuple[float, float],
                                     size: float) -> None:
        """ A helper method to update blocks which sets up all the recursive
            calls for a given blocks sub-divided blocks to set all the location
            attributes.
        """

        top_right = (top_left[0] + size, top_left[1])
        low_left = (top_left[0], top_left[1] + size)
        low_right = (top_left[0] + size, top_left[1] + size)
        # Upper Right Block
        self.children[0].update_block_locations(top_right, size)
        # Upper Left Block
        self.children[1].update_block_locations(top_left, size)
        # Lower Left Block
        self.children[2].update_block_locations(low_left, size)
        #Lower Right BLock
        self.children[3].update_block_locations(low_right, size)

    def get_selected_block(self, location: Tuple[float, float], level: int) \
            -> 'Block':
        """Return the Block within this Block that includes the given location
        and is at the given level. If the level specified is lower than
        the lowest block at the specified location, then return the block
        at the location with the closest level value.

        <location> is the (x, y) coordinates of the location on the window
        whose corresponding block is to be returned.
        <level> is the level of the desired Block.  Note that
        if a Block includes the location (x, y), and that Block is subdivided,
        then one of its four children will contain the location (x, y) also;
        this is why <level> is needed.

        Preconditions:
        - 0 <= level <= max_depth
        """
        if level > self.max_depth:
            # Level greater than max_depth so we set it to max_depth
            level = self.max_depth

        closest_distance = 100000
        closest_block = self

        for child in self.children:
            curr = child.get_selected_block(location, level)
            if curr.level <= level:
                # our compare the distance with the center of the block
                new_dist = get_distance(get_center(curr), location)
                if new_dist < closest_distance:
                    closest_distance = new_dist
                    closest_block = curr
        return closest_block

    def flatten(self) -> List[List[Tuple[int, int, int]]]:
        """Return a two-dimensional list representing this Block as rows
        and columns of unit cells.

        Return a list of lists L, where, for 0 <= i, j < 2^{self.level}
            - L[i] represents column i and
            - L[i][j] represents the unit cell at column i and row j.
        Each unit cell is represented by 3 ints for the colour
        of the block at the cell location[i][j]

        L[0][0] represents the unit cell in the upper left corner of the Block.
        """
        # base case has an extra condition for unit cell
        if len(self.children) == 0:
            if self.level != self.max_depth:
                sol = []
                for _ in range(2 ** (self.max_depth - self.level)):
                    temp = [self.colour] * (2 ** (self.max_depth - self.level))
                    sol.append(temp)
                return sol
            else:   # if the block is a unit cell
                return [[self.colour]]

        else:
            return combine_nested_list(self.flatten_child())

    def flatten_child(self) -> List[List[List[Tuple[int, int, int]]]]:
        """This is a helper method for flatten, which takes care of the
            recursive step, by calling the flatten method on all of a given
            blocks children.
        """
        childs = self.children
        top_right = childs[0].flatten()
        top_left = childs[1].flatten()
        bot_left = childs[2].flatten()
        bot_right = childs[3].flatten()
        return [top_right, top_left, bot_left, bot_right]


def combine_nested_list(childs: List) -> List:
    """
    This is a helper for the flatten method. It takes, a list of lists
    where the elements of the list correspond on the all the children on the
    top right, top_left, bot_left, and bot_right respectively, and combines
    them into one list.
    """
    top_right = childs[0]
    top_left = childs[1]
    bot_left = childs[2]
    bot_right = childs[3]

    for i in range(len(top_right)):
        top_left[i].extend(bot_left[i])
    for i in range(len(top_right)):
        top_right[i].extend(bot_right[i])
    top_left.extend(top_right)

    return top_left


def get_center(block: 'Block') -> Tuple[float, float]:
    """
    This is a helper method for the get selected_block method. It gives
    the location of the center of the <block> and returns a tuple.
    """
    size = block.size / 2
    return (block.position[0] + size, block.position[1] + size)


def get_distance(block_pos, pointer_pos) -> float:
    """
    This is a helper method for get_selected_block which return the distance
    between a the center of a block and the location of the mouse.<block_pos>:
    is the position of the block, and pointer_pos is the postion of the mouse.
    """
    delta_distance_x = abs(block_pos[0] - pointer_pos[0]) ** 2
    delta_distance_y = abs(block_pos[1] - pointer_pos[1]) ** 2
    distance = math.sqrt(delta_distance_x + delta_distance_y)

    return distance


def random_init(level: int, max_depth: int) -> 'Block':
    """Return a randomly-generated Block with level <level> and subdivided
    to a maximum depth of <max_depth>.

    Throughout the generated Block, set appropriate values for all attributes
    except position and size.  They can be set by the client, using method
    update_block_locations.

    Precondition:
        level <= max_depth
    """
    # If this Block is not already at the maximum allowed depth, it can
    # be subdivided. Use a random number to decide whether or not to
    # subdivide it further.
    subdivide_constant = math.exp(-0.25 * level)
    rand = random.random()

    if rand >= subdivide_constant or level == max_depth:  # Generate solid block
        block_colour = COLOUR_LIST[random.randint(0, 3)]
        new_block = Block(level, block_colour, None)
        new_block.max_depth = max_depth
        return new_block
    else:   # Generate sub divided block
        new_block = Block(level, None, None)
        new_block.max_depth = max_depth
        new_block.children = get_list_of_children(level, max_depth)
        set_parent(new_block, new_block.children)
        return new_block


def get_list_of_children(level: int, max_depth: int) -> List['Block']:
    """ This a helper function for the random_init function. It takes care of
        the recurice step by calling random_init 4 times one for each children
        then returns them.
    """
    upper_right_block = random_init(level + 1, max_depth)
    upper_left_block = random_init(level + 1, max_depth)
    lower_left_block = random_init(level + 1, max_depth)
    lower_right_block = random_init(level + 1, max_depth)
    return [upper_right_block, upper_left_block,
            lower_left_block, lower_right_block]


def set_parent(parent: 'Block', children: List['Block']) -> None:
    """ A Helper method of random_init_ which set the parent attribute of the
        subdivided blocks to the be the block in which they are contained
    """
    for child in children:
        child.parent = parent


def attributes_str(b: Block, verbose) -> str:
    """Return a str that is a concise representation of the attributes of <b>.

    Include attributes position, size, and level.  If <verbose> is True,
    also include highlighted, and max_depth.

    Note: These are attributes that every Block has.
    """
    answer = f'pos={b.position}, size={b.size}, level={b.level}, '
    if verbose:
        answer += f'highlighted={b.highlighted}, max_depth={b.max_depth}'
    return answer


def print_block(b: Block, verbose=False) -> None:
    """Print a text representation of Block <b>.

    Include attributes position, size, and level.  If <verbose> is True,
    also include highlighted, and max_depth.

    Precondition: b is not None.
    """
    print_block_indented(b, 0, verbose)


def print_block_indented(b: Block, indent: int, verbose) -> None:
    """Print a text representation of Block <b>, indented <indent> steps.

    Include attributes position, size, and level.  If <verbose> is True,
    also include highlighted, and max_depth.

    Precondition: b is not None.
    """
    if len(b.children) == 0:
        # b a leaf.  Print its colour and other attributes
        print(f'{"  " * indent}{colour_name(b.colour)}: ' +
              f'{attributes_str(b, verbose)}')
    else:
        # b is not a leaf, so it doesn't have a colour.  Print its
        # other attributes.  Then print its children.
        print(f'{"  " * indent}{attributes_str(b, verbose)}')
        for child in b.children:
            print_block_indented(child, indent + 1, verbose)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-io': ['print_block_indented'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing',
            'block', 'goal', 'player', 'renderer', 'math'
        ],
        'max-attributes': 15
    })

    # This tiny tree with one node will have no children, highlighted False,
    # and will have the provided values for level and colour; the initializer
    # sets all else (position, size, and max_depth) to 0.
    b0 = Block(0, COLOUR_LIST[2])
    # Now we update position and size throughout the tree.
    b0.update_block_locations((0, 0), 750)
    print("=== tiny tree ===")
    # We have not set max_depth to anything meaningful, so it still has the
    # value given by the initializer (0 and False).
    print_block(b0, True)

    b1 = Block(0, children=[
        Block(1, children=[
            Block(2, COLOUR_LIST[3]),
            Block(2, COLOUR_LIST[2]),
            Block(2, COLOUR_LIST[0]),
            Block(2, COLOUR_LIST[0])
        ]),
        Block(1, COLOUR_LIST[2]),
        Block(1, children=[
            Block(2, COLOUR_LIST[1]),
            Block(2, COLOUR_LIST[1]),
            Block(2, COLOUR_LIST[2]),
            Block(2, COLOUR_LIST[0])
        ]),
        Block(1, children=[
            Block(2, COLOUR_LIST[0]),
            Block(2, COLOUR_LIST[2]),
            Block(2, COLOUR_LIST[3]),
            Block(2, COLOUR_LIST[1])
        ])
    ])
    b1.update_block_locations((0, 0), 750)
    print("\n=== handmade tree ===")
    # Similarly, max_depth is still 0 in this tree.  This violates the
    # representation invariants of the class, so we shouldn't use such a
    # tree in our real code, but we can use it to see what print_block
    # does with a slightly bigger tree.
    print_block(b1, True)

    # Now let's make a random tree.
    # random_init has the job of setting all attributes except position and
    # size, so this time max_depth is set throughout the tree to the provided
    # value (3 in this case).
    b2 = random_init(0, 3)
    # Now we update position and size throughout the tree.
    b2.update_block_locations((0, 0), 750)
    print("\n=== random tree ===")
    # All attributes should have sensible values when we print this tree.
    print_block(b2, True)
