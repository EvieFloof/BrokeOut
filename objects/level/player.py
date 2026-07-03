from typing import TYPE_CHECKING

import pygame

from core.context import GameContext
from objects.prototype import Entity

if TYPE_CHECKING:
    from objects.level.ball import Ball


class Player(Entity, GameContext):
    def __init__(self) -> None:
        super().__init__()

        self.base_width: int = (
            self.game.config.game.player.width_multiplier
            * self.game.config.game.ball.radius
        )
        self.width: int = self.base_width

        self.pos: list[int] = [
            (self.scene.bounds["x_min"] - self.scene.bounds["x_max"]) / 2,
            self.scene.bounds["y_max"] - self.game.config.game.ball.radius - 5,
        ]

        self.autoplay: bool = self.game.config.debug.game.autoplay

    def collides_with_ball(self, ball: 'Ball') -> bool:
        """Check collision with ball"""
        vertical = (
            abs(self.pos[1] - ball.pos[1]) < 2 * self.game.config.game.ball.radius
        )
        horizontal = (
            abs(self.pos[0] - ball.pos[0])
            < self.width / 2 + self.game.config.game.ball.radius
        )
        return vertical and horizontal

    def update(self) -> None:
        x = pygame.mouse.get_pos()[0] if not self.autoplay else self.scene.ball.pos[0]
        x = max(x, self.scene.bounds["x_min"] + self.width / 2)
        x = min(x, self.scene.bounds["x_max"] - self.width / 2)
        self.pos[0] += (x - self.pos[0]) * 0.25

        if self.width > self.base_width:
            self.width = self.width - 0.1

    def draw(self) -> None:
        rect = pygame.Rect(
            int(self.pos[0] - self.width / 2 + self.scene.offset[0]),
            int(self.pos[1] - self.game.config.game.ball.radius + self.scene.offset[1]),
            self.width,
            2 * self.game.config.game.ball.radius,
        )
        pygame.draw.rect(self.scene.surface, self.scene.color, rect, 0)
