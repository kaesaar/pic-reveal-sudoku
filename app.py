import tkinter
from tkinter import filedialog
import pygame
import io
import PIL
from PIL import Image


pygame.init()

def pick_image_file():
    root = tkinter.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select Background",
        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )
    root.destroy()
    return file_path

SUDOKU_GRID_SIZE = 540
CELL_SIZE = SUDOKU_GRID_SIZE // 9
LINE_COLOR = (0, 0, 0)
NUM_COLOR = (50, 50, 50)
USER_NUM_COLOR = (0, 0, 255)
HIGHLIGHT_COLOR = (255, 255, 0)

HOVER_LINE_COLOR = (180, 200, 255) # light blue
SAME_NUM_HIGHLIGHT = (255, 200, 100) # yellow

FONT = pygame.font.SysFont("arial", 40)

WHITE = (255, 255, 255)
OVERLAY_COLOR = (255, 255, 255)

def process_image(file_path, target_size=SUDOKU_GRID_SIZE):
    try:
        source_img = Image.open(file_path).convert("RGB")
    except FileNotFoundError:
        print("Image file not found")
        return None
    
    img = source_img.resize((target_size, target_size), Image.Resampling.LANCZOS)

    return img

def pil_to_pygame(pil_image):
    """Convert pillow image object to a pygame surface"""
    mode = pil_image.mode
    size = pil_image.size
    data = pil_image.tobytes()
    return pygame.image.fromstring(data, size, mode)

def reveal_cell(row, col, overlay_surface):
    """make specified cell transparent"""

    transparent_hole = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    transparent_hole.fill((0, 0, 0, 0))
    
    rect_x = col * CELL_SIZE
    rect_y = row * CELL_SIZE

    overlay_surface.blit(transparent_hole, (rect_x, rect_y), special_flags=pygame.BLEND_RGBA_MULT)

def rehide_cell(row, col, overlay_surface):
    """re-cover a revealed cell by blitting a patch over it"""
    opaque_patch = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    opaque_patch.fill(OVERLAY_COLOR + (240,))

    rect_x = col * CELL_SIZE
    rect_y = row * CELL_SIZE

    opaque_patch.set_alpha(240)
    overlay_surface.blit(opaque_patch, (rect_x, rect_y))


class SudokuGame:
    def __init__(self):
        self.solved = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9]
        ]

        self.initial = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ]

        self.current_board = [row[:] for row in self.initial]
        self.selected = None
        self.hovered = None
        self.all_solved = False
    def is_solved(self):
        """check if current board == solved board"""
        for r in range(9):
            for c in range(9):
                if self.current_board[r][c] != self.solved[r][c]:
                    return False
        return True
    
WIDTH = SUDOKU_GRID_SIZE
HEIGHT = 600
SCREEN_SIZE = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Pic Sodoku")

game = SudokuGame()

def draw_grid(screen, game, overlay_surface):

    if not game.all_solved:
        game.all_solved = game.is_solved()

    temp_guide_surface = pygame.Surface((SUDOKU_GRID_SIZE, SUDOKU_GRID_SIZE), pygame.SRCALPHA)
    
    if game.hovered and not game.all_solved:
        r, c = game.hovered
        
        # row highlight
        row_rect = pygame.Rect(0, r * CELL_SIZE, SUDOKU_GRID_SIZE, CELL_SIZE)
        pygame.draw.rect(temp_guide_surface, HOVER_LINE_COLOR + (100,), row_rect, 0)
        
        # column highlight
        col_rect = pygame.Rect(c * CELL_SIZE, 0, CELL_SIZE, SUDOKU_GRID_SIZE)
        pygame.draw.rect(temp_guide_surface, HOVER_LINE_COLOR + (100,), col_rect, 0)

    if game.all_solved:
        for r in range(9):
            for c in range(9):
                reveal_cell(r, c, overlay_surface)
    screen.blit(overlay_surface, (0, 0))

    screen.blit(temp_guide_surface, (0, 0))

    # selected number global highlighter
    highlight_value = None
    if game.selected:
        r_sel, c_sel = game.selected
        highlight_value = game.current_board[r_sel][c_sel]

    for r in range(9):
        for c in range(9):
            num = game.current_board[r][c]

            if num != 0 and num == highlight_value and not game.all_solved:
                rect_x = c * CELL_SIZE
                rect_y = r * CELL_SIZE
                same_num_surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
                same_num_surface.fill(SAME_NUM_HIGHLIGHT)
                same_num_surface.set_alpha(150) # for better visibility
                screen.blit(same_num_surface, (rect_x, rect_y))

            if num != 0:
                color = NUM_COLOR if game.initial[r][c] != 0 else USER_NUM_COLOR

                text = FONT.render(str(num), True, color)

                # center of the cells
                x = c * CELL_SIZE + (CELL_SIZE - text.get_width()) // 2
                y = r * CELL_SIZE + (CELL_SIZE - text.get_height()) // 2
                screen.blit(text, (x, y))

    if game.selected and not game.all_solved:
        r, c = game.selected

        rect_x = c * CELL_SIZE
        rect_y = r * CELL_SIZE

        highlight_surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
        highlight_surface.fill(HIGHLIGHT_COLOR)
        highlight_surface.set_alpha(100)

        screen.blit(highlight_surface, (rect_x, rect_y))

    for i in range(10):
        thickness = 3 if i % 3 == 0 else 1

        # horizontal lines
        pygame.draw.line(screen, LINE_COLOR, (0, i * CELL_SIZE), (SUDOKU_GRID_SIZE, i * CELL_SIZE), thickness)

        # vertical lines
        pygame.draw.line(screen, LINE_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, SUDOKU_GRID_SIZE), thickness)

SudokuGame.is_solved = lambda self: all(self.current_board[r][c] == self.solved[r][c] for r in range(9) for c in range(9))

running = True

sudoku_background_image = None
overlay_surface = None

image_path = pick_image_file()

if image_path:
    pil_img = process_image(image_path, target_size=SUDOKU_GRID_SIZE)
    if pil_img:
        sudoku_background_image = pil_to_pygame(pil_img)

        overlay_surface = pygame.Surface((SUDOKU_GRID_SIZE, SUDOKU_GRID_SIZE), pygame.SRCALPHA)
        overlay_surface.fill(OVERLAY_COLOR + (240,))

    else:
        running = False
else:
    running = False

while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        #stop input if solved
        if game.all_solved:
            continue

        # mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            mouse_x, mouse_y = mouse_pos

            if 0 <= mouse_x < SUDOKU_GRID_SIZE and 0 <= mouse_y < SUDOKU_GRID_SIZE:

                col = mouse_x // CELL_SIZE
                row = mouse_y // CELL_SIZE

                if game.initial[row][col] == 0:
                    game.selected = (row, col)
                else:
                    game.selected = None
            else:
                game.selected = None

        # keyboard
        if event.type == pygame.KEYDOWN and game.selected:
            r, c = game.selected

            if game.initial[r][c] == 0:

                if pygame.K_1 <= event.key <= pygame.K_9:
                    num_to_enter = event.key - pygame.K_0
                    game.current_board[r][c] = num_to_enter
                    
                    if num_to_enter == game.solved[r][c]:
                        reveal_cell(r, c, overlay_surface)
                    else:
                        rehide_cell(r, c, overlay_surface)

                elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                    game.current_board[r][c] = 0
                    rehide_cell(r, c, overlay_surface)

    screen.fill(WHITE)

    if sudoku_background_image and overlay_surface:

        screen.blit(sudoku_background_image, (0,0))

        draw_grid(screen, game, overlay_surface)

    pygame.display.flip()

pygame.quit()