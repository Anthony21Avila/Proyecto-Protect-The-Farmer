import pygame, sys, json, random
from scripts.sprite import Spritesheet
from scripts.players import Player1, Player2
from scripts.enemigos import Enemigo, astar, crear_estados_enemigo, encontrar_direccion_opuesta

pygame.init()
pygame.joystick.init()

altura = 900
ancho = 1500
screen = pygame.display.set_mode((ancho, altura))
pygame.display.set_caption("Protect The Farmer")
pygame.display.set_icon(pygame.image.load("assets/images/icono.png"))
clock = pygame.time.Clock()
fondo = pygame.image.load('assets/images/background.png')
fondo = pygame.transform.scale(fondo, (ancho, altura))
corazon_imagen = corazon_imagen = pygame.transform.scale(pygame.image.load("assets/images/corazones.png").convert_alpha(), (30, 30))
fersa = pygame.image.load("assets/images/fresa.png").convert_alpha()

with open("scripts/sprite_data.json") as f:
    sprite_data = json.load(f)

spritesheet = Spritesheet("assets/images/1.png")

joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for joystick in joysticks:
    joystick.init()
    print(f"Joystick {joystick.get_id()} conectado: {joystick.get_name()}")

def generar_posicion_valida(vacios, ancho, alto, jugador1, jugador2, distancia_segura=150, ancho_rect=35, alto_rect=35):
    for _ in range(100):
        x = random.randint(50, ancho - 50)
        y = random.randint(320, alto - 80)
        rect = pygame.Rect(x - ancho_rect // 2, y - alto_rect // 2, ancho_rect, alto_rect)

        if any(rect.colliderect(v) for v in vacios):
            continue

        if rect.centerx and rect.centery:
            distancia_p1 = ((jugador1.rect.centerx - x)**2 + (jugador1.rect.centery - y)**2)**0.5
            distancia_p2 = ((jugador2.rect.centerx - x)**2 + (jugador2.rect.centery - y)**2)**0.5

            if distancia_p1 < distancia_segura or distancia_p2 < distancia_segura:
                continue

        return x, y
    return None, None

def construir_grid(vacios, p1r):
    filas, columnas = 30, 50
    grid = [[0 for _ in range(columnas)] for _ in range(filas)]

    for v in vacios:
        x1 = v.left // 30
        y1 = v.top // 30
        w = v.width // 30
        h = v.height // 30
        for i in range(w):
            for j in range(h):
                if 0 <= y1 + j < filas and 0 <= x1 + i < columnas:
                    grid[y1 + j][x1 + i] = 3

    px = p1r.centerx // 30
    py = p1r.centery // 30
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            nx, ny = px + dx, py + dy
            if 0 <= nx < columnas and 0 <= ny < filas:
                if grid[ny][nx] == 0:
                    grid[ny][nx] = 2

    return grid

def dibujar_vidas(screen, jugador):
    for i in range(jugador.vidas):
        x = 650 + i * (corazon_imagen.get_width() + 10)
        y = 20
        screen.blit(corazon_imagen, (x, y))

def dibujar_puntos(screen, puntos, fresa_sprite):
    font = pygame.font.SysFont(None, 36)
    texto = font.render(str(puntos), True, (255, 255, 255))

    ancho = screen.get_width()
    screen.blit(fresa_sprite, (ancho - 80, 20))
    screen.blit(texto, (ancho - 40, 25))
    
p1 = Player1(sprite_data, spritesheet)
p2 = Player2(sprite_data, spritesheet)

run = True

p1.crear(screen)
p2.crear(screen)

vacios = [pygame.Rect(200, 320, 200, 200), pygame.Rect(1100, 320, 200, 200), pygame.Rect(650, 470, 200, 200), pygame.Rect(200, 650, 200, 200), pygame.Rect(1100, 650, 200, 200)]

enemigos = []
tiempo_spawn = pygame.time.get_ticks()
tiempo_entre_enemigos = 3000
MAX_ENEMIGOS = 7

fresas = []
ultimo_spawn_fresa = pygame.time.get_ticks()
puntos, umbral_puntos, umbral_anterior = 0, 0, 0
fresa_sprite = fresa_sprite = pygame.transform.scale(pygame.image.load("assets/images/fresa.png").convert_alpha(), (30, 30))
vel_ene = 2

while run:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            run = False

    
    screen.fill((0,0,0))
    screen.blit(fondo, (0,0))
    clock.tick(60)

    for v in vacios:
        pygame.draw.rect(screen, (20, 20, 20), v)

    ahora = pygame.time.get_ticks()
    if ahora - tiempo_spawn > tiempo_entre_enemigos and len(enemigos) < MAX_ENEMIGOS:
        x, y = generar_posicion_valida(vacios, ancho, altura, p1, p2)
        if x is not None and y is not None:
            nuevo_enemigo = Enemigo(x, y, sprite_data, spritesheet, vel_ene)
            nuevo_enemigo.grid = grid
            crear_estados_enemigo(nuevo_enemigo, p1, p2)
            enemigos.append(nuevo_enemigo)
            tiempo_spawn = ahora

    grid = construir_grid(vacios, p1.rect)
    for enemigo in enemigos[:]:
        if hasattr(enemigo, "actualizar_estado"):
            enemigo.actualizar_estado(p1, p2)

        pos_actual = (enemigo.rect.centerx // 30, enemigo.rect.centery // 30)
        pos_jugador2 = (p2.rect.centerx // 30, p2.rect.centery // 30)
        pos_jugador1 = (p1.rect.centerx // 30, p1.rect.centery // 30)

        if not (0 <= pos_actual[0] < 50 and 0 <= pos_actual[1] < 30):
            continue

        if enemigo.estado_actual == "perseguir":
            objetivo = pos_jugador2
        elif enemigo.estado_actual == "evadir":
            objetivo = encontrar_direccion_opuesta(p1.rect, enemigo.rect, grid)
            if objetivo is None:
                objetivo = pos_jugador2
        elif enemigo.estado_actual == "quieto":
            enemigo.path = []
            enemigo.dibujar(screen)
            continue

        if objetivo and 0 <= objetivo[0] < 50 and 0 <= objetivo[1] < 30:
            if (
                ahora - enemigo.ultimo_recalculo > enemigo.recalculo_cada
                or enemigo.ultimo_objetivo != objetivo
            ):
                nuevo_camino = astar(pos_actual, objetivo, grid)
                if nuevo_camino:
                    enemigo.path = nuevo_camino
                    enemigo.path_index = 1
                    enemigo.ultimo_objetivo = objetivo
                    enemigo.ultimo_recalculo = ahora
                else:
                    enemigo.path = []
                    enemigo.path_index = 1
        else:
            enemigo.path = []
            enemigo.path_index = 1

        enemigo.seguir_ruta()
        enemigo.dibujar(screen)

        if enemigo.tocar_jugador(p1.rect):
            enemigos.remove(enemigo)
        if enemigo.tocar_jugador(p2.rect):
            enemigos.remove(enemigo)
            if p2.vidas > 0:
                p2.recibir_atk()
            if p2.vidas == 0:
                run = False

    if ahora - ultimo_spawn_fresa > 6000 and len(fresas) < 20:
        intentos = 0
        while intentos < 100:
            x = random.randint(30, 1400)
            y = random.randint(300, 780)
            grid_x = x // 30
            grid_y = y // 30

            if 0 <= grid_y < len(grid) and 0 <= grid_x < len(grid[0]):
                if grid[grid_y][grid_x] == 0:
                    rect = pygame.Rect(x, y, 30, 30)
                    fresas.append(rect)
                    ultimo_spawn_fresa = ahora
                    break
            intentos += 1

    for fresa in fresas[:]:
        if p2.rect.colliderect(fresa):
            fresas.remove(fresa)
            puntos += 1

        if puntos >= umbral_puntos + 3:
            umbral_puntos += 3

        if umbral_puntos >= umbral_anterior + 3:
            umbral_anterior = int(umbral_puntos)
            vel_ene += 0.5


    for fresa in fresas:
        screen.blit(fresa_sprite, (fresa.x, fresa.y))

    dibujar_puntos(screen, puntos, fresa_sprite)

    if p2.rect.colliderect(p1.rect):
        boost = True
    else:
        boost = False
    
    if len(joysticks) >= 2:
        p2.mover(pygame.key.get_pressed(), boost, screen, vacios, joystick=joysticks[1])
    else:
        p2.mover(pygame.key.get_pressed(), boost, screen, vacios)


    if len(joysticks) >= 1:
        p1.mover(pygame.key.get_pressed(), screen, vacios, joystick=joysticks[0])
    else:
        p1.mover(pygame.key.get_pressed(), screen,  vacios)

    dibujar_vidas(screen, p2)
    pygame.display.flip()

del p2, p1
sys.exit()