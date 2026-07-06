# type: ignore

import pygame
import pygame.freetype

from objects import prototype


class Button(prototype.Entity):
    def __init__(
        self, pos: tuple | list, size: tuple | list, text: str, onclick = None, disabled: bool = False
    ) -> None:
        super().__init__()

        self.font = pygame.freetype.Font("assets/fonts/Monocraft.ttf", 36)
        self.size: list = size
        self.text: str = text
        self.pos: list = pos

        self.disabled: bool = disabled

        self.onclick = onclick

        self.game.event_manager.subscribe(self, "MouseButtonDown")

    def get_collided(self) -> bool:
        button = pygame.Rect(
            (self.pos[0] - (self.size[0] // 2), self.pos[1] - (self.size[1] // 2)),
            self.size,
        )
        return button.collidepoint(pygame.mouse.get_pos())

    def MouseButtonDown(self, event: pygame.Event) -> None:
        if self.get_collided() and event.button == 1:
            if self.onclick is not None:
                self.onclick()

    def set_event_state(self, enabled: bool):
        if enabled:
            self.game.event_manager.subscribe(self, "MouseButtonDown")
        else:
            self.game.event_manager.unsubscribe(self, "MouseButtonDown")

    def draw(
        self,
        surface: pygame.Surface,
        bg_color: tuple | list = (173, 95, 125),
        fg_color: tuple | list = (246, 172, 201),
    ) -> None:
        mouse = pygame.mouse.get_pos()
        button = pygame.Rect(self.pos, self.size)
        self.text_rect = self.font.get_rect(self.text, size=21)
        button.center = self.text_rect.center = self.pos

        pygame.draw.rect(
            surface,
            (
                bg_color[0],
                bg_color[1],
                bg_color[2],
                93 if (button.collidepoint(mouse) and not self.disabled) else 51,
            ),
            button,
            border_radius=3,
        )
        for i in range(1, 3):
            pygame.draw.rect(
                surface,
                fg_color if not self.disabled else (fg_color[0] // 2, fg_color[1] // 2, fg_color[2] // 2,),
                (
                    self.pos[0] - (self.size[0] // 2) + 3 - i,
                    self.pos[1] - (self.size[1] // 2) + 3 - i,
                    self.size[0],
                    self.size[1],
                ),
                1,
                border_radius=2,
            )
        self.font.render_to(
            surface, self.text_rect, self.text, fg_color if not self.disabled else (fg_color[0] // 2, fg_color[1] // 2, fg_color[2] // 2,), size=21
        )
