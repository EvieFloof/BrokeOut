import random

import pygame
import pygame.freetype

from objects.prototype import Entity


class LogoElement(Entity):
    def __init__(self) -> None:
        super().__init__()

        self.titley: int = self.game.config.graphics.render.height // 2
        self.titlesize: int = 36

        self.font = pygame.freetype.Font("assets/fonts/Monocraft.ttf", 36)
        self.text: str = "Broke Out" if random.randint(1, 15) != 13 else "Just Another Indie Game"

        self.gradient = pygame.transform.scale(
            pygame.image.load("assets/images/store/gradient0.png").convert_alpha(),
            (self.game.config.graphics.render.width, 258),
        )
        self.gradient_rect: tuple = self.gradient.get_rect()

        self.text_rect = None

    def MouseWheel(self, event) -> None:
        # self.scroll += event.y * 25
        self.scroll_target += event.y * 30

    def update(self) -> None:
        if self.text_rect is not None:
            if self.text_rect.center[1] > 100:
                self.titley += (100 - self.titley) * 0.1

        if self.titlesize < 50:
            self.titlesize += (51 - self.titlesize) * 0.1


    def draw(self, surface: pygame.Surface) -> None:
        version, name = (
            self.game.config.release.version,
            self.game.config.release.compliant_name,
        )

        self.game.window.blit(self.gradient, (0, 0))

        if not "credits" in dir(self.scene) or not self.scene.credits:
            self.text_rect = self.font.get_rect(f"Version {version} • {name}", size=19)

            self.text_rect.center = (
                    surface.get_rect().center[0],
                    self.titley + 51,
                )
            self.font.render_to(
                    surface,
                    self.text_rect,
                    f"Version {version} • {name}",
                    self.scene.color,
                    size=19,
                )

        self.text_rect = self.font.get_rect(self.text, size=self.titlesize)

        self.text_rect.center = (surface.get_rect().center[0], self.titley + 5)
        self.font.render_to(
            surface, self.text_rect, self.text, [c // 2 for c in self.scene.color], size=self.titlesize
        )

        self.text_rect.center = (surface.get_rect().center[0], self.titley)
        self.font.render_to(
            surface, self.text_rect, self.text, self.scene.color, size=self.titlesize
        )