import pygame, sys, json, random
from scripts.sprite import Spritesheet
from scripts.players import Player1, Player2
from scripts.enemigos import Enemigo, astar

pygame.init()
pygame.joystick.init()

altura = 900
ancho = 1500
screen = pygame.display.set_mode((ancho, altura))
pygame.display.set_caption("Protect The Farmer")
clock = pygame.time.Clock()
fondo = pygame.image.load('assets/images/background.png')
fondo = pygame.transform.scale(fondo, (ancho, altura))

transparente = (0,0,0, 100)

with open("scripts/sprite_data.json") as f:
    sprite_data = json.load(f)

spritesheet = Spritesheet("assets/images/1.png")

joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for joystick in joysticks:
    joystick.init()
    print(f"Joystick {joystick.get_id()} conectado: {joystick.get_name()}")


def construir_grid(vacios, p1r, p2r):
    filas, columnas = 30, 50
    grid = [[0 for _ in range(columnas)] for _ in range(filas)]

    for v in vacios:
        x1 = v.left // 30
        y1 = v.top // 30
        w = v.width // 30
        h = v.height // 30
        for i in range(w):
            for j in range(h):
                grid[y1 + j][x1 + i] = 1

    px = p1r.centerx // 30
    py = p1r.centery // 30
    tx = p2r.centerx // 30
    ty = p2r.centery // 30

    if (px, py) != (tx, ty) and 0 <= px < columnas and 0 <= py < filas:
        grid[py][px] = 1

    return grid

p1 = Player1(sprite_data, spritesheet)
p2 = Player2(sprite_data, spritesheet)

run = True

p1.crear(screen)
p2.crear(screen)

vacios = [pygame.Rect(200, 320, 200, 200), pygame.Rect(1100, 320, 200, 200), pygame.Rect(650, 470, 200, 200), pygame.Rect(200, 600, 200, 200), pygame.Rect(1100, 600, 200, 200)]

enemigos = []
tiempo_spawn = pygame.time.get_ticks()
tiempo_entre_enemigos = 3000
MAX_ENEMIGOS = 7


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
        nuevo_enemigo = Enemigo(random.randint(50, 1420), random.randint(320, 800), sprite_data, spritesheet) 
        enemigos.append(nuevo_enemigo)
        tiempo_spawn = ahora

    grid = construir_grid(vacios, p1.rect, p2.rect)
    for enemigo in enemigos[:]:
        ahora = pygame.time.get_ticks()
        pos_actual = (enemigo.rect.centerx // 30, enemigo.rect.centery // 30)
        pos_objetivo = (p2.rect.centerx // 30, p2.rect.centery // 30)

        if not (0 <= pos_actual[0] < 50 and 0 <= pos_actual[1] < 30):
            continue
        if not (0 <= pos_objetivo[0] < 50 and 0 <= pos_objetivo[1] < 30):
            continue

        if grid[pos_actual[1]][pos_actual[0]] == 1 or grid[pos_objetivo[1]][pos_objetivo[0]] == 1:
            continue

        if ahora - enemigo.ultimo_recalculo > enemigo.recalculo_cada or enemigo.ultimo_objetivo != pos_objetivo:
            enemigo.path = astar(pos_actual, pos_objetivo, grid) or []
            enemigo.path_index = 1
            enemigo.ultimo_objetivo = pos_objetivo
            enemigo.ultimo_recalculo = ahora

        enemigo.seguir_ruta()
        enemigo.dibujar(screen)

        if enemigo.tocar_jugador(p1.rect):
            enemigos.remove(enemigo)

            
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

    pygame.display.flip()

sys.exit()