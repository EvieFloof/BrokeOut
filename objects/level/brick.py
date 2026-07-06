import math
import random

import pygame

from objects.prototype import Entity
from systems.logging import Logger


class Brick(Entity):
    """Brick object, That's, Ewww, A Brick"""

    def __init__(self, pos: list | tuple) -> None:
        super().__init__()

        self.logger: Logger = Logger("objects.brick", False)

        self.pos: list = pos
        self.size: list = [50, 30]

        self.life: int = random.randint(1, 3)
        self.text: str = ""

        # Random color variation
        divisor: int = random.randint(2, 5)
        self.color: list = [c // (divisor // 2) for c in self.scene.color]

    def is_alive(self) -> bool:
        """Check if brick is still alive (This was a trial, I'm making a note here: Huge success)"""
        return self.life > 0

    def draw_text(self) -> None:
        text_rect = self.scene.font.get_rect("•" * self.life, size=16)
        text_rect.center = self.pos

        self.scene.font.render_to(
            self.scene.surface,
            text_rect,
            "•" * self.life,
            self.scene.background_color(),
            size=16,
        )

    def get_rect(self, is_skeleton: bool = False) -> pygame.Rect:
        if is_skeleton:
            size: list = [self.size[0] * 0.9, self.size[1] * 0.9]
        else:
            size: list = self.size
        return pygame.Rect(
            int(self.pos[0] - size[0] / 2 + self.scene.offset[0]),
            int(self.pos[1] - size[1] / 2 + self.scene.offset[1]),
            size[0],
            size[1],
        )

    def draw(self) -> None:
        """Draw the brick"""
        pygame.draw.rect(self.scene.surface, self.color, self.get_rect(), 0)
        self.draw_text()

    def draw_skeleton(self) -> None:
        pygame.draw.rect(self.scene.surface, self.color + [25], self.get_rect(True), 0)

    def handle_hit(self) -> None:
        self.life -= 1
        self.logger.log(f"Brick {self} got hit ({self.life} left)")

        score_change = 1500
        self.scene.score += score_change

    def check_ball_collision(self) -> bool:
        """Check and handle collision with ball"""
        ball = self.scene.ball

        rect = pygame.Rect(
            self.pos[0] - self.size[0] / 2,
            self.pos[1] - self.size[1] / 2,
            self.size[0],
            self.size[1],
        )

        closest_x = max(rect.left, min(ball.pos[0], rect.right))
        closest_y = max(rect.top, min(ball.pos[1], rect.bottom))

        dx = ball.pos[0] - closest_x
        dy = ball.pos[1] - closest_y

        if (dx * dx + dy * dy) < self.game.config.game.ball.radius**2:
            overlap_x = self.game.config.game.ball.radius - abs(dx)
            overlap_y = self.game.config.game.ball.radius - abs(dy)

            if overlap_x < overlap_y:
                ball.velocity[0] *= -1
                ball.pos[0] += math.copysign(
                    overlap_x, dx
                )  # overlap_x value but dx sign
            else:
                ball.velocity[1] *= -1
                ball.pos[1] += math.copysign(
                    overlap_y, dy
                )  # overlap_y value but dy sign

            self.handle_hit()

            self.scene.screen_shake.start(duration=3, magnitude=3)
            self.scene.shaders.set_curvature(0.41)

            return True

        return False


class LargeBrick(Brick):
    def __init__(self, pos: list | tuple) -> None:
        super().__init__(pos)

    def handle_hit(self) -> None:
        if self.scene.player.width >= 220:
            self.scene.player.width = 220
        else:
            self.scene.player.width += 50
        self.life = -1

    def draw_text(self) -> None:
        text_rect = self.scene.font.get_rect("<->", size=16)
        text_rect.center = self.pos

        self.scene.font.render_to(
            self.scene.surface, text_rect, "<->", self.scene.background_color(), size=16
        )


class FastBrick(Brick):
    def __init__(self, pos: list | tuple) -> None:
        super().__init__(pos)

    def handle_hit(self) -> None:
        if self.scene.ball.speed >= 16:
            self.scene.ball.speed = 16
        else:
            self.scene.ball.speed += 2
        self.life = -1

    def draw_text(self) -> None:
        text_rect = self.scene.font.get_rect(">>>", size=16)
        text_rect.center = self.pos

        self.scene.font.render_to(
            self.scene.surface, text_rect, ">>>", self.scene.background_color(), size=16
        )


class BrickGroup(Entity):
    def __init__(self) -> None:
        self.logger = Logger("objects.brick.brickgroup")
        self.bricks = []

        super().__init__()

        self.logger.log("Initialised brick group")

    def generate_bricks(self) -> None:
        """Generate brick layout"""
        self.bricks = []
        level = self.scene.levels[(self.scene.level - 1) % len(self.scene.levels)]
        self.logger.log(f"{level=}", "group_verbose")
        for line in range(len(level)):
            for brick in range(len(level[line])):
                if level[line][brick] != 0:
                    brick = level[line][brick](
                        (
                            (self.game.config.graphics.render.width // 5 - 5)
                            + ((line % 2) * 13)
                            + 51
                            + (brick * 53),
                            59 + (line * 33),
                        )
                    )
                    self.bricks.append(brick)

    def update(self) -> None:
        if not self.bricks:
            self.logger.log(
                f"All bricks are broken, advancing level {self.scene.level}"
            )
            self.scene.trigger_next_level()
            self.generate_bricks()

        new_bricks = []
        for brick in self.bricks:
            if brick.is_alive():
                brick.check_ball_collision()
                new_bricks.append(brick)
        self.bricks = new_bricks

    def draw(self) -> None:
        for brick in self.bricks:
            if brick.is_alive():
                brick.draw()
            else:
                self.bricks.remove(brick)


class BricksSkeleton(Entity):
    def __init__(self) -> None:
        super().__init__()

        self.logger: Logger = Logger("objects.brick.bricks_skeleton")
        self.bricks: list = []

        self.level: list = self.scene.levels[self.scene.level % len(self.scene.levels)]

        self.logger.log("Initialised brick group")
        for line in range(len(self.level)):
            for brick in range(len(self.level[line])):
                if self.level[line][brick] != 0:
                    brick = self.level[line][brick](
                        (
                            (self.game.config.graphics.render.width // 5 - 5)
                            + ((line % 2) * 13)
                            + 51
                            + (brick * 53),
                            59 + (line * 33),
                        )
                    )
                    self.bricks.append(brick)

    def draw(self) -> None:
        for brick in self.bricks:
            brick.draw_skeleton()
