"""Beta-Go: Course project for CSC111 Winter 2023

Authors:
Henry "TJ" Chen
Dmitrii Vlasov
Ming Yau (Oscar) Lam
Duain Chhabra

Date: April 3, 2023

Version: pre-Alpha

Module Description
==================

This module contains python classes which represent the actual components to
a game of Go - the board and the stones.

Copyright and Usage Information
===============================

This file was developed as part of the course project for CSC111 Winter 2023.
Feel free to test it out, but please contact us to obtain permission if you
intend to redistribute it or use it for your own work.
"""

# TODO: rewrite so that the board starts with the complete graph (maybe not, coz running time)
from __future__ import annotations
from typing import Optional


class Board:
    """
    A class that represents the game board.

    Attributes:
        size (int): The size of the board (i.e. the number of rows and columns).
        grid (list): A 2D list representing the board, containing Stone objects.
    """

    def __init__(self, size: int = 9):
        """
        Initializes a Board object. Populates all valid positions with "imaginary stones" of
        neither colour - in reality, these stones would not exist on the board - it is
        our way of representing an empty board. Then, update all the stones to have the correct
        neighbours.

        Args:
            size (int): The size of the board. Defaults to 9.
        """
        self.size = size
        self.grid = [[Stone(x, y) for y in range(size)] for x in range(size)]

        for column in self.grid:
            for stone in column:
                if stone.x + 1 < size:
                    stone.add_neighbour(self.get_stone(stone.x + 1, stone.y))
                if stone.x - 1 >= 0:
                    stone.add_neighbour(self.get_stone(stone.x - 1, stone.y))
                if stone.y + 1 < size:
                    stone.add_neighbour(self.get_stone(stone.x, stone.y + 1))
                if stone.y - 1 >= 0:
                    stone.add_neighbour(self.get_stone(stone.x, stone.y - 1))

    def __getitem__(self, position: tuple[int, int]):
        """
        Returns the Stone object at the specified position.

        Args:
            position (tuple): A tuple containing the x and y coordinates of the Stone object.

        Returns:
            Stone: The Stone object at the specified position.
        """
        x, y = position
        return self.grid[x][y]

    def add_stone(self, x: int, y: int, color: str = "Neither"):
        """
        Adds a Stone object to the board at the specified position.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.
            color (str): The color of the stone. Defaults to "Neither".
        """
        self.grid[x][y].color = color

    def get_stone(self, x: int, y: int):
        """Return the stone situated at the given coordinates"""
        return self.grid[x][y]

    # pretty useless methods
    def remove_stones(self, stones: list[Stone]):
        """
        Removes the specified Stone objects from the board.

        Args:
            stones (list): A list of Stone objects to remove.
        """
        for stone in stones:
            self.grid[stone.x][stone.y].die()

    def get_dead_stones(self):
        """
        Returns a list of Stone objects that should be removed from the board.

        Returns:
            list: A list of Stone objects that should be removed.
        """
        dead_stones = []
        for x in range(self.size):
            for y in range(self.size):
                stone = self.grid[x][y]
                if stone.color != "Neither" and stone.count_neighbours() >= stone.max_num_neighbours:
                    dead_stones.append(stone)
        return dead_stones

    def __str__(self):
        """Print a visual representation of the board."""
        ans = "-" * (self.size * 2 + 1) + '\n'
        for y in range(self.size):
            row = "|"
            for x in range(self.size):
                stone = self.get_stone(x, y)
                if stone.color == "Black":
                    row += "○"
                elif stone.color == "White":
                    row += "●"
                else:
                    row += " "
                row += "|"
            ans += row + '\n'
            ans += "-" * (self.size * 2 + 1) + '\n'
        return ans

    def print_max_neighbours(self):
        """for debugging"""
        ans = "-" * (self.size * 2 + 1) + '\n'
        for y in range(self.size):
            row = "|"
            for x in range(self.size):
                stone = self.get_stone(x, y)
                row += str(stone.max_num_neighbours)
                row += "|"
            ans += row + '\n'
            ans += "-" * (self.size * 2 + 1) + '\n'
        return ans

    def board_to_move_sequence(self) -> list[tuple[int, int, int]]:
        """Convert a board state into a sequence of moves, store as a list of tuples
        NOTE: This does not store the sequence that the moves were actually played in
        """
        sequence = []
        i = 0
        for row in self.grid:
            for move in row:
                sequence.append((i, move.x, move.y))
                i += 1
        return sequence

    def is_valid_move(self, x: int, y: int, color: str) -> bool:
        """Check if a coordinate is valid for the board. (It does not overwrite any stone, is not placed in a location
        that leads to instant death, and within boundaries of the board. It does not mutate the board
        Raises ValueError if color is not 'White' or 'Black'
        """
        if color not in {'Black', 'White'}:
            raise ValueError
        elif self.get_stone(x, y).color != "Neither":
            return False
        elif x < 0 or x > 8 or y < 0 or y > 8:
            return False
        else:
            self.get_stone(x, y).color = color
            if self.get_stone(x, y).check_is_dead(set()):
                self.get_stone(x, y).color = 'Neither'
                return False
            else:
                self.get_stone(x, y).color = 'Neither'
                return True

    def calculate_score(self: Board) -> list:
        """Calculates the score for both players.
        """
        black_score, white_score = 0.0, 0.0
        black_territory, white_territory = 0, 0
        black_territory_cord, white_territory_cord = [], []

        for x in range(self.size):
            for y in range(self.size):
                stone = self.get_stone(x, y)
                # This code is relevant if you want to count the stones as well
                # if stone.color == "Black":
                #     black_score += 1
                # elif stone.color == "White":
                #     white_score += 1
                # else:

                # Captured stones are not counted as territory
                territory_owner = self.get_territory_owner(x, y)
                if territory_owner == "Black":
                    black_territory += 1
                    black_territory_cord.append((x, y))
                elif territory_owner == "White":
                    white_territory += 1
                    white_territory_cord.append((x, y))

        # WIP for dead stones
        # for i in get_dead_cells(board, "Black"):
        #     white_territory_cord.append(i)
        # for i in get_dead_cells(board, "White"):
        #     black_territory_cord.append(i)

        black_score += black_territory
        white_score += white_territory
        return [("Black score:", black_score, "WhiteScore:", white_score), black_territory_cord, white_territory_cord]

    def get_territory_owner(self: Board, x, y) -> str:
        """Determines the owner of the territory at the given coordinates."""
        def single_territory_owner(x, y, visited):
            """
            Using a smilara approach from A3
            """
            if (x, y) in visited:  # if we have already visited this stone, return an empty set
                return set()
            visited.add((x, y))

            neighbors = self.get_stone(x, y).get_neighbours()  # get the neighbours of the stone
            result = set()
            for nx, ny in neighbors:
                if self.is_valid_coord(nx, ny) and (nx, ny) not in visited:
                    stone = self.get_stone(nx, ny)
                    if stone.color == "Neither":
                        result = result.union(single_territory_owner(nx, ny, visited))
                    else:
                        result.add(stone.color)
            return result

        visited = set()
        stone_colors = single_territory_owner(x, y, visited)
        if len(stone_colors) == 1:
            return next(iter(stone_colors))
        else:
            return "Neither"

    def get_dead_cells(self, color) -> list[tuple[int, int]]:
        """Function to get dead cells for a given color on a board.
           WIP and it does not work yet. or capture stones."""
        dead_cells = []

        for x in range(self.size):
            for y in range(self.size):
                stone = self.get_stone(x, y)
                if stone.color == color:
                    liberties = self.get_stone(x, y).get_liberties(color)
                    if liberties == 0:
                        dead_cells.append((x, y))
        print("dead cells", dead_cells, "color", color)
        return dead_cells


class Stone:
    """
    A class representing a stone on a game board.

    Attributes:
        color (str): The color of the stone ("Black", "White", or "Neither").
        x (int): The x position of the stone on the board.
        y (int): The y position of the stone on the board.
        neighbours (dict): A dict of neighbouring Stone objects with (x, y) as keys.

    Methods:
        add_neighbour(neighbor): Adds a neighbour to the stone.
        remove_neighbour(neighbor): Removes a neighbour from the stone.
        count_neighbours(): Returns the number of neighbours the stone has.
        die(): Removes the stone and its connections from the board.
    """

    color: str
    x: int
    y: int
    neighbours: dict[tuple[int, int], Stone]
    max_num_neighbours: int

    def __init__(self, x: int, y: int, color: str = "Neither"):
        """
        Initializes a new stone with the specified color and position.

        Args:
            color (str, optional): The color of the stone. Defaults to "Neither".
            x (int): The x position of the stone on the board.
            y (int): The y position of the stone on the board.
        """
        self.color = color
        self.neighbours = {}
        self.x = x
        self.y = y
        max_neighbours = 4  # default for stones not on edge or corner
        if x == 0 or x == 8:  # stone is on left or right edge
            max_neighbours = 3
        elif y == 0 or y == 8:  # stone is on top or bottom edge
            max_neighbours = 3
        if (x == 0 and y == 0) or (x == 0 and y == 8) or (x == 8 and y == 0) or (x == 8 and y == 8):
            max_neighbours = 2  # stone is in a corner
        self.max_num_neighbours = max_neighbours
        # TODO: maybe make it work for other sizes of boards? also potentially cash the whole thing

    def __str__(self):
        return f'Stone on coordinates {self.x}, {self.y} is {self.color} and has {self.count_neighbours()} neighbours.'

    def add_neighbour(self, neighbour: Stone):
        """
        Adds a neighbour to the stone if it is adjacent to the stone.

        Args:
            neighbour (Stone): The neighbouring stone to add.
        """
        # Check if the neighbor is adjacent to the current stone
        if abs(self.x - neighbour.x) + abs(self.y - neighbour.y) == 1:
            self.neighbours[neighbour.x, neighbour.y] = neighbour
            neighbour.neighbours[self.x, self.y] = self
        else:
            print('You fucked up the neighbours')
            raise Exception

    def remove_neighbour(self, neighbour: Stone):
        """
        Removes a neighbour from the stone.

        Effectively deletes the connection between two stones.

        Args:
            neighbour (Stone): The neighbouring stone to remove.
        """
        del self.neighbours[(neighbour.x, neighbour.y)]
        del neighbour.neighbours[(self.x, self.y)]

    def count_neighbours(self):
        """
        Returns the number of neighbours the stone has.

        Returns:
            int: The number of neighbours the stone has.
        """
        return len(self.neighbours)

    def get_neighbours(self):
        """
        Returns a set of neighbouring Stone objects.

        Returns:
            set: A set of neighbouring Stone objects.
        """
        return self.neighbours

    # TODO: potentially move to Stone
    def update_neighbours(self):
        """
        Updates the neighboring Stone objects for each Stone object on the board.
        """
        neighbours = self.get_neighbours()
        for neighbour in neighbours:
            if neighbour.color != "Neither":
                self.add_neighbour(neighbour)
            else:
                self.remove_neighbour(neighbour)

    # TODO: potentially move to Board
    def die(self):
        """
        Removes the stone and its connections from the board.
        """
        for neighbour in self.neighbours.values():
            neighbour.remove_neighbour(self)
        self.color = "Neither"
        self.neighbours = {}

    def check_is_dead(self,visited:set[Stone])-> bool:
        if len(self.neighbours)<self.max_num_neighbours:
            return False
        elif all(((neighbour.color!=self.color) or (neighbour in visited)) for neighbour in self.neighbours.values()):
            return True
        else:
            visited.add(self)
            bools=[]
            for neighbour in self.neighbours.values():
                if neighbour not in visited:
                    bools.append(neighbour.check_is_dead(visited))
            return any(bools)

    def get_liberties(self, color) -> int:
        """Returns the number of liberties the stone has.
        TODO: Experimental Function"""
        liberties = 0
        for neighbour in self.neighbours.values():
            if neighbour.color == "Neither":
                liberties += 1
            elif neighbour.color != color:
                liberties += 1
        return liberties



if __name__ == '__main__':
    # Create a new 9x9 board
    board = Board(9)
    # print(board[(1, 5)])
    # print(board)
    # board.add_stone(1, 5, "Black")
    # print(board[(1, 5)])
    # print(board)
    # board.add_stone(1, 6, "White")
    # print(board[(1, 5)])
    # print(board[(1, 6)])
    # # print(board)
    # print(board.print_max_neighbours())
