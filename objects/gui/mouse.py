import pygame

from objects import prototype


class Mouse(prototype.Entity):
    def __init__(self) -> None:
        self.cursor = pygame.image.load(
            "assets/images/store/cursor.png"
        ).convert_alpha()
        self.rect = (0, 0, 16, 16)
        self.i = 1
        super().__init__()

    def draw(self) -> None:
        if pygame.mouse.get_focused():
            mousex, mousey = pygame.mouse.get_pos()
            if self.game.config.debug.precise_mouse:
                pygame.draw.rect(
                    self.game.window,
                    [255, 0, 0],
                    (mousex, 0, 1, self.game.config.graphics.render.height),
                )
                pygame.draw.rect(
                    self.game.window,
                    [255, 0, 0],
                    (0, mousey, self.game.config.graphics.render.width, 1),
                )

            self.game.window.blit(self.cursor, (mousex, mousey * self.i))
