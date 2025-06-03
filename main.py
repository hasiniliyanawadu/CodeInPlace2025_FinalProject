import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

CANVAS_WIDTH = 400
CANVAS_HEIGHT = CANVAS_WIDTH
N_ROWS = 4
N_COLS = N_ROWS
SIZE = CANVAS_WIDTH / N_ROWS

# List of specific positions to draw pieces
piece_positions = [(3, 0, 'red'), (3, 2, 'red'), (0, 1, 'black'), (0, 3, 'black')]
# Dictionary to keep track of pieces and their positions
pieces = {} 
# Keep track of highlighted squares
highlighted_squares = [] 
# Keep track of highlighted pieces 
highlighted_pieces = [] 

# Variable to keep track of the current player
current_player = 'red'

def main():
    global canvas, root
    root = tk.Tk()
    root.title("Checkers Game")

    canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    canvas.pack()
    
    # For each row and column, draw a square
    for r in range(N_ROWS):
        for c in range(N_COLS):
            draw_square(canvas, r, c)
    
    # Place pieces for both players
    place_pieces(canvas)

    # Highlight the pieces of the current player
    highlight_player_pieces(canvas, current_player)

    # Load the crown image 
    load_crown_image()

    # Set up mouse click event
    canvas.bind('<Button-1>', handle_click)

    root.mainloop()  # Keeps the window open

def draw_square(canvas, r, c):
    """
    Draws a square at row r, column c.
    """
    color = get_color(r, c)  # Get the square's color based on the row and column
    x = c * SIZE  # Calculate left_x
    y = r * SIZE  # Calculate top_y
    end_x = x + SIZE  # Calculate right_x
    end_y = y + SIZE  # Calculate bottom_y
    
    canvas.create_rectangle(x, y, end_x, end_y, fill=color, outline='black')  # Draw the rectangle

def get_color(r, c):
    """
    Gets the color of the checkerboard square at row r column c.
    """
    if is_even(r + c):
        return "#ee1c25"  # Red
    else:
        return "#231f20" # Black

def is_even(value):
    """
    Returns whether or not a number is even.
    """
    return value % 2 == 0

def place_pieces(canvas):
    """
    Places pieces on the board at specified positions.
    """
    for pos in piece_positions:
        draw_piece(canvas, pos[0], pos[1], pos[2])
        pieces[(pos[0], pos[1])] = {'color': pos[2], 'king': False}  # Keep track of piece positions and king status

def draw_piece(canvas, r, c, color, king=False): 
    """
    Draws a circle (piece) in the middle of the square at row r, column c.
    """
    x = c * SIZE + SIZE / 2  # Calculate the center x of the square
    y = r * SIZE + SIZE / 2  # Calculate the center y of the square
    radius = SIZE / 2.3
    
    canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color)
    if king:
        canvas.create_image(x, y, image=crown_photo)
    
def load_crown_image():
    """
    Loads the crown image and resizes it.
    """
    global crown_photo
    crown_image = Image.open("crown2.png") 
    crown_image = crown_image.resize((int(SIZE / 3), int(SIZE / 3)), resample=Image.LANCZOS)
    crown_photo = ImageTk.PhotoImage(crown_image)

def highlight_square(canvas, r, c, color="yellow"):
    """
    Highlights a square at row r, column c with a given color.
    """
    x = c * SIZE
    y = r * SIZE
    end_x = x + SIZE
    end_y = y + SIZE
    
    highlight = canvas.create_rectangle(x, y, end_x, end_y, outline=color, width=3)
    highlighted_squares.append(highlight)


def has_possible_moves(player):
    """
    Checks if the given player has any possible moves left.
    """
    for (r, c), info in pieces.items():
        if info['color'] == player:
            start = (r, c, info)
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            captures = [(2, 2), (2, -2), (-2, 2), (-2, -2)]
            
            for d in directions:
                move = (r + d[0], c + d[1])
                if validate_move(start, move):
                    return True
            
            for c in captures:
                move = (r + c[0], c[1]) 
                if validate_move(start, move):
                    return True
    
    return False


def handle_click(event):
    global selected_piece, current_player

    x, y = event.x, event.y
    row = int(y // SIZE)
    col = int(x // SIZE)

    if (row, col) in pieces:
        if pieces[(row, col)]['color'] == current_player:
            clear_highlights(canvas)
            selected_piece = (row, col, pieces[(row, col)])
            print(f"Selected piece at {selected_piece}")
            highlight_possible_moves(selected_piece)
            print("Checking for mandatory captures...")
            if has_mandatory_captures(current_player):
                print("Mandatory capture is required!")
                highlight_mandatory_captures(current_player)
    elif selected_piece:
        target_square = (row, col)
        if validate_move(selected_piece, target_square):
            move_piece(selected_piece, target_square)
            clear_highlights(canvas)
            selected_piece = None

            # Check for winner after each move
            winner = check_winner()
            if winner:
                display_winner(winner)
            else:
                # Switch turns after a valid move
                current_player = 'black' if current_player == 'red' else 'red'
                highlight_player_pieces(canvas, current_player)
                
def display_winner(winner):
    """
    Displays a window showing the winner of the game.
    """
    global winner_window

    winner_window = tk.Toplevel(root)
    winner_window.title("Game Over")

    if winner == 'tie':
        winner_label = tk.Label(winner_window, text="It's a tie!", font=('Helvetica', 24))
    else:
        winner_label = tk.Label(winner_window, text=f"{winner.capitalize()} player wins!", font=('Helvetica', 24))

    winner_label.pack(padx=20, pady=20)

    # Play Again button
    play_again_button = tk.Button(winner_window, text="Play Again", command=play_again)
    play_again_button.pack(pady=10)

    winner_window.transient(root)  # Set winner window to be transient to main window
    winner_window.grab_set()  # Make winner window modal
    root.wait_window(winner_window)  # Wait for winner window to be closed before continuing


def play_again():
    """
    Resets the game for a new round.
    """
    global winner_window, pieces, current_player, root

    winner_window.destroy()  # Close the winner window
    root.destroy()  # Close the main game window
    
    pieces.clear()  # Clear pieces dictionary
    current_player = 'red'  # Reset current player to red (or whichever starts first)
    
    main()  # Restart the game


def highlight_mandatory_captures(player):
    """
    Highlights the target squares for mandatory captures with red.
    """
    global selected_piece

    start_row, start_col, piece_info = selected_piece
    captures = [(2, 2), (2, -2), (-2, 2), (-2, -2)]

    for capture in captures:
        move = (start_row + capture[0], start_col + capture[1])
        if validate_move(selected_piece, move):
            highlight_square(canvas, move[0], move[1], color="white")


def clear_highlights(canvas):
    """
    Clears all highlighted squares and pieces.
    """
    for highlight in highlighted_squares:
        canvas.delete(highlight)
    highlighted_squares.clear()
    
    for highlight in highlighted_pieces:
        canvas.delete(highlight)
    highlighted_pieces.clear()

selected_piece = None


def has_mandatory_captures(player):
    """
    Checks if the given player has any mandatory capture moves left.
    """
    for (r, c), info in pieces.items():
        if info['color'] == player:
            start = (r, c, info)
            captures = [(2, 2), (2, -2), (-2, 2), (-2, -2)]
            
            for capture in captures:
                move = (r + capture[0], c + capture[1]) 
                if validate_move(start, move):
                    print(f"Mandatory capture found for {player} at {move}")
                    return True
    
    return False


def validate_move(start, end):
    """
    Validates the move based on checkers game rules.
    """
    start_row, start_col, start_info = start
    start_color = start_info['color']
    start_king = start_info['king']
    end_row, end_col = end
    
    # Ensure end position is within bounds and empty
    if end_row < 0 or end_row >= N_ROWS or end_col < 0 or end_col >= N_COLS or (end_row, end_col) in pieces:
        return False
    
    # Regular pieces can only move forward unless they are kings
    if not start_king:
        if start_color == 'red' and end_row >= start_row:
            return False
        if start_color == 'black' and end_row <= start_row:
            return False
    
    # Basic diagonal move validation
    if abs(start_row - end_row) == 1 and abs(start_col - end_col) == 1:
        return True
    
    # Capture move validation
    if abs(start_row - end_row) == 2 and abs(start_col - end_col) == 2:
        middle_row = (start_row + end_row) // 2
        middle_col = (start_col + end_col) // 2
        print(f"Middle piece at ({middle_row}, {middle_col})")  # Debug info
        if (middle_row, middle_col) in pieces and pieces[(middle_row, middle_col)]['color'] != start_color:
            return True
    
    return False

def highlight_possible_moves(piece):
    """
    Highlights all possible moves for the selected piece.
    """
    start_row, start_col, piece_info = piece
    piece_color = piece_info['color']
    piece_king = piece_info['king']
    
    directions = [
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]
    captures = [
        (2, 2), (2, -2), (-2, 2), (-2, -2)
    ]
    
    has_capture = False
    
    for c in captures:
        move = (start_row + c[0], start_col + c[1])
        if validate_move(piece, move):
            highlight_square(canvas, move[0], move[1])
            has_capture = True
    
    if not has_capture:
        for d in directions:
            move = (start_row + d[0], start_col + d[1])
            if validate_move(piece, move):
                highlight_square(canvas, move[0], move[1])

def highlight_player_pieces(canvas, player):
    """
    Highlights all pieces of the current player.
    """
    for (r, c), info in pieces.items():
        if info['color'] == player:
            highlight_piece(canvas, r, c)

def highlight_piece(canvas, r, c, color="green"):
    """
    Highlights a piece at row r, column c with a given color.
    """
    x = c * SIZE
    y = r * SIZE
    end_x = x + SIZE
    end_y = y + SIZE
    
    highlight = canvas.create_rectangle(x, y, end_x, end_y, outline=color, width=3)
    highlighted_pieces.append(highlight)

def move_piece(start, end):
    """
    Moves the piece from start to end if the move is valid.
    """
    global pieces
    
    start_row, start_col, piece_info = start
    piece_color = piece_info['color']
    piece_king = piece_info['king']
    end_row, end_col = end

    # Remove the piece from the start position
    del pieces[(start_row, start_col)]
    draw_square(canvas, start_row, start_col)  # Redraw the square to cover the old piece

    # If the move is a capture, remove the captured piece
    if abs(start_row - end_row) == 2 and abs(start_col - end_col) == 2:
        middle_row = (start_row + end_row) // 2
        middle_col = (start_col + end_col) // 2
        print(f"Capturing piece at ({middle_row}, {middle_col})")  # Debug info
        if (middle_row, middle_col) in pieces:
            del pieces[(middle_row, middle_col)]
            draw_square(canvas, middle_row, middle_col)

    # Place the piece in the new position
    pieces[(end_row, end_col)] = {'color': piece_color, 'king': piece_king}
    draw_piece(canvas, end_row, end_col, piece_color, piece_king)

    # Print the position where the piece is moved to
    print(f"Moved piece to ({end_row}, {end_col})")

    # Check if the piece should be kinged
    if (piece_color == 'red' and end_row == 0) or (piece_color == 'black' and end_row == N_ROWS - 1):
        pieces[(end_row, end_col)]['king'] = True
        draw_piece(canvas, end_row, end_col, piece_color, True)

def has_pieces(player):
    """
    Checks if the given player has any pieces left.
    """
    return any(info['color'] == player for info in pieces.values())

def check_winner():
    """
    Checks if there is a winner in the game.
    Returns 'red' if all black pieces are eliminated,
    'black' if all red pieces are eliminated, 'tie' if both players
    have the same number of pieces and no possible moves left,
    and None if no winner yet.
    """
    red_pieces = 0
    black_pieces = 0
    
    for info in pieces.values():
        if info['color'] == 'red':
            red_pieces += 1
        elif info['color'] == 'black':
            black_pieces += 1
    
    if black_pieces == 0:
        return 'red'
    elif red_pieces == 0:
        return 'black'
    elif red_pieces == black_pieces:
        if not has_possible_moves('red') and not has_possible_moves('black'):
            return 'tie'
    
    return None

        
if __name__ == '__main__':
    main()
