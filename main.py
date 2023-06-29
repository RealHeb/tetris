"""
Стрелочки чтобы двигать фигуру
R - Вращение фигуры
Пробел - остановка игры/запуск игры.
"""


import pygame
import time
from numpy import rot90
from copy import deepcopy
from random import randint

class Board:
    # Доску взял из старых задач, когда в Яндекс.Лицее pygame проходили.
    def __init__(self, height, width):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = 10
        self.top = 10
        self.size = 20

    def get_cell(self, mouse_pos):
        for y in range(self.height):
            for x in range(self.width):
                rect1 = pygame.Rect(x * self.size + self.left, y * self.size + self.top, self.size, self.size)
                if rect1.collidepoint(mouse_pos):
                    return y, x
        return None


    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == 1:
                    pygame.draw.rect(screen, 'yellow',
                                     (x * self.size + self.left, y * self.size + self.top, self.size, self.size))
                elif self.board[y][x] == 2:
                    pygame.draw.rect(screen, 'blue',
                                     (x * self.size + self.left, y * self.size + self.top, self.size, self.size))
                elif self.board[y][x] == 3:
                    pygame.draw.rect(screen, 'red',
                                     (x * self.size + self.left, y * self.size + self.top, self.size, self.size))
                elif self.board[y][x] == 4:
                    pygame.draw.rect(screen, 'green',
                                     (x * self.size + self.left, y * self.size + self.top, self.size, self.size))
                elif self.board[y][x] == 5:
                    pygame.draw.rect(screen, 'orange',
                                     (x * self.size + self.left, y * self.size + self.top, self.size, self.size))
                elif self.board[y][x] == 6:
                    pygame.draw.rect(screen, 'pink',
                                     (x * self.size + self.left, y * self.size + self.top, self.size, self.size))
                elif self.board[y][x] == 7:
                    pygame.draw.rect(screen, 'purple',
                                     (x * self.size + self.left, y * self.size + self.top, self.size, self.size))
                elif self.board[y][x] == -1:
                    pygame.draw.rect(screen, 'grey',
                                     (x * self.size + self.left, y * self.size + self.top, self.size, self.size))
                pygame.draw.rect(screen, 'white',
                                 (x * self.size + self.left, y * self.size + self.top, self.size, self.size), 1)



class Piece:
    # Класс падающих фигур. У каждой фигуры есть центр, вокруг которого фигура вращается, который знает обо всех
    # остальных кусках фигуры. Фигура движется вниз только когда это возможно для всех её частей и при
    # удалении линии центр фигуры перемещается в случайную другую её часть.
    def __init__(self, placement_on_board, placement, master_point, color):
        """
        master_point - Точка, по которой будет определятся положение фигуры в пространстве после вращения,
        левая верхняя точка.

        Пример piece (Z фигура):
        [(0, 0), (0, 1), (1, 1), (1, 2)]
        [[1 1 0],
         [0 1 1],
         [0,0,0]]
        (0, 0)
        3 (зелёный)
        """
        self.color = color
        self.placement = placement
        self.master_point = master_point
        self.placement_on_board = placement_on_board

    def fall(self, board):
        # Обработчик доски, выдает новую доску и True, если фигура не коснулась ничего, False если коснулась.
        new_placement_board = []
        new_board = deepcopy(board)
        self.master_point = self.master_point[0] + 1, self.master_point[1]
        for point in self.placement_on_board:
            new_board[point[0]][point[1]] = 0
        for point in self.placement_on_board:
            if not point[0] + 1 == len(board):
                if board[point[0] + 1][point[1]] == 0 or board[point[0] + 1][point[1]] == self.color:
                    new_placement_board.append((point[0] + 1, point[1]))
                    new_board[point[0] + 1][point[1]] = self.color
                else:
                    new_board = board
                    for row in range(len(new_board)):
                        new_board[row] = [-1 if x == self.color else x for x in new_board[row]]
                    return board, True
            else:
                new_board = board
                for row in range(len(new_board)):
                    new_board[row] = [-1 if x == self.color else x for x in new_board[row]]
                return board, True
        self.placement_on_board = new_placement_board
        return new_board, False

    def move_sideways(self, board, value):
        max_x = -1
        min_x = 99
        max_y = -1
        min_y = 99
        for point in self.placement_on_board:
            if point[1] <= min_x:
                min_x = point[1]
            if point[1] >= max_x:
                max_x = point[1]
            if point[0] <= min_y:
                min_y = point[0]
            if point[0] >= max_y:
                max_y = point[0]
        self.max_x = max_x
        self.min_x = min_x
        self.max_y = max_y
        self.min_y = min_y
        new_placement_board = []
        new_board = deepcopy(board)
        if value == 0 or value + self.min_x < 0 or value + self.max_x >= len(board[0]):
            return board
        for old_point in self.placement_on_board:
            new_board[old_point[0]][old_point[1]] = 0
        for point in self.placement_on_board:
            if board[point[0]][point[1] + value] == 0 or board[point[0]][point[1] + value] == self.color:
                new_placement_board.append((point[0], point[1] + value))
                new_board[point[0]][point[1] + value] = self.color
            else:
                return board
        self.placement_on_board = new_placement_board
        self.master_point = self.master_point[0], self.master_point[1] + value
        return new_board

    def get_rotated_piece(self):
        '''Разворачиваем координаты фигуры и ее положение'''
        rotated_piece = rot90(self.placement)
        rotated_placement_board = []
        for row in range(len(rotated_piece)):
            for col in range(len(rotated_piece)):
                if rotated_piece[row][col] == 1:
                    rotated_placement_board.append((row + self.master_point[0], col + self.master_point[1]))
        return rotated_piece, rotated_placement_board

    def rotate(self, board):
        conflicted_with_static = False
        rotated_piece, rotated_board = self.get_rotated_piece()
        new_board = deepcopy(board)
        for old_coord in self.placement_on_board:
            new_board[old_coord[0]][old_coord[1]] = 0
        for coord in rotated_board:
            if not coord[0] < len(board):
                return board
            if coord[1] >= len(board[0]):
                board = piece.move_sideways(board, -1)
                return piece.rotate(board)
            if coord[1] <= -1:
                board = piece.move_sideways(board, 1)
                return piece.rotate(board)
            if board[coord[0]][coord[1]] == -1:
                conflicted_with_static = True
            new_board[coord[0]][coord[1]] = piece.color
        if not conflicted_with_static:
            self.placement = rotated_piece
            self.placement_on_board = rotated_board
            return new_board
        return board

    def copy(self):
        return Piece(deepcopy(self.placement_on_board), deepcopy(self.placement), self.master_point, self.color)


def line_clear(board):
    for row in range(len(board)):
        if board[row].count(-1) == len(board[row]):
            """Создаем доску, в которой будут 'склеены' часть до и после заполненной строки. и добавим новую строку"""
            board = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]] + board[:row] + board[row + 1:]
    return board


def end_game_check(board):
    for i in board[0]:
        if i == -1:
            game_over()


def game_over():
    pass

pygame.init()
size = width, height = 220, 325
screen = pygame.display.set_mode(size)

running = True
activated = True
board = Board(15, 10)
z_piece = Piece([(0, 4), (0, 5), (1, 5), (1, 6)], [[1, 1, 0], [0, 1, 1], [0, 0, 0]], (0, 4), 4)
s_piece = Piece([(0, 5), (0, 6), (1, 4), (1, 5)], [[0, 1, 1], [1, 1, 0], [0, 0, 0]], (0, 4), 3)

L_piece = Piece([(0, 4), (1, 4), (2, 4), (2, 5)], [[1, 0, 0], [1, 0, 0], [1, 1, 0]], (0, 4), 5)
J_piece = Piece([(0, 5), (1, 5), (2, 5), (2, 4)], [[0, 1, 0], [0, 1, 0], [1, 1, 0]], (0, 4), 6)

O_piece = Piece([(0, 4), (0, 5), (1, 4), (1, 5)], [[1, 1], [1, 1]], (0, 4), 1)

I_piece = Piece([(0, 4), (1, 4), (2, 4), (3, 4)], [[1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0]], (0, 4), 2)

T_piece = Piece([(0, 4), (0, 5), (0, 6), (1, 5)], [[1, 1, 1], [0, 1, 0], [0, 0, 0]], (0, 4), 7)

speed = 2
all_pieces = [I_piece, L_piece, z_piece, s_piece, O_piece, J_piece, T_piece]
last_activation = time.time()
piece = all_pieces[randint(0, 6)].copy()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_e:
                activated = not activated
            if event.key == pygame.K_SPACE:
                board.board = piece.rotate(board.board)
            if event.key == pygame.K_LEFT:
                board.board = piece.move_sideways(board.board, -1)
            if event.key == pygame.K_RIGHT:
                board.board = piece.move_sideways(board.board, 1)
    if activated and time.time() - last_activation >= 1 / speed:
        fall_data = piece.fall(board.board)
        board.board = fall_data[0]
        if fall_data[1]:
            board.board = line_clear(board.board)
            piece = all_pieces[randint(0, 6)].copy()
        last_activation = time.time()
    screen.fill((0, 0, 0))
    board.render(screen)
    pygame.display.flip()
