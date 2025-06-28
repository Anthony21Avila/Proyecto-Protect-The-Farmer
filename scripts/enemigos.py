import pygame
import heapq

import pygame
import heapq

class Enemigo:
    def __init__(self, x, y, sprite_data, spritesheet):
        self.posicionX = x
        self.posicionY = y
        self.velocidad = 2
        self.rect = pygame.Rect(self.posicionX - 17, self.posicionY - 17, 35, 35)

        self.sprite_data = sprite_data["enemigos"]
        self.spritesheet = spritesheet
        self.direction = "abajo"
        self.frame_index = 0
        self.frame_delay = 10
        self.frame_counter = 0

        self.path = []
        self.path_index = 1
        self.ultimo_recalculo = 0
        self.recalculo_cada = 300
        self.ultimo_objetivo = (-1, -1)

    def seguir_ruta(self):
        if self.path and self.path_index < len(self.path):
            sig_x, sig_y = self.path[self.path_index]
            destino_x = sig_x * 30 + 15
            destino_y = sig_y * 30 + 15
            dx = destino_x - self.rect.centerx
            dy = destino_y - self.rect.centery
            dist = max(1, (dx**2 + dy**2)**0.5)

            self.posicionX += self.velocidad * dx / dist
            self.posicionY += self.velocidad * dy / dist

            # Dirección visual
            if abs(dx) > abs(dy):
                self.direction = "derecha" if dx > 0 else "izquierda"
            else:
                self.direction = "abajo" if dy > 0 else "arriba"

            self.animar()
            self.path_index += 1 if dist < self.velocidad + 1 else 0

        self.rect.topleft = (self.posicionX - 17, self.posicionY - 17)

    def animar(self):
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_index = (self.frame_index + 1) % len(self.sprite_data[self.direction])
            self.frame_counter = 0

    def dibujar(self, screen):
        frame = self.sprite_data[self.direction][self.frame_index]
        sprite = self.spritesheet.get_sprite(frame["x"], frame["y"], frame["w"], frame["h"])
        screen.blit(sprite, (self.rect.left, self.rect.top))

    def tocar_jugador(self, jugador1_rect):
        return self.rect.colliderect(jugador1_rect)


class Node:
    def __init__(self, x, y, parent=None, g=0, h=0):
        self.x = x
        self.y = y
        self.parent = parent
        self.g = g
        self.h = h
        self.f = g + h

    def __lt__(self, other):
        return self.f < other.f

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(start, end, grid):
    open_list = []
    heapq.heappush(open_list, Node(*start, g=0, h=heuristic(start, end)))
    closed_set = set()

    while open_list:
        current = heapq.heappop(open_list)
        if (current.x, current.y) == end:
            path = []
            while current:
                path.append((current.x, current.y))
                current = current.parent
            return path[::-1]

        closed_set.add((current.x, current.y))

        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = current.x + dx, current.y + dy
            if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid):
                if (nx, ny) in closed_set:
                    continue
                if grid[ny][nx] == 1:
                    continue
                
                extra_cost = 5 if grid[ny][nx] == 2 else 1
                g = current.g + extra_cost
                h = heuristic((nx, ny), end)
                heapq.heappush(open_list, Node(nx, ny, parent=current, g=g, h=h))
    return None
