"""
core.scene_manager - Gestion de l'affichage des scènes et des entitées

Contenu:

Classe SceneManager
Classe Scene

EwoFluffy - BrokeTeam - 2026
"""

import importlib
import sys

import pygame

from core import context
from systems import logging, renderer


class Scene(context.Context):
    """
    Scene - Écran du jeu pouvant contenir des entitées
    """

    def __init__(self) -> None:
        self.logger = logging.Logger("core.scene_manager.scene")
        self.runtime_timer = 0.0
        super().__init__()
        self.logger.success(f"New scene loaded as {self}")

    def run(self) -> None:
        """
        run - Fonction executée lorsque la scène devient active
        """

        self.logger.log(f"Scene {self} now running")

    def inactive(self) -> None:
        """
        inactive - Fonction executée lorsque la scène va devenir inactive
        """

        self.logger.log(f"Scene {self} now inactive")
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        self.runtime_timer = 0

    def _get_ticks(self) -> float:
        """
        _get_ticks - Retourner le nombre de ticks executée depuis que la scène est active
        """

        return self.runtime_timer

    def update(self) -> None:
        """
        update - Fonction executée à chaque frame pour la logique de la scène
        """

        pass

    def draw(self) -> None:
        """
        draw - Fonction executée à chaque frame pour le rendu de la scène
        """

        pass


# class SceneManager(context.Context):
#     """
#     SceneManager - Orchestrer l'affichage et l'exécution des objets Scene
#     """

#     def __init__(self) -> None:
#         super().__init__()

#         self.logger = logging.Logger("core.scene_manager")
#         self.active = Scene()  # Empty placeholder scene
#         self.scene_cache = {}  # Cache optionnel pour recharger plus vite
#         self.stack = []

#     def set_active_scene(self, scene_name: str, use_cache: bool = True, stack = False) -> Scene:
#         """
#         set_active_scene - Basculer vers une autre scène
#         ---
#         params:
#             - scene_name: str = Nom de la scène dans le dossier "scenes/"
#             - use_cache: bool = Utiliser le cache de scène pour charger la scène selectionnée
#         """

#         self.logger.log(f"Changing active scene to '{scene_name}'")

#         self.game.audio_engine.stop_all()
#         self.active.inactive()
#         if hasattr(self.active, "__module__"):
#             module_name = self.active.__module__
#             if module_name in sys.modules:
#                 del sys.modules[module_name]

#         if use_cache and scene_name in self.scene_cache:
#             self.active = self.scene_cache[scene_name]
#             self.logger.log(f"Loaded '{scene_name}' from cache")
#         else:
#             module_name = f"scenes.{scene_name}"

#             try:
#                 module = importlib.import_module(module_name)
#             except ImportError as e:
#                 self.logger.error(f"Failed to import scene '{scene_name}': {e}")
#                 raise

#             last_segment = scene_name.split(".")[-1]

#             class_name = (
#                 "".join(part.capitalize() for part in last_segment.split("_")) + "Scene"
#             )

#             try:
#                 scene_class = getattr(module, class_name)
#             except AttributeError:
#                 raise AttributeError(
#                     f"The scene '{scene_name}' does not contain a '{class_name}' class."
#                 )

#             scene = scene_class()
#             self.scene_cache[scene_name] = scene
#             self.active = scene
#             self.logger.success(f"Loaded new scene '{scene_name}'")

#         self.game.event_manager.reset()

#         self.game.active_scene = self.active
#         self.active._name = scene_name
#         self.active.run()
#         return self.active

#     def update(self) -> None:
#         """
#         update - Mettre à jour la scène actuelle et incrémenter le timer d'execution
#         """

#         self.active.runtime_timer += 1

#         self.active.update()

#     def draw(self) -> None:
#         """
#         draw - Effectuer les opérations de rendu de la scène
#         """

#         self.active.draw()



class SceneManager(context.Context):
    """
    SceneManager - Orchestrer l'affichage et l'exécution des objets Scene
    """

    def __init__(self) -> None:
        super().__init__()

        self.logger = logging.Logger("core.scene_manager")
        self.scene_cache = {}  # Cache optionnel pour recharger plus vite
        self.stack = [Scene()]
        self.active = self.stack[-1]
    
    # def replace_current_scene(self, scene_name: str, use_cache: bool = True, empty_stack: bool = True):
    def set_active_scene(self, scene_name: str, use_cache: bool = True, empty_stack: bool = True):
        self.logger.log(f"Replacing active scene to '{scene_name}'")

        self.game.audio_engine.stop_all()
        self.stack[-1].inactive()

        if hasattr(self.stack[-1], "__module__"):
            module_name = self.stack[-1].__module__
            if module_name in sys.modules:
                del sys.modules[module_name]

        if empty_stack:
            self.stack = []

        if use_cache and scene_name in self.scene_cache:
            self.stack.append(self.scene_cache[scene_name])
            self.logger.log(f"Loaded '{scene_name}' from cache")
        else:
            module_name = f"scenes.{scene_name}"

            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                self.logger.error(f"Failed to import scene '{scene_name}': {e}")
                raise

            last_segment = scene_name.split(".")[-1]

            class_name = (
                "".join(part.capitalize() for part in last_segment.split("_")) + "Scene"
            )

            try:
                scene_class = getattr(module, class_name)
            except AttributeError:
                raise AttributeError(
                    f"The scene '{scene_name}' does not contain a '{class_name}' class."
                )

            scene = scene_class()
            self.scene_cache[scene_name] = scene
            self.stack.append(scene)
            self.logger.success(f"Loaded new scene '{scene_name}'")

        if empty_stack:
            self.game.event_manager.reset()

        self.game.active_scene = self.stack[-1]
        self.stack[-1]._name = scene_name
        self.stack[-1].run()

        self.active = self.stack[-1]

        return self.stack[-1]

    def add_scene(self, scene_name: str, use_cache: bool = True) -> Scene:
        """
        set_active_scene - Ajouter un scène à la pile
        ---
        """
        self.logger.log(f"Replacing active scene to '{scene_name}'")

        self.stack[-1].inactive()

        if use_cache and scene_name in self.scene_cache:
            self.stack.append(self.scene_cache[scene_name])
            self.logger.log(f"Loaded '{scene_name}' from cache")
        else:
            module_name = f"scenes.{scene_name}"

            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                self.logger.error(f"Failed to import scene '{scene_name}': {e}")
                raise

            last_segment = scene_name.split(".")[-1]

            class_name = (
                "".join(part.capitalize() for part in last_segment.split("_")) + "Scene"
            )

            try:
                scene_class = getattr(module, class_name)
            except AttributeError:
                raise AttributeError(
                    f"The scene '{scene_name}' does not contain a '{class_name}' class."
                )

            scene = scene_class()
            self.scene_cache[scene_name] = scene
            self.stack.append(scene)
            self.logger.success(f"Loaded new scene '{scene_name}'")

        self.game.active_scene = self.stack[-1]
        self.stack[-1]._name = scene_name
        self.stack[-1].run()

        self.active = self.stack[-1]

        return self.stack[-1]


    def update(self) -> None:
        """
        update - Mettre à jour la scène actuelle et incrémenter le timer d'execution
        """

        self.active.runtime_timer += 1

        self.active.update()
        for scene in self.stack[:-1]:
            scene.update()

    def draw(self) -> None:
        """
        draw - Effectuer les opérations de rendu de la scène
        """

        self.active.draw()
        for scene in self.stack[:-1]:
            scene.draw()
