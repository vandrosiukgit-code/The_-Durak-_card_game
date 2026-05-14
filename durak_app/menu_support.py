import math
import os

import pygame


class ResourceManager:
    def __init__(self, empty_color, frame_color):
        self.cache = {}
        self.empty_color = empty_color
        self.frame_color = frame_color

    def get_img(self, folder, filename, size):
        size_int = (int(size[0]), int(size[1]))
        if not filename:
            return self._make_placeholder(size_int)
        key = (folder, filename, size_int)
        if key not in self.cache:
            path = os.path.join(folder, filename) if folder else filename
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, size_int)
                self.cache[key] = img
            except Exception:
                self.cache[key] = self._make_placeholder(size_int)
        return self.cache[key]

    def _make_placeholder(self, size):
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surf, self.empty_color, (0, 0, *size), border_radius=10)
        pygame.draw.rect(surf, self.frame_color, (0, 0, *size), 1, border_radius=10)
        return surf


class DynamicSquareGrid:
    def __init__(self, parent_height, padding, spacing_ratio=0.1, aspect_ratio=1.0):
        self.parent_height = parent_height
        self.padding = padding
        self.spacing_ratio = spacing_ratio
        self.aspect_ratio = aspect_ratio
        self.S = parent_height - (2 * padding)
        self.rect = pygame.Rect(0, 0, self.S, self.S)

    def calculate_and_draw(
        self,
        surface,
        x,
        y,
        items,
        res_folder,
        res_manager,
        click_list,
        action_prefix,
        labels=None,
        draw_text_fn=None,
        mouse_pos=None,
        colors=None,
    ):
        colors = colors or {}
        total_elements = len(items)
        N = 2 if total_elements <= 4 else math.ceil(math.sqrt(total_elements))
        N = max(1, N)

        cell_size = self.S / N
        item_h = cell_size * (1 - self.spacing_ratio)
        item_w = item_h * self.aspect_ratio
        offset_x = (cell_size - item_w) / 2
        text_space = 24 if labels else 0
        free_space_y = cell_size - (item_h + text_space)
        offset_y = (free_space_y / 3) * 2 if labels else free_space_y / 2

        self.rect.x = x
        self.rect.y = y
        pygame.draw.rect(surface, colors.get("grid_base"), self.rect, border_radius=12)
        pygame.draw.rect(surface, colors.get("frame"), self.rect, 1, border_radius=12)

        total_cells = N * N
        for k in range(total_cells):
            row = math.floor(k / N)
            col = k % N
            x_local = col * cell_size
            y_local = row * cell_size
            final_x = self.rect.x + x_local + offset_x
            final_y = self.rect.y + y_local + offset_y
            current_rect = pygame.Rect(final_x, final_y, item_w, item_h)
            is_hovered = mouse_pos and current_rect.collidepoint(mouse_pos)

            if k < total_elements:
                if is_hovered:
                    scale = 1.05
                    hover_w = item_w * scale
                    hover_h = item_h * scale
                    hover_x = final_x - (hover_w - item_w) / 2
                    hover_y = final_y - (hover_h - item_h) / 2
                    draw_rect = pygame.Rect(hover_x, hover_y, hover_w, hover_h)
                    size_int = (int(hover_w), int(hover_h))
                    img = res_manager.get_img(res_folder, items[k], size_int)
                    surface.blit(img, draw_rect)
                    pygame.draw.rect(surface, colors.get("highlight"), draw_rect, width=3, border_radius=10)
                else:
                    size_int = (int(item_w), int(item_h))
                    img = res_manager.get_img(res_folder, items[k], size_int)
                    surface.blit(img, current_rect)
                    pygame.draw.rect(surface, colors.get("frame"), current_rect, width=1, border_radius=10)
                click_list.append((current_rect, f"{action_prefix}_{k}"))
            else:
                pygame.draw.rect(surface, colors.get("empty_slot"), current_rect, border_radius=10)
                pygame.draw.rect(surface, colors.get("frame"), current_rect, 1, border_radius=10)

            if labels and k < len(labels) and draw_text_fn:
                text_y = current_rect.bottom + 5
                label_color = colors.get("highlight") if is_hovered else colors.get("text")
                draw_text_fn(labels[k], (current_rect.centerx, text_y), size=14, color=label_color, anchor="midtop")
