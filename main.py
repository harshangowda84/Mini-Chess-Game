import pygame
import os
import sys
import random
import time
from pygame import mixer
from typing import List, Tuple, Optional
from enum import Enum, auto

# Initialize Pygame and Mixer
pygame.init()
mixer.init()

class GameState(Enum):
    MENU = auto()
    PLAYER_SELECT = auto()
    GAME = auto()
    PAUSED = auto()
    ENDED = auto()

# Screen Setup
display_info = pygame.display.Info()
SCREEN_WIDTH: int = min(1366, display_info.current_w)
SCREEN_HEIGHT: int = min(768, display_info.current_h)

# UI Scaling based on screen resolution
BASE_SCALE = min(SCREEN_WIDTH / 1366, SCREEN_HEIGHT / 768)
SCALE_FACTOR: float = BASE_SCALE

# Game Constants
FPS = 60  # Frames per second
WINDOW_WIDTH = 1366
WINDOW_HEIGHT = 768
BUTTON_WIDTH = int(120 * SCALE_FACTOR)
BUTTON_HEIGHT = int(40 * SCALE_FACTOR)
BUTTON_GAP = int(20 * SCALE_FACTOR)
BUTTON_RADIUS = int(15 * SCALE_FACTOR)

# UI Constants
UI_LEFT_SPACE: int = int(SCREEN_WIDTH * 0.1)  # Increased side margins
UI_TOP_SPACE: int = int(SCREEN_HEIGHT * 0.1)  # Increased top margin
UI_BOTTOM_SPACE: int = int(SCREEN_HEIGHT * 0.1)  # Increased bottom margin

def updateBoardSize(size: str):
    global DIMENSION_X, DIMENSION_Y, SQ_SIZE, BOARD_LEFT, BOARD_TOP
    
    if size == "4x4":
        DIMENSION_X = DIMENSION_Y = 4
    elif size == "6x6":
        DIMENSION_X = DIMENSION_Y = 6
    elif size == "8x8":
        DIMENSION_X = DIMENSION_Y = 8
    
    # Calculate maximum possible square size that will fit the screen
    available_height = SCREEN_HEIGHT - (UI_TOP_SPACE + UI_BOTTOM_SPACE)
    available_width = SCREEN_WIDTH - (2 * UI_LEFT_SPACE)
    
    # For 8x8, make squares slightly smaller to ensure proper fit
    if size == "8x8":
        available_height *= 0.95  # 95% of available height
        available_width *= 0.95   # 95% of available width
    
    # Use the smaller dimension to ensure board fits
    SQ_SIZE = min(
        available_width // DIMENSION_X,
        available_height // DIMENSION_Y
    )
    
    # Center the board both horizontally and vertically
    BOARD_LEFT = (SCREEN_WIDTH - (DIMENSION_X * SQ_SIZE)) // 2
    BOARD_TOP = (SCREEN_HEIGHT - (DIMENSION_Y * SQ_SIZE)) // 2
    
    # For 8x8, adjust vertical position slightly higher
    if size == "8x8":
        BOARD_TOP = int(BOARD_TOP * 0.9)  # Move up by 10%

# Colors
WHITE = pygame.Color('white')
BLACK = pygame.Color('black')
GREY = pygame.Color('grey')
BLUE = pygame.Color('#4a90e2')
GREEN = pygame.Color('#50C878')
RED = pygame.Color('#FF6B6B')
BACKGROUND = pygame.Color('#F0F0F0')
BOARD_LIGHT = pygame.Color('#F0D9B5')
BOARD_DARK = pygame.Color('#B58863')

def show_checkmate_message(winner):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    WINDOW.blit(overlay, (0, 0))
    
    message = f"{winner} Wins by Checkmate!"
    text = TITLE_FONT.render(message, True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    WINDOW.blit(text, text_rect)
    
    continue_text = FONT.render("Click anywhere to continue", True, WHITE)
    continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
    WINDOW.blit(continue_text, continue_rect)
    pygame.display.update()
    
    try:
        checkmate_sound = load_sound('checkmate_sound.wav')
        checkmate_sound.play()
    except:
        print("Warning: Could not load checkmate sound")
    
    # Wait for click
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

def load_sound(filename: str) -> mixer.Sound:
    """Load a sound file from the audios directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sound_path = os.path.join(script_dir, 'audios', filename)
    return mixer.Sound(sound_path)

def transition_to_menu():
    global current_state, CURRENT_TURN, selected_piece, valid_moves
    current_state = GameState.MENU
    CURRENT_TURN = 'w'
    selected_piece = None
    valid_moves = []
    # Play transition sound
    try:
        sound = load_sound('Chess Sound Effects.wav')
        sound.play()
    except:
        print("Warning: Could not load transition sound")
        pass  # If sound file doesn't exist, skip it

# Game State Variables
current_state = GameState.MENU
BOARD_SIZES = ["4x4", "6x6", "8x8"]
selected_size = None
white_player = "HUMAN"  # or "AI"
black_player = "HUMAN"  # or "AI"

# Initialize Window
WINDOW = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mini Chess")
clock = pygame.time.Clock()

# Font
pygame.font.init()
FONT = pygame.font.Font(None, 36)
TITLE_FONT = pygame.font.Font(None, 72)

class Button:
    def __init__(self, x, y, width, height, text, color=BLUE, hover_color=GREEN):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=15)
        text_surface = FONT.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered:
            return True
        return False

# Board dimensions (default to 6x6)
DIMENSION_X: int = 6
DIMENSION_Y: int = 6
BOARD_SIZE_OPTIONS = ["4x4", "6x6", "8x8"]
SELECTED_BOARD_SIZE: str = "6x6"

# Calculate initial square size
updateBoardSize(SELECTED_BOARD_SIZE)

# Chess Board
class Piece:
    def __init__(self, color: str, type: str, position: Tuple[int, int]):
        self.color = color  # 'w' or 'b'
        self.type = type    # 'P', 'N', 'B', 'Q', 'K'
        self.position = position

    def get_valid_moves(self, board: 'Board') -> List[Tuple[int, int]]:
        moves = []
        row, col = self.position

        if self.type == 'P':
            direction = -1 if self.color == 'w' else 1
            # Move forward
            new_row = row + direction
            if 0 <= new_row < DIMENSION_Y and not board.get_piece_at((new_row, col)):
                moves.append((new_row, col))
            # Capture diagonally
            for dc in [-1, 1]:
                new_col = col + dc
                if 0 <= new_row < DIMENSION_Y and 0 <= new_col < DIMENSION_X:
                    target = board.get_piece_at((new_row, new_col))
                    if target and target.color != self.color:
                        moves.append((new_row, new_col))
        elif self.type == 'N':
            knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
            for dr, dc in knight_moves:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < DIMENSION_Y and 0 <= new_col < DIMENSION_X:
                    target = board.get_piece_at((new_row, new_col))
                    if not target or target.color != self.color:
                        moves.append((new_row, new_col))
        elif self.type == 'B':
            # Diagonals
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                r, c = row, col
                while True:
                    r += dr
                    c += dc
                    if 0 <= r < DIMENSION_Y and 0 <= c < DIMENSION_X:
                        target = board.get_piece_at((r, c))
                        if not target:
                            moves.append((r, c))
                        elif target.color != self.color:
                            moves.append((r, c))
                            break
                        else:
                            break
                    else:
                        break
        elif self.type == 'Q':
            # Horizontal, Vertical, and Diagonal
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                r, c = row, col
                while True:
                    r += dr
                    c += dc
                    if 0 <= r < DIMENSION_Y and 0 <= c < DIMENSION_X:
                        target = board.get_piece_at((r, c))
                        if not target:
                            moves.append((r, c))
                        elif target.color != self.color:
                            moves.append((r, c))
                            break
                        else:
                            break
                    else:
                        break
        elif self.type == 'K':
            # One square in any direction
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < DIMENSION_Y and 0 <= new_col < DIMENSION_X:
                    target = board.get_piece_at((new_row, new_col))
                    if not target or target.color != self.color:
                        moves.append((new_row, new_col))
        return moves

class Board:
    def __init__(self):
        self.pieces: List[Piece] = []
        self.setup_board()

    def setup_board(self):
        self.pieces.clear()
        # Adjust setup based on board size
        if SELECTED_BOARD_SIZE == "4x4":
            # New 4x4 setup with Bishops instead of Pawns
            self.pieces.append(Piece('b', 'B', (0, 0)))
            self.pieces.append(Piece('b', 'Q', (0, 1)))
            self.pieces.append(Piece('b', 'K', (0, 2)))
            self.pieces.append(Piece('b', 'B', (0, 3)))
            self.pieces.append(Piece('w', 'B', (3, 0)))
            self.pieces.append(Piece('w', 'Q', (3, 1)))
            self.pieces.append(Piece('w', 'K', (3, 2)))
            self.pieces.append(Piece('w', 'B', (3, 3)))
        elif SELECTED_BOARD_SIZE == "6x6":
            # Setup as per logs
            self.pieces.append(Piece('b', 'N', (0, 0)))
            self.pieces.append(Piece('b', 'B', (0, 1)))
            self.pieces.append(Piece('b', 'Q', (0, 2)))
            self.pieces.append(Piece('b', 'K', (0, 3)))
            self.pieces.append(Piece('b', 'B', (0, 4)))
            self.pieces.append(Piece('b', 'N', (0, 5)))
            for i in range(6):
                self.pieces.append(Piece('b', 'P', (1, i)))
            for i in range(6):
                self.pieces.append(Piece('w', 'P', (4, i)))
            self.pieces.append(Piece('w', 'N', (5, 0)))
            self.pieces.append(Piece('w', 'B', (5, 1)))
            self.pieces.append(Piece('w', 'Q', (5, 2)))
            self.pieces.append(Piece('w', 'K', (5, 3)))
            self.pieces.append(Piece('w', 'B', (5, 4)))
            self.pieces.append(Piece('w', 'N', (5, 5)))
        elif SELECTED_BOARD_SIZE == "8x8":
            # Standard chess setup
            self.pieces.append(Piece('b', 'R', (0, 0)))
            self.pieces.append(Piece('b', 'N', (0, 1)))
            self.pieces.append(Piece('b', 'B', (0, 2)))
            self.pieces.append(Piece('b', 'Q', (0, 3)))
            self.pieces.append(Piece('b', 'K', (0, 4)))
            self.pieces.append(Piece('b', 'B', (0, 5)))
            self.pieces.append(Piece('b', 'N', (0, 6)))
            self.pieces.append(Piece('b', 'R', (0, 7)))
            for i in range(8):
                self.pieces.append(Piece('b', 'P', (1, i)))
            for i in range(8):
                self.pieces.append(Piece('w', 'P', (6, i)))
            self.pieces.append(Piece('w', 'R', (7, 0)))
            self.pieces.append(Piece('w', 'N', (7, 1)))
            self.pieces.append(Piece('w', 'B', (7, 2)))
            self.pieces.append(Piece('w', 'Q', (7, 3)))
            self.pieces.append(Piece('w', 'K', (7, 4)))
            self.pieces.append(Piece('w', 'B', (7, 5)))
            self.pieces.append(Piece('w', 'N', (7, 6)))
            self.pieces.append(Piece('w', 'R', (7, 7)))

    def get_piece_at(self, position: Tuple[int, int]) -> Optional[Piece]:
        for piece in self.pieces:
            if piece.position == position:
                return piece
        return None

    def move_piece(self, piece: Piece, new_pos: Tuple[int, int]):
        target = self.get_piece_at(new_pos)
        if target:
            self.pieces.remove(target)  # Capture
        piece.position = new_pos

    def is_check(self, color: str) -> bool:
        king_pos = None
        for piece in self.pieces:
            if piece.color == color and piece.type == 'K':
                king_pos = piece.position
                break
        if not king_pos:
            return False

        opponent_color = 'b' if color == 'w' else 'w'
        for piece in self.pieces:
            if piece.color == opponent_color:
                valid_moves = piece.get_valid_moves(self)
                if king_pos in valid_moves:
                    return True
        return False

    def is_checkmate(self, color: str) -> bool:
        if not self.is_check(color):
            return False
        # Check if ANY piece can make a move to get out of check
        for piece in self.pieces:
            if piece.color == color:
                valid_moves = piece.get_valid_moves(self)
                for move in valid_moves:
                    # Simulate move
                    original_pos = piece.position
                    target = self.get_piece_at(move)
                    piece.position = move
                    if target:
                        self.pieces.remove(target)
                    in_check = self.is_check(color)
                    # Undo move
                    piece.position = original_pos
                    if target:
                        self.pieces.append(target)
                    if not in_check:
                        return False
        return True

    def get_valid_moves_considering_check(self, piece: Piece) -> List[Tuple[int, int]]:
        """Get valid moves that don't leave the king in check"""
        moves = piece.get_valid_moves(self)
        valid_moves = []
        
        # Test each move
        for move in moves:
            # Simulate move
            original_pos = piece.position
            target = self.get_piece_at(move)
            piece.position = move
            if target:
                self.pieces.remove(target)
                
            # If move doesn't leave king in check, it's valid
            if not self.is_check(piece.color):
                valid_moves.append(move)
                
            # Undo move
            piece.position = original_pos
            if target:
                self.pieces.append(target)
                
        return valid_moves

    def is_draw(self) -> bool:
        """Check if the game is a draw (only kings left or stalemate)"""
        # Check if only kings remain
        if len(self.pieces) == 2:
            kings = [p for p in self.pieces if p.type == 'K']
            if len(kings) == 2:
                return True
                
        # Check for stalemate (no legal moves but not in check)
        current_color = 'w' if CURRENT_TURN == 'w' else 'b'
        if not self.is_check(current_color):
            has_legal_moves = False
            for piece in self.pieces:
                if piece.color == current_color:
                    valid_moves = self.get_valid_moves_considering_check(piece)
                    if valid_moves:
                        has_legal_moves = True
                        break
            if not has_legal_moves:
                return True
        
        return False

def show_draw_message():
    """Display draw message when game ends in a draw"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    WINDOW.blit(overlay, (0, 0))
    
    message = "Game Drawn!"
    text = TITLE_FONT.render(message, True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    WINDOW.blit(text, text_rect)
    
    reason = "Only Kings Remain" if len(board.pieces) == 2 else "Stalemate"
    reason_text = FONT.render(f"Reason: {reason}", True, WHITE)
    reason_rect = reason_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
    WINDOW.blit(reason_text, reason_rect)
    
    continue_text = FONT.render("Click anywhere to continue", True, WHITE)
    continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
    WINDOW.blit(continue_text, continue_rect)
    pygame.display.update()
    
    # Wait for click
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

# Board and Game Variables
board: Board = Board()
selected_piece: Optional[Piece] = None
valid_moves: List[Tuple[int, int]] = []

def load_piece_image(piece: Piece) -> pygame.Surface:
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    piece_dir = os.path.join(script_dir, 'images')
    piece_name = f"{piece.color}_{piece.type}.png"
    piece_path = os.path.join(piece_dir, piece_name)
    
    if not os.path.exists(piece_path):
        print(f"Error: Piece image not found: {piece_path}")
        raise FileNotFoundError(f"Piece image not found: {piece_path}")
    
    image = pygame.image.load(piece_path)
    return pygame.transform.scale(image, (int(SQ_SIZE * 0.8), int(SQ_SIZE * 0.8)))

def draw_board(WINDOW: pygame.Surface):
    colors = [BOARD_LIGHT, BOARD_DARK]
    for row in range(DIMENSION_Y):
        for col in range(DIMENSION_X):
            color = colors[(row + col) % 2]
            x = BOARD_LEFT + col * SQ_SIZE
            y = BOARD_TOP + row * SQ_SIZE
            pygame.draw.rect(WINDOW, color, (x, y, SQ_SIZE, SQ_SIZE))
            
            # Highlight valid moves
            if (row, col) in valid_moves:
                s = 5  # Border thickness
                pygame.draw.rect(WINDOW, RED, (x+s, y+s, SQ_SIZE-2*s, SQ_SIZE-2*s), 3)
            
            # Highlight king in check or checkmate
            piece = board.get_piece_at((row, col))
            if piece and piece.type == 'K':
                if board.is_check(piece.color):
                    # Draw red background for check
                    check_surface = pygame.Surface((SQ_SIZE, SQ_SIZE))
                    check_surface.set_alpha(128)  # Semi-transparent
                    check_surface.fill(RED)
                    WINDOW.blit(check_surface, (x, y))
                    # Draw "CHECK!" text above the board
                    check_text = FONT.render("CHECK!", True, RED)
                    text_rect = check_text.get_rect(center=(SCREEN_WIDTH//2, BOARD_TOP - 30))
                    WINDOW.blit(check_text, text_rect)
                elif board.is_checkmate(piece.color):
                    # Solid red for checkmate
                    pygame.draw.rect(WINDOW, RED, (x, y, SQ_SIZE, SQ_SIZE), 0)

def draw_pieces(WINDOW: pygame.Surface):
    for piece in board.pieces:
        row, col = piece.position
        piece_image = load_piece_image(piece)
        x = BOARD_LEFT + col * SQ_SIZE + (SQ_SIZE - piece_image.get_width()) // 2
        y = BOARD_TOP + row * SQ_SIZE + (SQ_SIZE - piece_image.get_height()) // 2
        WINDOW.blit(piece_image, (x, y))

def draw_menu():
    # Draw title
    title = TITLE_FONT.render("Mini Chess Game", True, BLACK)
    title_rect = title.get_rect(center=(SCREEN_WIDTH//2, UI_TOP_SPACE * 3))
    WINDOW.blit(title, title_rect)
    
    # Create board size buttons
    buttons = []
    button_y = SCREEN_HEIGHT // 2 - BUTTON_HEIGHT
    for size in BOARD_SIZES:
        button_x = SCREEN_WIDTH//2 - BUTTON_WIDTH//2
        button = Button(button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, size)
        button.draw(WINDOW)
        buttons.append(button)
        button_y += BUTTON_HEIGHT + 20
    return buttons

def draw_player_select():
    # Draw title
    title = TITLE_FONT.render(f"Select Players - {selected_size} Board", True, BLACK)
    title_rect = title.get_rect(center=(SCREEN_WIDTH//2, UI_TOP_SPACE * 3))
    WINDOW.blit(title, title_rect)
    
    buttons = []
    
    # White player selection
    white_text = FONT.render("White Player:", True, BLACK)
    WINDOW.blit(white_text, (SCREEN_WIDTH//4, SCREEN_HEIGHT//2 - BUTTON_HEIGHT))
    
    white_human = Button(SCREEN_WIDTH//4, SCREEN_HEIGHT//2, 
                        BUTTON_WIDTH, BUTTON_HEIGHT, "Human",
                        GREEN if white_player == "HUMAN" else GREY)
    white_ai = Button(SCREEN_WIDTH//4 + BUTTON_WIDTH + 20, SCREEN_HEIGHT//2,
                     BUTTON_WIDTH, BUTTON_HEIGHT, "AI",
                     GREEN if white_player == "AI" else GREY)
    
    # Black player selection
    black_text = FONT.render("Black Player:", True, BLACK)
    WINDOW.blit(black_text, (3*SCREEN_WIDTH//4 - BUTTON_WIDTH, SCREEN_HEIGHT//2 - BUTTON_HEIGHT))
    
    black_human = Button(3*SCREEN_WIDTH//4 - BUTTON_WIDTH, SCREEN_HEIGHT//2,
                        BUTTON_WIDTH, BUTTON_HEIGHT, "Human",
                        GREEN if black_player == "HUMAN" else GREY)
    black_ai = Button(3*SCREEN_WIDTH//4, SCREEN_HEIGHT//2,
                     BUTTON_WIDTH, BUTTON_HEIGHT, "AI",
                     GREEN if black_player == "AI" else GREY)
    
    # Start button
    start_button = Button(SCREEN_WIDTH//2 - BUTTON_WIDTH//2, 
                         3*SCREEN_HEIGHT//4,
                         BUTTON_WIDTH, BUTTON_HEIGHT, "Start Game", BLUE)
    
    buttons = [
        ("WHITE_HUMAN", white_human),
        ("WHITE_AI", white_ai),
        ("BLACK_HUMAN", black_human),
        ("BLACK_AI", black_ai),
        ("START", start_button)
    ]
    
    for _, button in buttons:
        button.draw(WINDOW)
    
    return buttons

def draw_game():
    global selected_piece, valid_moves, current_state, CURRENT_TURN
    
    # Draw game state
    draw_board(WINDOW)
    draw_pieces(WINDOW)
    
    # Draw current turn indicator
    turn_text = f"{'White' if CURRENT_TURN == 'w' else 'Black'}'s Turn"
    turn_surf = FONT.render(turn_text, True, BLACK)
    turn_rect = turn_surf.get_rect(midtop=(SCREEN_WIDTH//2, 10))
    WINDOW.blit(turn_surf, turn_rect)
    
    # Draw menu button
    menu_button = Button(10, 10, BUTTON_WIDTH, BUTTON_HEIGHT, "Menu", RED)
    menu_button.draw(WINDOW)
    
    return [("MENU", menu_button)]

def animate_human_move(surface, start_pos, end_pos, piece, board):
    """Animate the movement of a piece"""
    # Calculate pixel coordinates
    piece_image = load_piece_image(piece)
    start_x = BOARD_LEFT + start_pos[1] * SQ_SIZE + (SQ_SIZE - piece_image.get_width()) // 2
    start_y = BOARD_TOP + start_pos[0] * SQ_SIZE + (SQ_SIZE - piece_image.get_height()) // 2
    end_x = BOARD_LEFT + end_pos[1] * SQ_SIZE + (SQ_SIZE - piece_image.get_width()) // 2
    end_y = BOARD_TOP + end_pos[0] * SQ_SIZE + (SQ_SIZE - piece_image.get_height()) // 2

    steps = 20  # Number of animation frames
    
    # Animate the movement
    for i in range(steps + 1):
        # Calculate current position
        alpha = i / steps
        current_x = start_x + (end_x - start_x) * alpha
        current_y = start_y + (end_y - start_y) * alpha
        
        # Redraw everything
        draw_board(surface)
        draw_pieces(surface)
        surface.blit(piece_image, (current_x, current_y))
        pygame.display.update()
        pygame.time.delay(20)  # Add a small delay for smooth animation

def main():
    global current_state, board, selected_piece, valid_moves, selected_size
    global white_player, black_player, DIMENSION_X, DIMENSION_Y, SELECTED_BOARD_SIZE, CURRENT_TURN
    
    running = True
    buttons = []
    CURRENT_TURN = 'w'  # White starts
    gameOver = False  # Initialize gameOver variable

    while running:
        WINDOW.fill(BACKGROUND)
        clock.tick(FPS)
        
        # Draw current state
        if current_state == GameState.MENU:
            buttons = draw_menu()
        elif current_state == GameState.PLAYER_SELECT:
            buttons = draw_player_select()
        elif current_state == GameState.GAME:
            buttons = draw_game()
            
            # Handle AI moves
            if ((CURRENT_TURN == 'w' and white_player == "AI") or 
                (CURRENT_TURN == 'b' and black_player == "AI")):
                if not gameOver and current_state == GameState.GAME:
                    from ai import findBestMove
                    valid_moves = []
                    
                    all_moves = []
                    for piece in board.pieces:
                        if piece.color == CURRENT_TURN:
                            moves = board.get_valid_moves_considering_check(piece)
                            all_moves.extend([(piece, move) for move in moves])
                    
                    if all_moves:
                        piece, move = findBestMove(board, all_moves, SELECTED_BOARD_SIZE)
                        if piece and move:
                            start_pos = piece.position
                            board.move_piece(piece, move)
                            # Animate AI move
                            animate_human_move(WINDOW, start_pos, move, piece, board)
                            try:
                                move_sound = load_sound('move_pieces.wav')
                                move_sound.play()
                            except:
                                print("Warning: Could not load move sound")
                            CURRENT_TURN = 'b' if CURRENT_TURN == 'w' else 'w'
                            
                            # Check game ending conditions
                            if board.is_draw():
                                print("Game Drawn!")
                                show_draw_message()
                                transition_to_menu()
                            elif board.is_check(CURRENT_TURN):
                                try:
                                    check_sound = load_sound('move_pieces.wav')
                                    check_sound.play()
                                except:
                                    print("Warning: Could not load check sound")
                                if board.is_checkmate(CURRENT_TURN):
                                    winner = 'White' if CURRENT_TURN == 'b' else 'Black'
                                    show_checkmate_message(winner)
                                    transition_to_menu()

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                # Handle button clicks
                if current_state == GameState.MENU:
                    for i, button in enumerate(buttons):
                        if button.rect.collidepoint(mouse_pos):
                            selected_size = BOARD_SIZES[i]
                            SELECTED_BOARD_SIZE = selected_size
                            updateBoardSize(selected_size)
                            board = Board()  # Reset board with new size
                            current_state = GameState.PLAYER_SELECT
                
                elif current_state == GameState.PLAYER_SELECT:
                    for button_id, button in buttons:
                        if button.rect.collidepoint(mouse_pos):
                            if button_id == "WHITE_HUMAN":
                                white_player = "HUMAN"
                            elif button_id == "WHITE_AI":
                                white_player = "AI"
                            elif button_id == "BLACK_HUMAN":
                                black_player = "HUMAN"
                            elif button_id == "BLACK_AI":
                                black_player = "AI"
                            elif button_id == "START":
                                current_state = GameState.GAME
                                CURRENT_TURN = 'w'  # Reset turn to white
                                board = Board()  # Reset board
                                selected_piece = None
                                valid_moves = []
                
                elif current_state == GameState.GAME:
                    # Handle menu button
                    for button_id, button in buttons:
                        if button_id == "MENU" and button.rect.collidepoint(mouse_pos):
                            current_state = GameState.MENU
                            continue
                    
                    # Handle board clicks (only for human players)
                    if ((CURRENT_TURN == 'w' and white_player == "HUMAN") or 
                        (CURRENT_TURN == 'b' and black_player == "HUMAN")):
                        if BOARD_LEFT <= mouse_pos[0] <= BOARD_LEFT + DIMENSION_X * SQ_SIZE and \
                           BOARD_TOP <= mouse_pos[1] <= BOARD_TOP + DIMENSION_Y * SQ_SIZE:
                            col = (mouse_pos[0] - BOARD_LEFT) // SQ_SIZE
                            row = (mouse_pos[1] - BOARD_TOP) // SQ_SIZE
                            
                            clicked_piece = board.get_piece_at((row, col))
                            
                            if selected_piece:
                                valid_moves = board.get_valid_moves_considering_check(selected_piece)
                                if (row, col) in valid_moves:
                                    # Make the move
                                    board.move_piece(selected_piece, (row, col))
                                    # Animate the move
                                    start_pos = selected_piece.position
                                    animate_human_move(WINDOW, start_pos, (row, col), selected_piece, board)
                                    try:
                                        move_sound = load_sound('move_pieces.wav')
                                        move_sound.play()
                                    except:
                                        print("Warning: Could not load move sound")
                                    CURRENT_TURN = 'b' if CURRENT_TURN == 'w' else 'w'
                                    
                                    # Check game ending conditions
                                    if board.is_draw():
                                        print("Game Drawn!")
                                        show_draw_message()
                                        transition_to_menu()
                                    elif board.is_check(CURRENT_TURN):
                                        try:
                                            check_sound = load_sound('move_pieces.wav')
                                            check_sound.play()
                                        except:
                                            print("Warning: Could not load check sound")
                                        if board.is_checkmate(CURRENT_TURN):
                                            winner = 'White' if CURRENT_TURN == 'b' else 'Black'
                                            try:
                                                checkmate_sound = load_sound('checkmate_sound.wav')
                                                checkmate_sound.play()
                                            except:
                                                print("Warning: Could not load checkmate sound")
                                            show_checkmate_message(winner)
                                            transition_to_menu()
                                
                                selected_piece = None
                                valid_moves = []
                            elif clicked_piece and clicked_piece.color == CURRENT_TURN:
                                selected_piece = clicked_piece
                                valid_moves = board.get_valid_moves_considering_check(clicked_piece)

        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()