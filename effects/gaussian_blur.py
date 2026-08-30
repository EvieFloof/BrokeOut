import cv2
import numpy as np
import pygame
from pygame import Surface

def gaussian_blur(surface: Surface, radius: int) -> Surface:
    if radius <= 0:
        return surface.copy()

    rgb = np.ascontiguousarray(pygame.surfarray.array3d(surface))
    rgb = cv2.GaussianBlur(rgb, (0, 0), sigmaX=radius)
    result = pygame.surfarray.make_surface(rgb)

    if surface.get_flags() & pygame.SRCALPHA:
        alpha = np.ascontiguousarray(pygame.surfarray.array_alpha(surface))
        alpha = cv2.GaussianBlur(alpha, (0, 0), sigmaX=radius)
        result = result.convert_alpha()
        pygame.surfarray.pixels_alpha(result)[:] = alpha

    return result