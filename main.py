import pygame, sys, json
from scripts.sprite import Spritesheet
from scripts.players import Player1, Player2
pygame.init()
pygame.joystick.init()

altura = 900
ancho = 1500
screen = pygame.display.set_mode((ancho, altura))
pygame.display.set_caption("Protect The Farmer")
clock = pygame.time.Clock()
fondo = pygame.image.load("assets\images\fondo.png")
fondo = pygame.transform.scale(fondo, (ancho, altura))

transparente = (0,0,0, 100)

with open("scripts/sprite_data.json") as f:
    sprite_data = json.load(f)

spritesheet = Spritesheet("assets/images/1.png")

joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for joystick in joysticks:
    joystick.init()
    print(f"Joystick {joystick.get_id()} conectado: {joystick.get_name()}")

p1 = Player1(sprite_data, spritesheet)
p2 = Player2(sprite_data, spritesheet)

run = True

p1.crear(screen)
p2.crear(screen)

while run:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            run = False

    
    screen.fill((0,0,0))
    screen.blit(fondo, (0,0))
    clock.tick(60)


    if p2.rect.colliderect(p1.rect):
        boost = True
    else:
        boost = False
    
    if len(joysticks) >= 2:
        p2.mover(pygame.key.get_pressed(), boost, screen, joystick=joysticks[1])
    else:
        p2.mover(pygame.key.get_pressed(), boost, screen)


    if len(joysticks) >= 1:
        p1.mover(pygame.key.get_pressed(), screen, joystick=joysticks[0])
    else:
        p1.mover(pygame.key.get_pressed(), screen)

    pygame.display.flip()

sys.exit()