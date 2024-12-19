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
        self.color = color  # Цвет шашки ('white' или 'black')
        self.x = x  # Координата x на доске
        self.y = y  # Координата y на доске
        self.king = False  # Статус дамки

    def make_king(self):
        if (self.color == 'white' and self.y == 0) or (self.color == 'black' and self.y == GRID_SIZE - 1):
            self.king = True

    def draw(self, screen, selected=False):
        center_x = self.x * CELL_SIZE + CELL_SIZE // 2
        center_y = self.y * CELL_SIZE + CELL_SIZE // 2
        color = WHITE if self.color == 'white' else BLACK

        # Рисуем обводку для выбранной шашки
        if selected:
            pygame.draw.circle(screen, SELECTED_COLOR, (center_x, center_y), CELL_SIZE // 3 + 5)

        # Рисуем саму шашку
        pygame.draw.circle(screen, color, (center_x, center_y), CELL_SIZE // 3)

        # Рисуем корону для дамки
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
        # Размещение начальных шашек
        for y in range(3):
            for x in range((y + 1) % 2, GRID_SIZE, 2):
                self.board[y][x] = Checker('black', x, y)

        for y in range(5, GRID_SIZE):
            for x in range((y + 1) % 2, GRID_SIZE, 2):
                self.board[y][x] = Checker('white', x, y)

    def draw(self, screen):
        # Рисуем доску
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                color = LIGHT_BROWN if (x + y) % 2 == 0 else DARK_BROWN
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Рисуем шашки
        for row in self.board:
            for checker in row:
                if checker:
                    selected = checker == self.selected_checker
                    checker.draw(screen, selected)

    def is_valid_move(self, checker, to_x, to_y):
        # Проверка на выход за пределы поля
        if not (0 <= to_x < GRID_SIZE and 0 <= to_y < GRID_SIZE):
            return False

        # Проверка на наличие шашки своего цвета на целевой клетке
        target = self.board[to_y][to_x]
        if target is not None:
            return False

        # Проверка на правильность движения шашки
        dx = abs(to_x - checker.x)
        dy = abs(to_y - checker.y)

        if dx != dy:
            return False

        if checker.king:
            # Дамка может перемещаться на любое расстояние по диагонали и захватывать шашки
            step_x = (to_x - checker.x) // dx if dx != 0 else 0
            step_y = (to_y - checker.y) // dy if dy != 0 else 0

            for i in range(1, dx):
                middle_x = checker.x + i * step_x
                middle_y = checker.y + i * step_y

                middle_checker = self.board[middle_y][middle_x]

                if middle_checker and middle_checker.color != checker.color:
                    # Проверяем наличие пустой клетки после вражеской шашки для захвата
                    after_x = middle_x + step_x
                    after_y = middle_y + step_y
                    if (0 <= after_x < GRID_SIZE and
                            0 <= after_y < GRID_SIZE and
                            not self.board[after_y][after_x]):
                        return True

            return True

        else:
            # Обычная шашка может двигаться только вперед по диагонали
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
                    after_x = (checker.x + to_x) // 2
                    after_y = (checker.y + to_y) // 2

                    target_after_jump = self.board[to_y][to_x]
                    if target_after_jump is None:
                        return True

        return False

    def make_move(self, checker, to_x, to_y):
        # Выполнение перемещения с удалением побитой шашки при необходимости

        step_count = max(abs(to_x - checker.x), abs(to_y - checker.y))

        if abs(to_x - checker.x) == 2:
            middle_x = (checker.x + to_x) // 2
            middle_y = (checker.y + to_y) // 2

            middle_checker = self.board[middle_y][middle_x]
            if middle_checker:
                self.board[middle_y][middle_x] = None

                # Обработка перемещения дамки с возможностью захвата нескольких шашек подряд.

        if checker.king and step_count > 1:
            step_x = (to_x - checker.x) // step_count
            step_y = (to_y - checker.y) // step_count

            for i in range(1, step_count):
                current_x = checker.x + i * step_x
                current_y = checker.y + i * step_y

                if i < step_count - 1:
                    middle_checker = self.board[current_y][current_x]
                    if middle_checker and middle_checker.color != checker.color:
                        after_x = current_x + step_x
                        after_y = current_y + step_y
                        if (0 <= after_x < GRID_SIZE and
                                0 <= after_y < GRID_SIZE and
                                not self.board[after_y][after_x]):
                            self.board[current_y][current_x] = None

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
    play_button_text = font.render("Play", True, BLACK)

    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    button_rect = play_button_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    button_color_current = BUTTON_COLOR

    mouse_pos = pygame.mouse.get_pos()

    if button_rect.collidepoint(mouse_pos):
        button_color_current = BUTTON_HOVER_COLOR

    pygame.draw.rect(screen,
                     button_color_current,
                     button_rect.inflate(20, 20))

    screen.blit(title_text, title_rect)
    screen.blit(play_button_text, button_rect)


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
                play_button_rect = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 - 30, 140, 60)
                if play_button_rect.collidepoint(mouse_pos):
                    play_game()

    pygame.quit()
    sys.exit()


# Основная функция игры
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
                print(f"Game Over! {board.current_player} wins!")
                running = False

    pygame.quit()
    sys.exit()


# Запуск игры с главного меню
main_menu()
