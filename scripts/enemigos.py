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

        self.estados = {}
        self.estado_actual = "quieto"

        self.path = []
        self.path_index = 1
        self.ultimo_recalculo = 0
        self.recalculo_cada = 300
        self.ultimo_objetivo = (-1, -1)

    def seguir_ruta(self):
        if not self.path or self.path_index >= len(self.path):
            return
        
        sig_x, sig_y = self.path[self.path_index]
        destino_x = sig_x * 30 + 15
        destino_y = sig_y * 30 + 15

        dx = destino_x - self.rect.centerx
        dy = destino_y - self.rect.centery
        dist = max(1, (dx**2 + dy**2)**0.5)

        self.posicionX += self.velocidad * dx / dist
        self.posicionY += self.velocidad * dy / dist

        if abs(dx) > abs(dy):
            self.direction = "derecha" if dx > 0 else "izquierda"
        else:
            self.direction = "abajo" if dy > 0 else "arriba"

        self.animar()

        if abs(self.rect.centerx - destino_x) < 5 and abs(self.rect.centery - destino_y) < 5:
            self.path_index += 1

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
    
    def actualizar_estado(self, jugador1, jugador2):
        distancia_j1 = self.rect.centerx - jugador1.rect.centerx
        distancia_j1_y = self.rect.centery - jugador1.rect.centery
        distancia_j1_total = (distancia_j1**2 + distancia_j1_y**2)**0.5

        distancia_j2 = self.rect.centerx - jugador2.rect.centerx
        distancia_j2_y = self.rect.centery - jugador2.rect.centery
        distancia_j2_total = (distancia_j2**2 + distancia_j2_y**2)**0.5

        rango_p1 = 50
        rango_p2 = 450
        if distancia_j1_total < rango_p1:
            self.estado_actual = "evadir"
        elif distancia_j2_total < rango_p2:
            self.estado_actual = "perseguir"
        else:
            self.estado_actual = "quieto"


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

def astar(start, end, grid, max_iter=1000):
    open_list = []
    heapq.heappush(open_list, Node(*start, g=0, h=heuristic(start, end)))
    closed_set = set()
    iteraciones = 0

    while open_list and iteraciones < max_iter:
        current = heapq.heappop(open_list)
        iteraciones += 1

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
                if (nx, ny) in closed_set or grid[ny][nx] == 1 or grid[ny][nx] == 3:
                    continue

                extra_cost = 5 if grid[ny][nx] == 2 else 1
                g = current.g + extra_cost
                h = heuristic((nx, ny), end)
                heapq.heappush(open_list, Node(nx, ny, parent=current, g=g, h=h))

    return None

class Estado:
    def __init__(self, nombre, acciones):
        self.nombre = nombre
        self.acciones = acciones

class Accion:
    def __init__(self, nombre, funcion, estado_destino):
        self.nombre = nombre
        self.funcion = funcion
        self.estado_destino = estado_destino

def crear_estados_enemigo(enemigo, p1, p2):
    def ve_a_player2():
        return True

    def evita_player1():
        dx = enemigo.rect.centerx - p1.rect.centerx
        dy = enemigo.rect.centery - p1.rect.centery
        distancia = (dx**2 + dy**2)**0.5
        return distancia < 100

    def quieto_si_nadie():
        dx = enemigo.rect.centerx - p2.rect.centerx
        dy = enemigo.rect.centery - p2.rect.centery
        return (dx**2 + dy**2)**0.5 > 600

    enemigo.estados = {
        "quieto": Estado("quieto", [
            Accion("ir a p2", ve_a_player2, "perseguir")
        ]),
        "perseguir": Estado("persiguiendo a jugador 2", [
            Accion("evitar p1", evita_player1, "evadir"),
            Accion("quedarse quieto", quieto_si_nadie, "quieto")
        ]),
        "evadir": Estado("evitando a jugador 1", [
            Accion("seguir a p2", lambda: not evita_player1(), "perseguir")
        ])
    }

def encontrar_direccion_opuesta(jugador1_rect, enemigo_rect, grid):
    ex, ey = enemigo_rect.centerx // 30, enemigo_rect.centery // 30
    jx, jy = jugador1_rect.centerx // 30, jugador1_rect.centery // 30

    filas, columnas = len(grid), len(grid[0])

    vecinos = [(ex + dx, ey + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] 
               if (dx != 0 or dy != 0)]

    vecinos.sort(key=lambda pos: -((pos[0] - jx) ** 2 + (pos[1] - jy) ** 2))

    for nx, ny in vecinos:
        if 0 <= nx < columnas and 0 <= ny < filas:
            if grid[ny][nx] == 0:
                return (nx, ny)

    return None