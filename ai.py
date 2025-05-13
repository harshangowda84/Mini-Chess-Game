import random
import time

# Constants
CHECKMATE = 1000000
STALEMATE = 0
DEPTH = 2
AI_MOVE_DELAY = 0.5  # Reduced delay for better responsiveness

def findBestMove(board, validMoves, board_size='6x6'):
    """Find the best move that doesn't leave own king in check and doesn't capture opponent's king"""
    
    # Add delay to match human pace
    time.sleep(AI_MOVE_DELAY)
    
    if not validMoves:
        return None, None
        
    # Filter moves that would capture a king
    filtered_moves = []
    last_moved_pieces = []  # Track last moved pieces to avoid repetition
    
    for piece, move in validMoves:
        target = board.get_piece_at(move)
        if not target or target.type != 'K':
            # Simulate move to check if it leaves own king in check
            original_pos = piece.position
            if target:
                board.pieces.remove(target)
            piece.position = move
            
            if not board.is_check(piece.color):
                filtered_moves.append((piece, move))
                
            # Undo move simulation
            piece.position = original_pos
            if target:
                board.pieces.append(target)
    
    if not filtered_moves:
        return None, None
        
    # Select best move from filtered legal moves with piece diversity
    best_moves = []
    best_score = -CHECKMATE
    
    # Penalize moves that use recently moved pieces
    piece_usage_penalty = 20  # Penalty for using same piece repeatedly
    
    for piece, move in filtered_moves:
        # Make move
        original_pos = piece.position
        target = board.get_piece_at(move)
        piece.position = move
        if target:
            board.pieces.remove(target)
            
        # Base position evaluation
        score = evaluateBoard(board, piece.color, board_size)
        score += evaluatePosition(piece, move, board_size, board)
        
        # Penalize if piece was recently used
        if piece in last_moved_pieces:
            score -= piece_usage_penalty
        
        # Extra points for checking opponent's king
        opponent_color = 'b' if piece.color == 'w' else 'w'
        if board.is_check(opponent_color):
            score += 50  # Bonus for check
            if board.is_checkmate(opponent_color):
                score = CHECKMATE  # Maximum score for checkmate
        
        # Bonus for moving different piece types
        if piece.type in ['P', 'N', 'B', 'Q']:  # Encourage non-king piece movement
            score += 10
            
        # Bonus for forward movement of pieces
        if piece.type != 'K':  # Don't encourage king movement early
            if piece.color == 'w' and move[0] < original_pos[0]:  # White moving forward
                score += 5
            elif piece.color == 'b' and move[0] > original_pos[0]:  # Black moving forward
                score += 5
        
        # Small random factor to prevent deterministic play
        score += random.uniform(-5, 5)
        
        # Undo move
        piece.position = original_pos
        if target:
            board.pieces.append(target)
            
        if score > best_score:
            best_score = score
            best_moves = [(piece, move)]
        elif score == best_score and random.random() < 0.4:  # 40% chance to add equal moves
            best_moves.append((piece, move))
    
    if not best_moves:
        return None, None
    
    # Select random move from best moves
    chosen_move = random.choice(best_moves)
    # Update last moved pieces (keep track of last 3 moves)
    last_moved_pieces.append(chosen_move[0])
    if len(last_moved_pieces) > 3:
        last_moved_pieces.pop(0)
        
    return chosen_move

def evaluatePosition(piece, move, board_size='6x6', board=None):
    score = 0
    dim = int(board_size[0])
    center = dim // 2
    row, col = move
    
    # Center control bonus
    if board_size == '4x4':
        if 1 <= row <= 2 and 1 <= col <= 2:
            score += 5
    else:
        if abs(row - center) <= 1 and abs(col - center) <= 1:
            score += 3
    
    # King attack proximity bonus (only if board is provided)
    if board:
        enemy_color = 'b' if piece.color == 'w' else 'w'
        enemy_king = None
        for p in board.pieces:
            if p.type == 'K' and p.color == enemy_color:
                enemy_king = p
                break
        
        if enemy_king:
            king_row, king_col = enemy_king.position
            distance_to_king = abs(row - king_row) + abs(col - king_col)
            if distance_to_king <= 2:  # Close to enemy king
                score += (3 - distance_to_king) * 10
    
    # Piece-specific positioning
    if piece.type == 'P':
        # Encourage forward movement
        if piece.color == 'w' and row < piece.position[0]:
            score += 3  # Moving forward
        elif piece.color == 'b' and row > piece.position[0]:
            score += 3  # Moving forward
            
        # Bonus for supported pawns (only if board is provided)
        if board:
            for p in board.pieces:
                if p.color == piece.color and p.type == 'P':
                    if abs(p.position[1] - col) == 1:  # Adjacent columns
                        score += 2
                    
    elif piece.type == 'N':
        # Knights are more valuable near center
        if abs(row - center) <= 1 and abs(col - center) <= 1:
            score += 4
            
    elif piece.type == 'B':
        # Bishops control more squares when near center
        if abs(row - center) <= 1 and abs(col - center) <= 1:
            score += 3
            
    elif piece.type == 'Q':
        # Queen should stay back early game
        if board and len(board.pieces) > dim * 2:  # Early game
            if (piece.color == 'w' and row >= dim-2) or (piece.color == 'b' and row <= 1):
                score += 2
                
    elif piece.type == 'K':
        # King safety - prefer edges except in endgame
        if board:
            piece_count = len(board.pieces)
            if piece_count > dim * 2:  # Not endgame
                if row in [0, dim-1] or col in [0, dim-1]:
                    score += 3
            else:  # Endgame - king should be more active
                if abs(row - center) <= 2 and abs(col - center) <= 2:
                    score += 2
    
    return score

def evaluateBoard(board, color, board_size='6x6'):
    score = 0
    dim = int(board_size[0])
    pieces = {
        '4x4': {'B': 30, 'Q': 90, 'K': 900},
        '6x6': {'P': 10, 'N': 30, 'B': 30, 'Q': 90, 'K': 900},
        '8x8': {'P': 10, 'N': 30, 'B': 30, 'R': 50, 'Q': 90, 'K': 900}
    }[board_size]
    
    # Material score
    for piece in board.pieces:
        value = pieces.get(piece.type, 0)
        multiplier = 1 if piece.color == color else -1
        score += value * multiplier
        
        # Position-based scores
        if piece.color == color:
            # Control of center
            row, col = piece.position
            center = dim // 2
            if abs(row - center) <= 1 and abs(col - center) <= 1:
                score += 5
                
            # Piece development
            if piece.type in ['N', 'B', 'Q']:
                if (color == 'w' and row < dim-1) or (color == 'b' and row > 0):
                    score += 3
                    
            # Pawn structure
            if piece.type == 'P':
                # Connected pawns
                for other in board.pieces:
                    if other.color == color and other.type == 'P':
                        if abs(other.position[1] - piece.position[1]) == 1:
                            score += 2
                            
            # Attack potential
            valid_moves = piece.get_valid_moves(board)
            score += len(valid_moves) * 0.5  # Small bonus for mobility
            
            # Check detection
            enemy_color = 'b' if color == 'w' else 'w'
            original_pos = piece.position
            for move in valid_moves:
                # Simulate move
                target = board.get_piece_at(move)
                piece.position = move
                if target:
                    board.pieces.remove(target)
                    
                if board.is_check(enemy_color):
                    score += 20  # Big bonus for moves that give check
                    if board.is_checkmate(enemy_color):
                        score = CHECKMATE  # Maximum score for checkmate
                        
                # Undo move simulation
                piece.position = original_pos
                if target:
                    board.pieces.append(target)
    
    return score