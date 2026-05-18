from __future__ import annotations

import sys
from typing import Any

import pygame
import pygame.scrap


def clipboard_text_bytes(text: str, platform: str | None = None) -> bytes:
    platform_name = sys.platform if platform is None else platform
    if platform_name == "win32":
        return text.encode("mbcs", errors="replace")
    return text.encode("utf-8")


class PygameClipboardAdapter:
    def __init__(
        self,
        scrap_module: Any = pygame.scrap,
        error_type: type[Exception] = pygame.error,
        scrap_text_type: str = pygame.SCRAP_TEXT,
    ) -> None:
        self.scrap_module = scrap_module
        self.error_type = error_type
        self.scrap_text_type = scrap_text_type

    def copy_text(self, text: str) -> str | None:
        try:
            self.scrap_module.init()
            self.scrap_module.put(self.scrap_text_type, clipboard_text_bytes(text))
        except self.error_type as exc:
            return str(exc)
        return None
