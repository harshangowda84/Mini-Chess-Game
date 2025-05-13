# Mini Chess Game

A Python-based Mini Chess game with AI opponent support and multiple board size options.

## Features

- Multiple board sizes (4x4, 6x6, 8x8)
- Human vs Human gameplay
- Human vs AI gameplay
- AI vs AI gameplay
- Sound effects for moves, captures, and checkmate
- Piece movement animations
- Check and Checkmate detection
- Stalemate detection
- Move validation
- Simple and intuitive UI

## Screenshots

Place some screenshots of your game here

## Installation

### Method 1: Using the Executable (Windows)
1. Download the latest release
2. Extract the zip file
3. Run `Mini Chess.exe`

### Method 2: Running from Source

1. Clone the repository:
```bash
git clone https://github.com/YourUsername/Mini-Chess-Game.git
cd Mini-Chess-Game
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Run the game:
```bash
python main.py
```

## How to Play

1. Start the game by selecting a board size (4x4, 6x6, or 8x8)
2. Choose player types for both White and Black:
   - Human: Manual control
   - AI: Computer-controlled
3. Click on a piece to select it
4. Click on a highlighted square to move the selected piece
5. Game ends when:
   - Checkmate occurs
   - Stalemate occurs
   - Only kings remain (draw)

## Controls

- Left mouse click: Select/move pieces
- Menu button: Return to main menu
- Restart button: Start a new game

## Game Rules

### 4x4 Board
- Simplified chess with only Kings, Queens, and Bishops
- No pawns or knights
- Focus on quick tactical play

### 6x6 Board
- Standard pieces except Rooks
- Modified pawn movement
- Balanced gameplay

### 8x8 Board
- Full classical chess rules
- All traditional pieces
- Complete chess experience

## Technical Details

- Built with Python 3.12
- Uses Pygame for graphics and sound
- Implements minimax algorithm with alpha-beta pruning for AI
- Object-oriented design for piece movement and board management

## Project Structure

```
Mini_Chess/
├── main.py           # Game entry point and UI
├── engine.py         # Chess logic and game rules
├── ai.py            # AI opponent implementation
├── images/          # Chess piece images
├── audios/          # Sound effects
└── icons/           # UI icons
```

## Dependencies

- Python 3.12+
- pygame 2.5.0

## Building the Executable

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller mini_chess.spec
```

The executable will be created in the `dist` folder.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Chess piece images from [source]
- Sound effects from [source]
- Icons from [source]


