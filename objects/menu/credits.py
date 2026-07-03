import pygame
import pygame.freetype

from objects.prototype import Entity


class Credits(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.font = pygame.freetype.Font("assets/fonts/Monocraft.ttf", 19)
        self.text: list[str] = [
            "Broke Out • By Broke Team (2026)",
            f"Version {self.game.config.release.version} ({self.game.config.release.state})",
            "",
            ">>> Development Team <<<",
            "Lead Developer: Evie",
            "Titouan Brebion-Coïa",
            "Eliot Hartel",
            "",
            ">>> Music <<<",
            "Menu Audio: Evie",
            "Level Audio: Evie",
            "Splash Screen SFX: Nintendo",
            "",
            ">>> Design <<<",
            "Graphic Design: Evie",
            "Color palette: Titouan Brebion-Coïa, Eliot Hartel",
            "Easter-egg Fox: YamikoCrystalYC",
            "",
            ">>> Gameplay <<<",
            "Titouan Brebion-Coïa",
            "Eliot Hartel",
            "",
            ">>> Special thanks to <<<",
            "Cantine, Rémi, Sube, Python, UV, Pygame",
            "And that random guy's website solving a bug in a magic way",
            "Made with love by Broke Team <3"
        ]
        self.scroll: int = 0
        self.scroll_target: int = 0

        self.game.event_manager.subscribe(self, "MouseWheel")

    def MouseWheel(self, event) -> None:
        # self.scroll += event.y * 25
        self.scroll_target += event.y * 30

    def update(self) -> None:
        target_min = -230 if not self.scene.egg else -1
        target_max = -25

        if (self.scroll_target == self.scroll):
            pass
        else:
            self.scroll += (self.scroll_target - self.scroll) * 0.15

            if self.scroll_target < target_min:
                self.scroll_target += (target_min - self.scroll_target) * 0.3
            elif self.scroll_target > target_max:
                self.scroll_target += (target_max - self.scroll_target) * 0.3

    # noinspection PyMethodOverriding
    def draw(self, scene) -> None:
        if scene.egg:
            image = pygame.image.load("assets/images/credits/egg.png")
            scene.surface.blit(
                image,
                (
                    scene.surface.get_rect().center[0] - 213,
                    scene.scroll + scene.surface.get_rect().center[1] - 175,
                ),
            )
            line = "Surprise :3"
            text_rect = self.font.get_rect(line, size=35)
            text_rect.center = (
                scene.surface.get_rect().center[0],
                scene.scroll + scene.surface.get_rect().center[1] + 256,
            )
            self.font.render_to(scene.surface, text_rect, line, (0, 0, 0), size=35)
        else:
            i = 0
            for line in self.text:
                i += 1
                text_rect = self.font.get_rect(line, size=19)
                text_rect.center = (
                    scene.surface.get_rect().center[0],
                    self.scroll + scene.surface.get_rect().center[1] // 2 + (i * 25),
                )
                self.font.render_to(
                    scene.surface, text_rect, line, self.scene.color, size=19
                )