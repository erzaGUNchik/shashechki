import pygame
import sys

# Инициализация pygame
pygame.init()

# Определение размеров экрана и ячеек
WIDTH, HEIGHT = 800, 800
GRID_SIZE = 8
CELL_SIZE = WIDTH // GRID_SIZE

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (220, 160, 100)
DARK_BROWN = (139, 69, 19)
SELECTED_COLOR = (0, 255, 0)  # Цвет для выделенной шашки (зеленый)
BUTTON_COLOR = (100, 200, 100)  # Цвет кнопки
BUTTON_HOVER_COLOR = (150, 250, 150)  # Цвет кнопки при наведении

# Шрифты
font = pygame.font.SysFont("Arial", 30)


# Класс для представления шашки
class Checker:
    def __init__(self, color, x, y):
        self.color = color
        self.x = x
        self.y = y
        self.king = False

    def make_king(self):
        if (self.color == 'white' and self.y == 0) or (self.color == 'black' and self.y == GRID_SIZE - 1):
            self.king = True

    def draw(self, screen, selected=False):
        center_x = self.x * CELL_SIZE + CELL_SIZE // 2
        center_y = self.y * CELL_SIZE + CELL_SIZE // 2
        color = WHITE if self.color == 'white' else BLACK

        if selected:
            pygame.draw.circle(screen, SELECTED_COLOR, (center_x, center_y), CELL_SIZE // 3 + 5)

        pygame.draw.circle(screen, color, (center_x, center_y), CELL_SIZE // 3)

        if self.king:
            pygame.draw.circle(screen, (255, 215, 0), (center_x, center_y), CELL_SIZE // 6)


# Класс для игрового поля
class Board:
    def __init__(self):
        self.board = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.selected_checker = None
        self.current_player = 'white'
        self.create_checkers()

    def create_checkers(self):
        for y in range(3):
            for x in range((y + 1) % 2, GRID_SIZE, 2):
                self.board[y][x] = Checker('black', x, y)

        for y in range(5, GRID_SIZE):
            for x in range((y + 1) % 2, GRID_SIZE, 2):
                self.board[y][x] = Checker('white', x, y)

    def draw(self, screen):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                color = LIGHT_BROWN if (x + y) % 2 == 0 else DARK_BROWN
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        for row in self.board:
            for checker in row:
                if checker:
                    selected = checker == self.selected_checker
                    checker.draw(screen, selected)

    def is_valid_move(self, checker, to_x, to_y):
        if not (0 <= to_x < GRID_SIZE and 0 <= to_y < GRID_SIZE):
            return False

        target = self.board[to_y][to_x]
        if target is not None:
            return False

        dx = abs(to_x - checker.x)
        dy = abs(to_y - checker.y)

        if dx != dy:
            return False

        if checker.king:
            step_x = (to_x - checker.x) // dx if dx != 0 else 0
            step_y = (to_y - checker.y) // dy if dy != 0 else 0

            for i in range(1, dx):
                middle_x = checker.x + i * step_x
                middle_y = checker.y + i * step_y

                middle_checker = self.board[middle_y][middle_x]
                if middle_checker and middle_checker.color != checker.color:
                    after_x = middle_x + step_x
                    after_y = middle_y + step_y
                    if (0 <= after_x < GRID_SIZE and
                            0 <= after_y < GRID_SIZE and
                            not self.board[after_y][after_x]):
                        return True

            return True

        else:
            if checker.color == 'white' and to_y > checker.y:
                return False

            if checker.color == 'black' and to_y < checker.y:
                return False

            if dx == 1:
                return True

            elif dx == 2:
                middle_x = (checker.x + to_x) // 2
                middle_y = (checker.y + to_y) // 2

                middle_checker = self.board[middle_y][middle_x]
                if middle_checker and middle_checker.color != checker.color:
                    target_after_jump = self.board[to_y][to_x]
                    if target_after_jump is None:
                        return True

        return False

    def make_move(self, checker, to_x, to_y):
        step_count = max(abs(to_x - checker.x), abs(to_y - checker.y))

        if abs(to_x - checker.x) == 2:
            middle_x = (checker.x + to_x) // 2
            middle_y = (checker.y + to_y) // 2

            middle_checker = self.board[middle_y][middle_x]
            if middle_checker:
                self.board[middle_y][middle_x] = None

        self.board[to_y][to_x] = checker
        self.board[checker.y][checker.x] = None

        checker.x, checker.y = to_x, to_y

        # Проверяем необходимость превращения в дамку после движения.
        checker.make_king()

    def get_checker_at(self, x, y):
        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            return self.board[y][x]
        return None

    def is_game_over(self):
        black_pieces = sum(1 for row in self.board for cell in row if cell and cell.color == 'black')
        white_pieces = sum(1 for row in self.board for cell in row if cell and cell.color == 'white')

        return black_pieces == 0 or white_pieces == 0


def draw_menu(screen):
    screen.fill(WHITE)

    title_text = font.render("Checkers Game", True, BLACK)
    play_button_text = font.render("Играть", True, BLACK)
    stats_button_text = font.render("Статистика", True, BLACK)

    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    play_button_rect = play_button_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
    stats_button_rect = stats_button_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))

    button_color_current_play = BUTTON_COLOR
    button_color_current_stats = BUTTON_COLOR

    mouse_pos = pygame.mouse.get_pos()

    if play_button_rect.collidepoint(mouse_pos):
        button_color_current_play = BUTTON_HOVER_COLOR

    if stats_button_rect.collidepoint(mouse_pos):
        button_color_current_stats = BUTTON_HOVER_COLOR

    pygame.draw.rect(screen,
                     button_color_current_play,
                     play_button_rect.inflate(20, 20))

    pygame.draw.rect(screen,
                     button_color_current_stats,
                     stats_button_rect.inflate(20, 20))

    screen.blit(title_text, title_rect)
    screen.blit(play_button_text, play_button_rect)
    screen.blit(stats_button_text, stats_button_rect)


def show_statistics():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Статистика")

    running = True

    # Чтение результатов из файла и отображение их на экране.
    with open("game_results.txt", "r") as file:
        results_lines = file.readlines()

    while running:
        screen.fill(WHITE)

        title_text = font.render("Статистика", True, BLACK)

        screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4)))

        # Отображение результатов.
        for i, line in enumerate(results_lines):
            result_text = font.render(line.strip(), True, BLACK)
            screen.blit(result_text, result_text.get_rect(center=(WIDTH // 2, HEIGHT // 4 + (i + 1) * 30)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # Закрытие окна статистики по нажатию клавиши.
                running = False

    main_menu()  # Возвращаемся в главное меню после закрытия окна статистики.


def main_menu():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Checkers Menu")

    running = True

    while running:
        draw_menu(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                play_button_rect = pygame.Rect(WIDTH // 2 - 70,
                                               HEIGHT // 2 - 30,
                                               140,
                                               60)

                stats_button_rect = pygame.Rect(WIDTH // 2 - 70,
                                                HEIGHT // 2 + 30,
                                                140,
                                                60)

                if play_button_rect.collidepoint(mouse_pos):
                    play_game()

                elif stats_button_rect.collidepoint(mouse_pos):
                    show_statistics()  # Показать статистику.

    pygame.quit()
    sys.exit()


def play_game():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Checkers")

    board = Board()

    running = True

    while running:
        screen.fill((255, 255, 255))
        board.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                x //= CELL_SIZE
                y //= CELL_SIZE
                checker = board.get_checker_at(x, y)

                if board.selected_checker:
                    # Перемещение шашки
                    if board.is_valid_move(board.selected_checker, x, y):
                        board.make_move(board.selected_checker, x, y)
                        board.selected_checker = None
                        board.current_player = 'black' if board.current_player == 'white' else 'white'
                    else:
                        board.selected_checker = None

                elif checker and checker.color == board.current_player:
                    board.selected_checker = checker

            if board.is_game_over():
                winner_color = board.current_player
                print(f"Game Over! {winner_color} wins!")

                # Сохранение результата в файл
                with open("game_results.txt", "a") as file:
                    file.write(f"{winner_color} wins!\n")

                running = False

    main_menu()  # Возвращаемся в главное меню после завершения игры.


if __name__ == "__main__":
    main_menu()
