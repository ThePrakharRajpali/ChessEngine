"""
This is the main driver file. Responsible for handling user input and displaying game state.
"""
from lib2to3 import pygram
import pygame
import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8  # Dimension of chess board (8x8)
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # For Animation
IMAGES = {}


def load_images():
    """
    Initialize a global dictionary of images.
    Called exactly once in the main.
    """
    pieces = [
        "wp", "wR", "wN", "wB", "wQ", "wK",
        "bp", "bR", "bN", "bB", "bQ", "bK"
    ]

    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(
            pygame.image.load("images/" + piece + ".png"),
            (SQ_SIZE, SQ_SIZE)
        )
        # We can access image by saying IMAGES['wp']


def main():
    """
    main driver of code. 
    will handle input and update the graphics
    """
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    screen.fill(pygame.Color('white'))
    gs = ChessEngine.GameState()
    # print(gs.board)
    load_images()
    running = True

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        pygame.display.flip()


def drawGameState(screen, gs):
    """
    Responsible for graphics within current game state
    """
    drawBoard(screen)  # Draw square on the board
    # add piece highlighting or move suggestions
    drawPieces(screen, gs.board)  # draw pieces on top of squares


def drawBoard(screen):
    """
    Draw the squares on the board.
    Top Left Square is always light.
    """
    colors = [pygame.Color("white"), pygame.Color("gray")]

    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[(row + col) % 2]
            pygame.draw.rect(
                screen,
                color,
                pygame.Rect(
                    col * SQ_SIZE,
                    row * SQ_SIZE,
                    SQ_SIZE,
                    SQ_SIZE
                )
            )


def drawPieces(screen, board):
    """
    Draw Pieces on board using current GameState.board
    """
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                # If not empty, draw the piece on board
                screen.blit(
                    IMAGES[piece],
                    pygame.Rect(
                        col * SQ_SIZE,
                        row * SQ_SIZE,
                        SQ_SIZE,
                        SQ_SIZE
                    )
                )


if __name__ == "__main__":
    main()
