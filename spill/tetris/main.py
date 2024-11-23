import pygame
import random

# Initialize Pygame modules
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Global Variables
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 700
PLAY_WIDTH = 300  # Meaning 300 // 30 = 10 blocks
PLAY_HEIGHT = 600  # Meaning 600 // 30 = 20 blocks
BLOCK_SIZE = 30

TOP_LEFT_X = (SCREEN_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = SCREEN_HEIGHT - PLAY_HEIGHT

# Tetris shapes and their rotations
S_SHAPE = [['.....',
            '.....',
            '..00.',
            '.00..',
            '.....'],
           ['.....',
            '..0..',
            '..00.',
            '...0.',
            '.....']]

Z_SHAPE = [['.....',
            '.....',
            '.00..',
            '..00.',
            '.....'],
           ['.....',
            '..0..',
            '.00..',
            '.0...',
            '.....']]

I_SHAPE = [['..0..',
            '..0..',
            '..0..',
            '..0..',
            '.....'],
           ['.....',
            '0000.',
            '.....',
            '.....',
            '.....']]

O_SHAPE = [['.....',
            '.....',
            '.00..',
            '.00..',
            '.....']]

J_SHAPE = [['.....',
            '.0...',
            '.000.',
            '.....',
            '.....'],
           ['.....',
            '..00.',
            '..0..',
            '..0..',
            '.....'],
           ['.....',
            '.....',
            '.000.',
            '...0.',
            '.....'],
           ['.....',
            '..0..',
            '..0..',
            '.00..',
            '.....']]

L_SHAPE = [['.....',
            '...0.',
            '.000.',
            '.....',
            '.....'],
           ['.....',
            '..0..',
            '..0..',
            '..00.',
            '.....'],
           ['.....',
            '.....',
            '.000.',
            '.0...',
            '.....'],
           ['.....',
            '.00..',
            '..0..',
            '..0..',
            '.....']]

T_SHAPE = [['.....',
            '..0..',
            '.000.',
            '.....',
            '.....'],
           ['.....',
            '..0..',
            '..00.',
            '..0..',
            '.....'],
           ['.....',
            '.....',
            '.000.',
            '..0..',
            '.....'],
           ['.....',
            '..0..',
            '.00..',
            '..0..',
            '.....']]

SHAPES = [S_SHAPE, Z_SHAPE, I_SHAPE, O_SHAPE, J_SHAPE, L_SHAPE, T_SHAPE]
SHAPE_COLORS = [
    (0, 255, 0),    # S_SHAPE
    (255, 0, 0),    # Z_SHAPE
    (0, 255, 255),  # I_SHAPE
    (255, 255, 0),  # O_SHAPE
    (255, 165, 0),  # J_SHAPE
    (0, 0, 255),    # L_SHAPE
    (128, 0, 128)   # T_SHAPE
]

# Pre-load sounds
CLEARED_SOUND = pygame.mixer.Sound('spill/tetris/musikk/clear.wav')
GAME_OVER_SOUND = pygame.mixer.Sound('spill/tetris/musikk/gameover.wav')
BACKGROUND_MUSIC = pygame.mixer.Sound('spill/tetris/musikk/Tetris_theme_song.wav')
BACKGROUND_MUSIC.play(loops=-1)
BACKGROUND_MUSIC.set_volume(0.01)

class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0

def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]

    for (j, i), color in locked_positions.items():
        if i > -1:
            grid[i][j] = color
    return grid

def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j - 2, shape.y + i - 4))
    return positions

def valid_space(shape, grid):
    accepted_positions = [
        [(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)
    ]
    accepted_positions = [pos for sub in accepted_positions for pos in sub]

    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True

def check_lost(positions):
    for _, y in positions:
        if y < 1:
            return True
    return False

def get_shape():
    return Piece(5, 0, random.choice(SHAPES))

def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont('font/Roboto-Black.ttf', size)
    label = font.render(text, True, color)

    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - label.get_width() / 2,
                         TOP_LEFT_Y + PLAY_HEIGHT / 2 - label.get_height() / 2))

def draw_grid(surface, grid):
    sx = TOP_LEFT_X
    sy = TOP_LEFT_Y
    for i in range(len(grid)):
        # Horizontal lines
        pygame.draw.line(surface, (128, 128, 128),
                         (sx, sy + i * BLOCK_SIZE),
                         (sx + PLAY_WIDTH, sy + i * BLOCK_SIZE))
        # Vertical lines
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128),
                             (sx + j * BLOCK_SIZE, sy),
                             (sx + j * BLOCK_SIZE, sy + PLAY_HEIGHT))

def clear_rows(grid, locked):
    cleared_lines = 0
    rows_to_remove = []

    for i in range(len(grid)-1, -1, -1):
        if (0, 0, 0) not in grid[i]:
            rows_to_remove.append(i)

    if rows_to_remove:
        for row in rows_to_remove:
            CLEARED_SOUND.play()
            cleared_lines += 1
            for j in range(len(grid[row])):
                try:
                    del locked[(j, row)]
                except KeyError:
                    continue

        # Shift every row above down
        for key in sorted(locked.keys(), key=lambda x: x[1])[::-1]:
            x, y = key
            num_cleared = sum(1 for row in rows_to_remove if y < row)
            if num_cleared > 0:
                new_key = (x, y + num_cleared)
                locked[new_key] = locked.pop(key)

    return cleared_lines

def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('font/Roboto-Black.ttf', 35)
    label = font.render('Next Shape', True, (255, 255, 255))

    sx = TOP_LEFT_X + PLAY_WIDTH + 50
    sy = TOP_LEFT_Y + PLAY_HEIGHT / 2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    surface.blit(label, (sx, sy - 30))
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color,
                                 (sx + j * BLOCK_SIZE, sy + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

def draw_window(surface, grid, score=0):
    surface.fill((0, 0, 0))
    font = pygame.font.SysFont('font/Roboto-Black.ttf', 60)
    label = font.render('Tetris', True, (255, 255, 255))

    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - label.get_width() / 2, 30))

    # Draw score
    font = pygame.font.SysFont('font/Roboto-Black.ttf', 30)
    label = font.render(f'Score: {score}', True, (255, 255, 255))

    sx = TOP_LEFT_X - 200
    sy = TOP_LEFT_Y + 200
    surface.blit(label, (sx + 20, sy + 160))

    # Draw grid and board
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j],
                             (TOP_LEFT_X + j * BLOCK_SIZE,
                              TOP_LEFT_Y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    # Draw grid lines and border
    draw_grid(surface, grid)
    pygame.draw.rect(surface, (255, 0, 0),
                     (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 5)

def main(win):
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    score = 0

    while run:
        fall_speed = 0.27  # Adjust as needed
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        # Piece falling logic
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                # Move left
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                # Move right
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                # Rotate
                elif event.key == pygame.K_UP:
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)
                # Move down
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1

        shape_pos = convert_shape_format(current_piece)

        # Add piece to the grid for drawing
        for x, y in shape_pos:
            if y > -1:
                grid[y][x] = current_piece.color

        # Piece hit the ground
        if change_piece:
            for pos in shape_pos:
                locked_positions[(pos[0], pos[1])] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            # Clear rows and update score
            cleared_lines = clear_rows(grid, locked_positions)
            if cleared_lines > 0:
                score += cleared_lines * 10

        draw_window(win, grid, score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        # Check if user lost
        if check_lost(locked_positions):
            draw_text_middle("YOU LOST!", 80, (255, 255, 255), win)
            pygame.display.update()
            GAME_OVER_SOUND.play()
            pygame.time.delay(2000)
            run = False

def main_menu(win):
    run = True
    while run:
        win.fill((0, 0, 0))
        draw_text_middle('Press Any Key to Play', 60, (255, 255, 255), win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                main(win)
    pygame.quit()

# Set up the display
win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')

# Start the game
main_menu(win)
