"""
systems.renderer - Moteur de rendu de BrokeEngine

EwoFluffy - BrokeTeam - 2025
"""

import time

import moderngl
import numpy as np
import pygame

from core.context import Context
from systems.logging import Logger


# FIXME: Too many attributes for this class
class Renderer(Context):
    """
    Renderer - Instance du moteur de rendu de BrokeEngine

    Une instance de ce moteur est créé pour chaques objets Scene
    """

    def __init__(self, shader_name: str | None = None) -> None:
        super().__init__()

        self.logger: Logger = Logger("systems.renderer")

        self.shader_name = shader_name if self.game.config.debug.shaders else ""
        self.ctx = moderngl.create_context()
        self.ctx.gc_mode = "auto"
        self.start_time = time.time()
        self.setup_shaders()
        self.logger.success(f"Renderer instance {self} initialised")

        self.update_values: bool = True
        self.last_warp: float = 0.0

        self.game.event_manager.subscribe(self, "KeyDown")

    def KeyDown(self, event: pygame.Event):
        if event.key == pygame.K_f:
            self.game.isFullscreen = not self.game.isFullscreen
            self.game.set_pygame_window_mode(self.game.isFullscreen)

    def change_shader(self, shader_name: str) -> None:
        """
        change_shader - Changer le shader utilisé par le moteur de rendu
        ---
        params:
            shader_name: str = Nom du shader dans le dossier "shaders/"
        """

        if self.shader_name != shader_name:
            self.shader_name = shader_name
            self.setup_shaders()

    # noinspection PyAttributeOutsideInit
    def setup_shaders(self) -> None:
        """
        setup_shaders - Méthode d'initialisation des shaders
        """

        if self.shader_name:
            with open(f"shaders/{self.shader_name}.glsl", encoding="utf-8") as f:
                frag_shader_src = f.read()
        else:
            frag_shader_src = """
            #version 330 core

            uniform sampler2D iChannel0;

            in vec2 v_texcoord;
            out vec4 fragColor;

            void main() {
                fragColor = texture(iChannel0, v_texcoord);
            }
            """

        vertex_shader_src = """
        #version 330 core

        in vec2 in_vert;
        out vec2 v_texcoord;

        void main() {
            v_texcoord = (in_vert + 1.0) / 2.0;
            gl_Position = vec4(in_vert, 0.0, 1.0);
        }
        """

        if hasattr(self, "prog"):
            self.prog.release()
        if hasattr(self, "vao"):
            self.vao.release()
        if hasattr(self, "texture"):
            self.texture.release()

        self.prog = self.ctx.program(
            vertex_shader=vertex_shader_src, fragment_shader=frag_shader_src
        )

        vertices = np.array(
            [
                -1.0,
                -1.0,
                1.0,
                -1.0,
                -1.0,
                1.0,
                1.0,
                1.0,
            ],
            dtype="f4",
        )

        vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, vbo, "in_vert")

        self.texture = self.ctx.texture(
            (
                self.game.config.graphics.render.width,
                self.game.config.graphics.render.height,
            ),
            3,
        )
        self.texture.repeat_x = False
        self.texture.repeat_y = False

        self.has_warp: bool = "warp" in self.prog
        self.has_scan: bool = "scan" in self.prog
        self.has_itime: bool = "iTime" in self.prog
        self.has_iresolution: bool = "iResolution" in self.prog
        self.has_ichannel0: bool = "iChannel0" in self.prog

        if self.has_warp:
            self.prog["warp"].value = 0.0
        if self.has_scan:
            self.prog["scan"].value = 0.1
        if self.has_itime:
            self.prog["iTime"].value = 0.0
        if self.has_iresolution:
            self.prog["iResolution"].value = (
                self.game.config.graphics.render.width,
                self.game.config.graphics.render.height,
            )
        if self.has_ichannel0:
            self.prog["iChannel0"].value = 0

        self.logger.success("Shaders initialised")

    def set_curvature(self, curvature: float) -> None:
        """
        set_curvature - Changer la propriété "curvature" du shader crt
        ---
        params:
            - curvature: float = Valeur à donner au moteur de rendu
        """

        if self.has_warp and self.last_warp != curvature:
            self.logger.log(f"Screen curvature change requested to {curvature}")
            self.prog["warp"].value = curvature
            self.last_warp = curvature

    def render_frame(self) -> None:
        """
        render_frame - méthode executé à chaque frames pour la générer
        """

        flipped = pygame.transform.flip(self.game.window, False, True)
        texture_data = pygame.image.tobytes(flipped, "RGB")

        self.texture.write(texture_data)
        self.texture.use(0)

        if self.has_itime:
            current_time = time.time() - self.start_time
            self.prog["iTime"].value = current_time

        if self.has_warp and self.update_values:
            current_warp = self.prog["warp"].value
            if current_warp < 0.5:
                new_warp = current_warp + (0.5 - current_warp) * 0.05
                self.prog["warp"].value = new_warp
                self.last_warp = new_warp

        self.ctx.clear(0.0, 0.0, 0.0)
        self.vao.render(moderngl.TRIANGLE_STRIP)

    def __del__(self) -> None:
        if hasattr(self, "prog"):
            self.prog.release()
        if hasattr(self, "vao"):
            self.vao.release()
        if hasattr(self, "texture"):
            self.texture.release()
