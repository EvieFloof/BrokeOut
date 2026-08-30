import pygame
import pygame.freetype

from core.scene_manager import Scene
from objects.gui import mouse


class DevelopmentScene(Scene):
    # noinspection PyDefaultArgument
    def __init__(self) -> None:
        super().__init__()

        self.color = (159, 0, 0)
        self.shaders = self.game.renderer


    def run(self) -> None:
        self.mouse = mouse.Mouse()

        self.game.event_manager.subscribe(self, "WindowFocusLost")

    def WindowFocusLost(self) -> None:
        self.game.running = False

    def update(self) -> None:
        pass

    def draw(self) -> None:

        surface = pygame.Surface(self.game.window.get_size(), pygame.SRCALPHA)

        pygame.draw.rect(
                    surface,
                    (0, 0, 0, 255),
                    (
                        100, 100,
                        45,
                        45,
                    ),
                )

        self.game.window.blit(surface, (0, 0))

        self.shaders.render_frame()
