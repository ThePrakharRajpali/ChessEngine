"""
This class is responsible for storing information about current state of chess game. 
Responsible for determining the valid move.
Keep a move log
"""


class GameState():
    def __init__(self):
        # Board is 8x8 2D List,
        # Each Element of the list has 2 Characters
        # First Character - Color of Piece - 'b' or 'w'
        # Second Character - Type of Piece - 'p', 'R', 'N', 'B', 'Q', 'K'
        # "--" - represent empty space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.whiteToMove = True
        self.moveLog = []
