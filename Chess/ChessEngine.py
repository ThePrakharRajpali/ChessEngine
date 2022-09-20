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

        self.enpassantPossible = ()  # Coordinates of square where enpassant is possible

        self.inCheck = False
        self.pins = []
        self.checks = []

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

        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        # En passant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"

        # Check if En passant is possible
        # Only on 2 square pawn advances
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = (
                (move.startRow + move.endRow) // 2,
                move.endCol
            )
            # print(self.enpassantPossible)
        else:
            self.enpassantPossible = ()
        # print(move)

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

            # Undo Enpassant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = "bp" if self.whiteToMove else "wp"
                self.enpassantPossible = (move.endRow, move.endCol)

            # Undo 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            print(move)

    def getValidMovesNaive(self):
        """
        All moves considering checks.
        """
        # NOTE: will not work for enpassant

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

    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            # If only one check, block check or move king
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                # To block a check, move a piece into one of squares between enemy and king
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                # Enemy Piece causing the check
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []  # Squares the piece can move to
                # if Knight, must capture the knight or move king, other pieces can be blocked
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (
                            kingRow + check[2] * i,
                            kingCol + check[3] * i
                        )
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare == checkCol:
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved != "K":
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            # King not in check
            moves = self.getAllPossibleMoves()

        self.enpassantPossible = tempEnpassantPossible
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
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            if (self.board[row - 1][col] == "--"):
                # pawn can move forward 1 square
                if not piecePinned or pinDirection == (-1, 0):
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
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(
                            Move(
                                (row, col),
                                (row - 1, col - 1),
                                self.board
                            )
                        )
                elif (row - 1, col - 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(
                            Move(
                                (row, col),
                                (row - 1, col - 1),
                                self.board,
                                True
                            )
                        )
            if col + 1 <= 7:
                # Capture to right
                if self.board[row - 1][col + 1][0] == 'b':
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(
                            Move(
                                (row, col),
                                (row - 1, col + 1),
                                self.board
                            )
                        )
                elif (row - 1, col + 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(
                            Move(
                                (row, col),
                                (row - 1, col + 1),
                                self.board,
                                True
                            )
                        )
        else:
            if self.board[row + 1][col] == "--":
                if not piecePinned or pinDirection == (1, 0):
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
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(
                            Move(
                                (row, col),
                                (row + 1, col - 1),
                                self.board
                            )
                        )
                elif (row + 1, col - 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(
                            Move(
                                (row, col),
                                (row + 1, col - 1),
                                self.board,
                                True
                            )
                        )
            if col + 1 <= 7:
                if self.board[row + 1][col + 1][0] == 'w':
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(
                            Move(
                                (row, col),
                                (row + 1, col + 1),
                                self.board
                            )
                        )
                elif (row + 1, col + 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(
                            Move(
                                (row, col),
                                (row + 1, col + 1),
                                self.board,
                                True
                            )
                        )

    def getRookMoves(self, row, col, moves):
        """
        Get all rook moves for pawn locate at row, col and add them to moves
        """
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][i] != "Q":
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection(-d[0], -d[1]):
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
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = row + m[0]
            endCol = col + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
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
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
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
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = row + rowMoves[i]
            endCol = col + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(
                            Move(
                                (row, col),
                                (endRow, endCol),
                                self.board
                            )
                        )
                    if allyColor == 'w':
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        # Check outward from king for pins and checks
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        # 1st allied piece could be pinned
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        # 2nd allied pin, so no pin or check possible in this direction
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # Five Possibilites
                        # 1. Orthogonal Away from King and Piece is Rook
                        # 2. Diagonal Away from King and Piece is Bishop
                        # 3. 1 Square Diagonally from pawn
                        # 4. Any Direction from Queen
                        # 5. Any Direction is 1 Sqaure away from enemy King
                        if (0 <= j <= 3 and type == "R") or \
                            (4 <= j <= 7 and type == "B") or \
                            (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) or \
                                (type == "Q") or (i == 1 and type == "K"):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                # Piece blocking pin
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks


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

    def __init__(self, startSq, endSq, board, isEnpassantMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # Pawn Promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or \
            (self.pieceMoved == 'bp' and self.endRow == 7)

        # Enpassant
        self.isEnpassantMove = isEnpassantMove
        # if self.isEnpassantMove:
        #     print(self)
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"

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

    def __str__(self):
        return "Start Square: (" + str(self.startRow) + ", " + str(self.startCol) + \
            ") \nEnd Square: (" + str(self.endRow) + ", " + str(self.endCol) + \
            ")\nPiece Moved: " + self.pieceMoved + \
            "\nPiece Captured: " + self.pieceCaptured + \
            "\nisPawnPromotion: " + str(self.isPawnPromotion) + \
            "\nisEnpassantMove: " + str(self.isEnpassantMove)
