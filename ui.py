"""Shared ocean palette, typography and cached UI surfaces."""

from functools import lru_cache
import os
from pathlib import Path

import pygame

INK = (5, 28, 45)
PALE = (239, 248, 246)
MUTED = (170, 203, 209)
AQUA = (111, 225, 221)
CORAL = (255, 179, 132)
LINE = (55, 107, 126)


@lru_cache(maxsize=24)
def font(size=20, bold=False):
    # SysFont maps "segoeui" to Segoe UI Light on some Windows installs.
    # Select the actual regular/bold files so small labels retain their weight.
    directory = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    filename = directory / ("segoeuib.ttf" if bold else "segoeui.ttf")
    if filename.is_file():
        return pygame.font.Font(str(filename), size)
    return pygame.font.SysFont("dejavusans,arial", size, bold=bold)


@lru_cache(maxsize=256)
def label(message, size, color, bold):
    return font(size, bold).render(str(message), True, color)


def text(screen, message, pos, size=20, color=PALE, bold=False,
         center=False, max_width=None):
    message = str(message)
    if max_width:
        while message and font(size, bold).size(message)[0] > max_width:
            message = message[:-2] + "…" if len(message) > 2 else ""
    image = label(message, size, color, bold)
    rect = image.get_rect(center=pos) if center else image.get_rect(topleft=pos)
    screen.blit(image, rect)
    return rect


@lru_cache(maxsize=40)
def panel_surface(size, opacity=240):
    layer = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(layer, (6, 33, 50, opacity), layer.get_rect(), border_radius=18)
    pygame.draw.rect(layer, (*LINE, 230), layer.get_rect(), 1, border_radius=18)
    return layer


def panel(screen, rect, opacity=240):
    rect = pygame.Rect(rect)
    screen.blit(panel_surface(rect.size, opacity), rect)


def meter(screen, rect, ratio, color=AQUA):
    rect = pygame.Rect(rect)
    pygame.draw.rect(screen, (31, 64, 80), rect, border_radius=rect.height // 2)
    width = round(rect.width * max(0.0, min(1.0, ratio)))
    if width:
        fill = pygame.Rect(rect.x, rect.y, width, rect.height)
        pygame.draw.rect(screen, color, fill, border_radius=rect.height // 2)
