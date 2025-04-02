import pygame
import sys
import random
import copy
import time

pygame.init()
#game settings
WIDTH,HEIGHT = 540,600
SCREEN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Sudoku")

BG_COLOR = (246,247,241)
LINE_COLOR = (46,0,0)
HIGHLIGHT_COLOR = (214,214,174)
INCORRECT_COLOR = (255,100,100)
FONT = pygame.font.Font(None,30)
SMALL_FONT = pygame.font.Font(None,24)

 
CELL_SIZE = WIDTH//9
SELECTED_CELL = None
incorrect_cell = set() 
attempts = 3 #num of errors

# generate a valid board
def generate_full_board():
    board = [[0] * 9 for _ in range(9)]
    
    def is_valid(board, row, col, num):
        start_row, start_col = row // 3 * 3, col // 3 * 3
        return all(
            num != board[row][i] and num != board[i][col] and num != board[start_row + i // 3][start_col + i % 3]
            for i in range(9)
        )
    
    def fill_board(row=0, col=0):
        if row == 9:
            return True  # 棋盤填滿
        next_row, next_col = (row, col + 1) if col < 8 else (row + 1, 0)
        nums = list(range(1, 10))
        random.shuffle(nums)

        for num in nums:
            if is_valid(board, row, col, num):
                board[row][col] = num
                if fill_board(next_row, next_col):
                    return True
                board[row][col] = 0  # 回溯
        return False  # 無法填滿，需回溯

    fill_board()
    return board
#create a puzzle by removing cells based on the number you selected
def create_puzzle(board, num_cells_to_remove):
    puzzle = copy.deepcopy(board)
    while num_cells_to_remove > 0:
        row, col = random.randint(0, 8), random.randint(0, 8)
        if puzzle[row][col] != 0:
            puzzle[row][col] = 0
            num_cells_to_remove -= 1
    return puzzle

#draw the board grid
def draw_grid():
    SCREEN.fill(BG_COLOR)
    for row in range(9):
        for col in range(9):
            cell_x = col * CELL_SIZE
            cell_y = row * CELL_SIZE

            #Highlight selected cell 
            if SELECTED_CELL == (row, col):
                pygame.draw.rect(SCREEN,HIGHLIGHT_COLOR,(cell_x,cell_y,CELL_SIZE,CELL_SIZE))
            elif (row, col) in incorrect_cell:
                pygame.draw.rect(SCREEN,INCORRECT_COLOR,(cell_x,cell_y,CELL_SIZE,CELL_SIZE))
            
            #draw numbers
            if BOARD[row][col] != 0:
                text = FONT.render(str(BOARD[row][col]),True,LINE_COLOR)
                SCREEN.blit(text,(cell_x + CELL_SIZE // 3, cell_y + CELL_SIZE // 3))
    #Draw lines 
    for i in range(10):
        width = 4 if i % 3 == 0 else 1
        pygame.draw.line(SCREEN,LINE_COLOR,(0,i * CELL_SIZE), (WIDTH, i * CELL_SIZE), width)
        pygame.draw.line(SCREEN,LINE_COLOR,(i * CELL_SIZE,0), (i * CELL_SIZE,WIDTH), width)
    #display attempts
    attempt_text = SMALL_FONT.render(f"Attempts left: {attempts}", True,LINE_COLOR)
    SCREEN.blit(attempt_text,(10, HEIGHT-40))

#place a number in the selected cell 
def place_number(num):
    global attempts
    if SELECTED_CELL:
        row, col = SELECTED_CELL
        if BOARD[row][col] == 0:  
            if SOLUTION[row][col] == num:
                BOARD[row][col] = num  
                if (row, col) in incorrect_cell:
                    incorrect_cell.remove((row, col))
            else:
                incorrect_cell.add((row, col))
                attempts -= 1
                if attempts == 0:
                    end_game("! GAME OVER !")
    
    
    if check_board_complete():
        end_game("Congratulations~~!")

def check_board_complete():
    for row in range(9):
        for col in range(9):
            if BOARD[row][col] != SOLUTION[row][col]:  
                return False 
    return True 

def end_game(message):
    global attempts
    end_time = time.time()  
    elapsed_time = int(end_time - start_time) 
    minutes = elapsed_time // 60 
    seconds = elapsed_time % 60  

    while True:
        SCREEN.fill(BG_COLOR)
        
        text = FONT.render(message, True, (255, 0, 0))
        time_text = FONT.render(f"Time : {minutes} min {seconds} sec", True, LINE_COLOR)
        restart_text = SMALL_FONT.render("Press R to restart / Q to quit", True, LINE_COLOR)

        SCREEN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 350))
        SCREEN.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, HEIGHT - 320))
        SCREEN.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT - 290))
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    choose_difficulty()
                    attempts = 3
                    return 
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

#Difficulty: number of blanks
def choose_difficulty():
    global BOARD, SOLUTION, attempts, start_time
    difficulty_input = ""

    while True:
        SCREEN.fill(BG_COLOR)

        
        prompt_text = FONT.render("Enter number of cells to remove :", True, LINE_COLOR)
        input_text = FONT.render("then press ENTER to start the game", True, LINE_COLOR)
        entered_text = FONT.render(difficulty_input, True, LINE_COLOR)

        SCREEN.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 - 50))
        SCREEN.blit(input_text, (WIDTH // 2 - input_text.get_width() // 2, HEIGHT // 2))
        SCREEN.blit(entered_text, (WIDTH // 2 - entered_text.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and difficulty_input.isdigit():
                    num_cells_to_remove = int(difficulty_input)
                    if 1 <= num_cells_to_remove <= 80:
                        SOLUTION = generate_full_board()
                        BOARD = create_puzzle(SOLUTION, num_cells_to_remove)
                        start_time = time.time()
                        return
                elif event.key == pygame.K_BACKSPACE:
                    difficulty_input = difficulty_input[:-1]
                elif event.unicode.isdigit():
                    difficulty_input += event.unicode

choose_difficulty()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            col = mouse_x // CELL_SIZE
            row = mouse_y // CELL_SIZE
            SELECTED_CELL = (row, col)

        if event.type == pygame.KEYDOWN:
            if SELECTED_CELL and event.unicode.isdigit() and event.unicode != 0: #num 1-9
                place_number(int(event.unicode))
    draw_grid()
    pygame.display.flip()