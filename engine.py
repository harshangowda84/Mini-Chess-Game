class Move():
    # Convert board coordinates to chess notation
    def __init__(self, startSq, endSq, board, dimension=6):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        self.dimension = dimension

        # Pawn promotion
        self.isPawnPromotion = False
        if (self.pieceMoved == 'w_P' and self.endRow == 0) or (self.pieceMoved == 'b_P' and self.endRow == dimension - 1):
            self.isPawnPromotion = True

        # Update ranks and files based on dimension
        self.ranksToRows = {str(i + 1): self.dimension - 1 - i for i in range(self.dimension)}
        self.rowsToRanks = {v: k for k, v in self.ranksToRows.items()}
        self.filesToCols = {chr(ord('a') + i): i for i in range(self.dimension)}
        self.colsToFiles = {v: k for k, v in self.filesToCols.items()}

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

class GameState():
    def __init__(self, dimension=6):
        self.dimension = dimension
        # Initialize empty board
        self.board = [['--' for _ in range(dimension)] for _ in range(dimension)]
        
        # Track single king per side
        self.whiteKingLocation = None
        self.blackKingLocation = None
        
        # Set up pieces based on board size
        if dimension == 4:  # 4x4 board: 2 bishops, 1 queen, 1 king per side
            # Black pieces
            self.board[0] = ['b_B', 'b_Q', 'b_K', 'b_B']
            self.board[1] = ['--', '--', '--', '--']
            self.board[2] = ['--', '--', '--', '--']
            self.board[3] = ['w_B', 'w_Q', 'w_K', 'w_B']
            # King locations
            self.whiteKingLocation = (3, 2)
            self.blackKingLocation = (0, 2)
            
        elif dimension == 6:  # 6x6 board: Current setup
            self.board[0] = ['b_N', 'b_B', 'b_Q', 'b_K', 'b_B', 'b_N']
            self.board[1] = ['b_P', 'b_P', 'b_P', 'b_P', 'b_P', 'b_P']
            self.board[2] = ['--', '--', '--', '--', '--', '--']
            self.board[3] = ['--', '--', '--', '--', '--', '--']
            self.board[4] = ['w_P', 'w_P', 'w_P', 'w_P', 'w_P', 'w_P']
            self.board[5] = ['w_N', 'w_B', 'w_Q', 'w_K', 'w_B', 'w_N']
            self.whiteKingLocation = (5, 3)
            self.blackKingLocation = (0, 3)
            
        elif dimension == 8:  # 8x8 board: Standard chess setup
            self.board[0] = ['b_R', 'b_N', 'b_B', 'b_Q', 'b_K', 'b_B', 'b_N', 'b_R']
            self.board[1] = ['b_P', 'b_P', 'b_P', 'b_P', 'b_P', 'b_P', 'b_P', 'b_P']
            for r in range(2, 6):
                self.board[r] = ['--' for _ in range(8)]
            self.board[6] = ['w_P', 'w_P', 'w_P', 'w_P', 'w_P', 'w_P', 'w_P', 'w_P']
            self.board[7] = ['w_R', 'w_N', 'w_B', 'w_Q', 'w_K', 'w_B', 'w_N', 'w_R']
            self.whiteKingLocation = (7, 4)
            self.blackKingLocation = (0, 4)
            
        # Debug: Print initial board setup and king locations
        self.printBoardState()
        
        # Move functions
        self.moveFunctions = {
            'P': self.getPawnMoves,
            'N': self.getKnightMoves,
            'B': self.getBishopMoves,
            'R': self.getRookMoves,
            'Q': self.getQueenMoves,
            'K': self.getKingMoves
        }
        
        self.whiteToMove = True
        self.moveLog = []
        self.checkMate = False
        self.staleMate = False
        
    def printBoardState(self):
        print(f"\nCurrent board state ({self.dimension}x{self.dimension}):")
        for row in self.board:
            print(row)
        print(f"White king: {self.whiteKingLocation}")
        print(f"Black king: {self.blackKingLocation}")
        print(f"{'White' if self.whiteToMove else 'Black'} to move\n")

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

        # Update king location
        if move.pieceMoved == 'b_K':
            self.blackKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'w_K':
            self.whiteKingLocation = (move.endRow, move.endCol)

        # Debug: Print king locations after move
        print(f"After move {move.getChessNotation()}:")
        print(f"White king: {self.whiteKingLocation}")
        print(f"Black king: {self.blackKingLocation}")
        print("Current board:")
        for row in self.board:
            print(row)

    def undoMove(self, num_moves=1):
        for _ in range(num_moves):
            if len(self.moveLog) != 0:
                move = self.moveLog.pop()
                self.board[move.startRow][move.startCol] = move.pieceMoved
                self.board[move.endRow][move.endCol] = move.pieceCaptured
                self.whiteToMove = not self.whiteToMove

                # Restore king location
                if move.pieceMoved == 'b_K':
                    self.blackKingLocation = (move.startRow, move.startCol)
                elif move.pieceMoved == 'w_K':
                    self.whiteKingLocation = (move.startRow, move.startCol)

                # Debug: Print king locations after undo
                print(f"After undoing move {move.getChessNotation()}:")
                print(f"White king: {self.whiteKingLocation}")
                print(f"Black king: {self.blackKingLocation}")
                print("Current board:")
                for row in self.board:
                    print(row)
            else:
                break

    def getValidMoves(self):
        moves = self.getAllPossibleMoves()
        print(f"Possible moves for {'White' if self.whiteToMove else 'Black'}: {[move.getChessNotation() for move in moves]}")
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                print(f"Removing move {moves[i].getChessNotation()} because it leaves king in check")
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        # Check for checkmate or stalemate
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
                print("Checkmate detected")
            else:
                self.staleMate = True
                print("Stalemate detected")
        print(f"Valid moves for {'White' if self.whiteToMove else 'Black'}: {[move.getChessNotation() for move in moves]}")
        return moves

    def inCheck(self):
        king_location = self.whiteKingLocation if self.whiteToMove else self.blackKingLocation
        print(f"Checking if {'White' if self.whiteToMove else 'Black'} is in check. King position: {king_location}")
        if self.squareUnderAttack(king_location):
            print(f"King at {king_location} is under attack")
            return True
        return False

    def squareUnderAttack(self, position):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == position[0] and move.endCol == position[1]:
                print(f"Square {position} is under attack by move {move.getChessNotation()}")
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        for r in range(self.dimension):
            for c in range(self.dimension):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][2]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if r > 0:
                if self.board[r-1][c] == "--":
                    moves.append(Move((r, c), (r-1, c), self.board, self.dimension))
                if c-1 >= 0 and self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board, self.dimension))
                if c+1 < self.dimension and self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board, self.dimension))
        else:
            if r < self.dimension - 1:
                if self.board[r+1][c] == "--":
                    moves.append(Move((r, c), (r+1, c), self.board, self.dimension))
                if c-1 >= 0 and self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c-1), self.board, self.dimension))
                if c+1 < self.dimension and self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board, self.dimension))

    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow, endCol = r + m[0], c + m[1]
            if 0 <= endRow < self.dimension and 0 <= endCol < self.dimension:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board, self.dimension))

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, self.dimension):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < self.dimension and 0 <= endCol < self.dimension:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board, self.dimension))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board, self.dimension))
                        break
                    else:
                        break
                else:
                    break

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, self.dimension):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < self.dimension and 0 <= endCol < self.dimension:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board, self.dimension))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board, self.dimension))
                        break
                    else:
                        break
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in kingMoves:
            endRow, endCol = r + m[0], c + m[1]
            if 0 <= endRow < self.dimension and 0 <= endCol < self.dimension:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board, self.dimension))