class GameState():
    """
    This class is responsible for storing information about current state of chess game. 
    Responsible for determining the valid move.
    Keep a move log
    """

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
        self.moveFunctions = {
            'p': self.getPawnMoves,
            'R': self.getRookMoves,
            'N': self.getKnightMoves,
            'B': self.getBishopMoves,
            'Q': self.getQueenMoves,
            'K': self.getKingMoves
        }

        self.whiteToMove = True
        self.moveLog = []

        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

        self.checkMate = False
        self.staleMate = False

    def makeMove(self, move):
        """
        Takes a move ass parameter and executes it.
        Not works for castling, pawn promotion and en passant.
        """
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # Log move, for undo it later
        self.whiteToMove = not self.whiteToMove
        # update the kings' location
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        if move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

    def undoMove(self):
        """
        Undo the last move
        """
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # Update Kings' Location
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            if move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

    def getValidMoves(self):
        """
        All moves considering checks.
        """
        # 1. Generate all possible moves
        moves = self.getAllPossibleMoves()

        # 2. For each move, make the move
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])

            # 3. Generate all opponnent's move
            # 4. For all opponent's moves, see if they attack the king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                # 5. If they attack the King, not valid move
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:  # Either Checkmate or StaleMate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        return moves

    def inCheck(self):
        """
        Determine if current player is in check
        """
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, row, col):
        """
        Determine if the enemy can attack the square at (row, col)
        """
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == row and move.endCol == col:
                return True
        return False

    def getAllPossibleMoves(self):
        """
        All moves without considering checks.
        """
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.whiteToMove) or \
                        (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves)
        return moves

    def getPawnMoves(self, row, col, moves):
        """
        Get all pawn moves for pawn locate at row, col and add them to moves
        """
        if self.whiteToMove:
            if self.board[row - 1][col] == "--":
                # pawn can move forward 1 square
                moves.append(
                    Move(
                        (row, col),
                        (row - 1, col),
                        self.board
                    )
                )
                if row == 6 and self.board[row - 2][col] == "--":
                    # pawn can move 2 square forward
                    moves.append(
                        Move(
                            (row, col),
                            (row - 2, col),
                            self.board
                        )
                    )
            if col - 1 >= 0:
                # Capture to left
                if self.board[row - 1][col - 1][0] == 'b':
                    moves.append(
                        Move(
                            (row, col),
                            (row - 1, col - 1),
                            self.board
                        )
                    )
            if col + 1 <= 7:
                # Capture to right
                if self.board[row - 1][col + 1][0] == 'b':
                    moves.append(
                        Move(
                            (row, col),
                            (row - 1, col + 1),
                            self.board
                        )
                    )
        else:
            if self.board[row + 1][col] == "--":
                # Forward 1 squares
                moves.append(
                    Move(
                        (row, col),
                        (row + 1, col),
                        self.board
                    )
                )
                if row == 1 and self.board[row + 2][col] == "--":
                    # Forward 2 squares
                    moves.append(
                        Move(
                            (row, col),
                            (row + 2, col),
                            self.board
                        )
                    )
            if col - 1 >= 0:
                # capture left
                if self.board[row + 1][col - 1][0] == 'w':
                    moves.append(
                        Move(
                            (row, col),
                            (row + 1, col - 1),
                            self.board
                        )
                    )
            if col + 1 <= 7:
                if self.board[row + 1][col + 1][0] == 'w':
                    moves.append(
                        Move(
                            (row, col),
                            (row + 1, col + 1),
                            self.board
                        )
                    )
        # TODO: Add pawn promotion

    def getRookMoves(self, row, col, moves):
        """
        Get all rook moves for pawn locate at row, col and add them to moves
        """
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':
                        moves.append(
                            Move(
                                (row, col),
                                (endRow, endCol),
                                self.board
                            )
                        )
                    elif endPiece[0] == enemyColor:
                        moves.append(
                            Move(
                                (row, col),
                                (endRow, endCol),
                                self.board
                            )
                        )
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, row, col, moves):
        """
        Get all knight moves for pawn locate at row, col and add them to moves
        """
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = row + m[0]
            endCol = col + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(
                        Move(
                            (row, col),
                            (endRow, endCol),
                            self.board
                        )
                    )

    def getBishopMoves(self, row, col, moves):
        """
        Get all bishop moves for pawn locate at row, col and add them to moves
        """
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':
                        moves.append(
                            Move(
                                (row, col),
                                (endRow, endCol),
                                self.board
                            )
                        )
                    elif endPiece[0] == enemyColor:
                        moves.append(
                            Move(
                                (row, col),
                                (endRow, endCol),
                                self.board
                            )
                        )
                        break
                    else:
                        break
                else:
                    break

    def getQueenMoves(self, row, col, moves):
        """
        Get all queen moves for pawn locate at row, col and add them to moves
        """
        self.getBishopMoves(row, col, moves)
        self.getRookMoves(row, col, moves)

    def getKingMoves(self, row, col, moves):
        """
        Get all king moves for pawn locate at row, col and add them to moves
        """
        kingMoves = (
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        )
        allyColor = "w" if self.whiteToMove else "b"
        for m in kingMoves:
            endRow = row + m[0]
            endCol = col + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(
                        Move(
                            (row, col),
                            (endRow, endCol),
                            self.board
                        )
                    )


class Move():
    # maps keys to values
    ranksToRows = {
        "1": 7, "2": 6, "3": 5, "4": 4,
        "5": 3, "6": 2, "7": 1, "8": 0
    }

    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {
        "a": 0, "b": 1, "c": 2, "d": 3,
        "e": 4, "f": 5, "g": 6, "h": 7
    }

    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * \
            100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + \
            " " + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
