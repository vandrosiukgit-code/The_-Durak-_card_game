import pygame

from .config import ACTION_DISABLED, BUTTON_COLOR, BUTTON_HOVER, BUTTON_TEXT


class CardAnimation:
    def __init__(
        self,
        start_pos: tuple[float, float],
        end_pos: tuple[float, float],
        duration_ms: int,
        back_img: pygame.Surface,
        front_img: pygame.Surface,
        start_size: tuple[int, int],
        end_size: tuple[int, int],
        flip: bool = False,
        delay_ms: int = 0,
        hide_table_card: tuple[int, bool] | None = None,
    ) -> None:
        self.start_pos = pygame.Vector2(start_pos)
        self.end_pos = pygame.Vector2(end_pos)
        self.duration = duration_ms
        self.start_time = pygame.time.get_ticks() + delay_ms
        self.back_img = back_img
        self.front_img = front_img
        self.flip = flip
        self.start_size = start_size
        self.end_size = end_size
        self.done = False
        self.current_display_img: pygame.Surface | None = None
        self.current_pos = pygame.Vector2(start_pos)
        self.started = False
        self.hide_table_card = hide_table_card

    def update(self) -> None:
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed < 0:
            return
        self.started = True
        progress = min(1.0, elapsed / self.duration)
        ease = progress * progress * (3 - 2 * progress)
        self.current_pos = self.start_pos.lerp(self.end_pos, ease)

        width = self.start_size[0] + (self.end_size[0] - self.start_size[0]) * ease
        height = self.start_size[1] + (self.end_size[1] - self.start_size[1]) * ease

        image = self.back_img
        render_width = width
        if self.flip:
            flip_progress = abs(progress - 0.5) * 2
            render_width = width * flip_progress
            if progress > 0.5:
                image = self.front_img

        self.current_display_img = pygame.transform.smoothscale(
            image,
            (int(max(1, render_width)), int(height)),
        )
        if progress >= 1.0:
            self.done = True

    def draw(self, surface: pygame.Surface) -> None:
        if not self.started or self.current_display_img is None:
            return
        rect = self.current_display_img.get_rect(center=self.current_pos)
        surface.blit(self.current_display_img, rect)
        pygame.draw.rect(surface, BUTTON_TEXT, rect, width=2, border_radius=10)


class Button:
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font) -> None:
        self.rect = rect
        self.text = text
        self.font = font

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int], enabled: bool = True) -> None:
        if not enabled:
            color = ACTION_DISABLED
        else:
            color = BUTTON_HOVER if self.rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, BUTTON_TEXT, self.rect, width=2, border_radius=12)
        label = self.font.render(self.text, True, BUTTON_TEXT)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def is_clicked(self, event: pygame.event.Event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )
