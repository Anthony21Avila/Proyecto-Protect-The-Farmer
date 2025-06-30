#Nombre: Anthon Avila
#Matricula: 23-SISN-2-002

#Importa librerias y de otros scrips
import pygame, sys, json, random, math, os
from scripts.sprite import Spritesheet
from scripts.players import Player1, Player2
from scripts.enemigos import *
from scripts.record import *

#Inicializamos variables que vamos a utilizar, ademas de cargar ciertos elementos como sprites, iconos, fondo y de mas
pygame.init()
pygame.joystick.init()

altura = 900
ancho = 1500
pygame.mixer.init()
screen = pygame.display.set_mode((ancho, altura))
pygame.display.set_caption("Protect The Farmer")
pygame.display.set_icon(pygame.image.load("assets/images/icono.png"))
clock = pygame.time.Clock()
fondo = pygame.transform.scale(pygame.image.load('assets/images/background.png'), (ancho, altura))
fondo_menu = pygame.transform.scale(pygame.image.load('assets/images/portada.png'), (ancho, altura))
corazon_imagen = corazon_imagen = pygame.transform.scale(pygame.image.load("assets/images/corazones.png").convert_alpha(), (30, 30))
fersa = pygame.image.load("assets/images/fresa.png").convert_alpha()

with open("scripts/sprite_data.json") as f:
    sprite_data = json.load(f)

spritesheet = Spritesheet("assets/images/1.png")

joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for joystick in joysticks:
    joystick.init()
    print(f"Joystick {joystick.get_id()} conectado: {joystick.get_name()}")

slash = pygame.mixer.Sound("assets/sounds/Slash.ogg")
hit = pygame.mixer.Sound("assets/sounds/Hit.ogg")
inv = pygame.mixer.Sound("assets/sounds/Inv.ogg")
slash_frames = []
for i in range(1, 8):
    img = pygame.image.load(f"assets/images/slash/AxeSlashEffect ({i}).png").convert_alpha()
    slash_frames.append(pygame.transform.scale(img, (60, 60)))



#Menu principal
def Menu():
    font = pygame.font.SysFont(None, 46)
    font_titulo = pygame.font.SysFont(None, 72)
    menu = True
    clock = pygame.time.Clock()
    seleccion = None

    # Botones
    iniciar_btn = pygame.Rect(ancho // 2 - 100, 300, 200, 60)
    salir_btn = pygame.Rect(ancho // 2 - 100, 400, 200, 60)

    # Cargar sprites animados
    frame_index1 = 0
    frame_index2 = 0
    frame_timer = 0
    frame_delay = 10

    frames_p1 = sprite_data["jugador1"]["abajo"]
    frames_p2 = sprite_data["jugador2"]["abajo"]

    #LLamamos nuestro records
    top = obtener_top5()
    top_scores = []
    for i, record in enumerate(top):
        linea = f"{record['nombre']} - {record['puntos']}"
        top_scores.append(linea)
    max_caracteres = 10

    #Cargamos la musica
    pygame.mixer.music.load("assets/music/Menu.ogg")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    #While del menu
    while menu:
        clock.tick(60)
        screen.fill((0, 0, 0))
        screen.blit(fondo_menu, (0, 0))

        #Dibuja los botones
        pygame.draw.rect(screen, (100, 100, 255), iniciar_btn)
        pygame.draw.rect(screen, (255, 100, 100), salir_btn)

        text_iniciar = font.render("Iniciar", True, (255, 255, 255))
        text_salir = font.render("Salir", True, (255, 255, 255))
        screen.blit(text_iniciar, (iniciar_btn.x + 60, iniciar_btn.y + 15))
        screen.blit(text_salir, (salir_btn.x + 70, salir_btn.y + 15))

        #Dibujar el Titulo
        titulo = font_titulo.render("Protect The Farmer", True, (255, 255, 0))
        screen.blit(titulo, (ancho // 2 - titulo.get_width() // 2, 100))

        #Dibujamos los Records
        rect_fondo = pygame.Surface((400, 250), pygame.SRCALPHA)
        rect_fondo.fill((0, 0, 0, 120))
        screen.blit(rect_fondo, (40, 540))
        screen.blit(font.render("Top 5 Récords:", True, (255, 255, 255)), (50, 550))
        for i, score in enumerate(top_scores):
            nombre, puntos = score.split(" - ")
            if len(nombre) > max_caracteres:
                nombre = nombre[:max_caracteres - 3] + "..."
            linea = font.render(f"{i+1}. {nombre} - {puntos} pts", True, (255, 255, 255))
            screen.blit(linea, (50, 590 + i * 30))

        #Animar y mostrar sprites
        frame_timer += 1
        if frame_timer >= frame_delay:
            frame_index1 = (frame_index1 + 1) % len(frames_p1)
            frame_index2 = (frame_index2 + 1) % len(frames_p2)
            frame_timer = 0

        frame1 = spritesheet.get_sprite(**frames_p1[frame_index1])
        frame2 = spritesheet.get_sprite(**frames_p2[frame_index2])
        screen.blit(frame1, (ancho - 120, altura - 100))
        screen.blit(frame2, (ancho - 60, altura - 100))

        pygame.display.flip()

        #Captamos los eventos que ocurran
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if iniciar_btn.collidepoint(event.pos):
                    seleccion = "jugar"
                elif salir_btn.collidepoint(event.pos):
                    seleccion = "salir"

            #Soporte para los mandos
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    seleccion = "jugar"
                elif event.button == 1:
                    seleccion = "salir"

        if seleccion:
            pygame.mixer.Sound("assets/sounds/Choise.ogg").play()
            pygame.mixer.music.stop()
            pygame.display.flip()
            pygame.time.delay(2000)

            if seleccion == "jugar":
                menu = False
            elif seleccion == "salir":
                pygame.quit()
                sys.exit()

#Genera una posición aleatoria valida para enemigos o fresas
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

#Construye una grilla logica o matriz 30x50 para representar el mapa del juego
def construir_grid(vacios, p1r):
    filas, columnas = 30, 50
    grid = [[0 for _ in range(columnas)] for _ in range(filas)]

    for v in vacios:
        x1 = v.left // 30
        y1 = v.top // 30
        w = math.ceil(v.width / 30)
        h = math.ceil(v.height / 30)
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

#Muentra las vidas y las ubica en la parte superior de la pantalla
def dibujar_vidas(screen, jugador):
    for i in range(jugador.vidas):
        x = 650 + i * (corazon_imagen.get_width() + 10)
        y = 20
        screen.blit(corazon_imagen, (x, y))

#Para cargar los sprites del slash
def cargar_sprites_slash(ruta, cantidad):
    spritesheet = pygame.image.load(ruta).convert_alpha()
    ancho_total, alto = spritesheet.get_size()
    ancho_frame = ancho_total // cantidad
    frames = []
    for i in range(cantidad):
        frame = spritesheet.subsurface(pygame.Rect(i * ancho_frame, 0, ancho_frame, alto))
        frames.append(pygame.transform.scale(frame, (60, 60)))
    return frames

#Para la animacion del slash
def crear_animacion_slash(x, y, lista_animaciones):
    anim = {
        "pos": (x - 30, y - 30),  # centrado
        "frame": 0,
        "tiempo": pygame.time.get_ticks()
    }
    lista_animaciones.append(anim)

#Dibuja un icono y los puntos que a conseguido el jugador hasta el momento
def dibujar_puntos(screen, puntos, fresa_sprite):
    font = pygame.font.SysFont(None, 36)
    texto = font.render(str(puntos), True, (255, 255, 255))

    ancho = screen.get_width()
    screen.blit(fresa_sprite, (ancho - 80, 20))
    screen.blit(texto, (ancho - 40, 25))

def Play():
    #Inicializamos a ambos jugadores y les pasamos sus sprites y el spritesheet
    p1 = Player1(sprite_data, spritesheet)
    p2 = Player2(sprite_data, spritesheet)

    run = True

    p1.crear(screen)
    p2.crear(screen)

    #iniciamos vacios que restringiran a los jugadores y enemigos, ademas de colocar otras varaibles que usaremos 
    # como para registrar una lista de enemigo, los puntos que aparecen en el mapa y algunos limite o conficiones
    vacios = [pygame.Rect(210, 300, 180, 180), pygame.Rect(1110, 300, 180, 180), pygame.Rect(660, 480, 180, 180), pygame.Rect(210, 660, 180, 180), pygame.Rect(1110, 660, 180, 180)]

    animaciones_slash = []
    enemigos = []
    tiempo_spawn = pygame.time.get_ticks()
    tiempo_entre_enemigos = 3000
    MAX_ENEMIGOS = 7

    fresas = []
    ultimo_spawn_fresa = pygame.time.get_ticks()
    puntos, umbral_puntos, umbral_anterior = 0, 0, 0
    fresa_sprite = fresa_sprite = pygame.transform.scale(pygame.image.load("assets/images/fresa.png").convert_alpha(), (30, 30))
    vel_ene = 2

    #Detenemos la musica del menu y empezamos esta
    pygame.mixer.music.stop()
    pygame.mixer.music.load("assets/music/Main.ogg")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    #El While donde se ejecutara el juego
    while run:
        #Capturamos todos los eventos que ocurran en pygame
        for event in pygame.event.get():

            #Indicamos si el jugador presiona la X para salir del programa vuelva nuestro run en False y finalice el while
            if event.type == pygame.QUIT:
                run = False

        #Pintamos el fondo de negro, pasamos la imagen de fondo y asignamos los fps a 60
        screen.fill((0,0,0))
        screen.blit(fondo, (0,0))
        clock.tick(60)

        #Presentamos los vacios en pantalla
        for v in vacios:
            pygame.draw.rect(screen, (20, 20, 20), v)

        #Asignamos un tiempo para comprar en los siguientes if
        ahora = pygame.time.get_ticks()
        if ahora - tiempo_spawn > tiempo_entre_enemigos and len(enemigos) < MAX_ENEMIGOS:

            #Validamos que sea posible generar en estas areas un enemigo y lo añadimos a nuestra lista de enemigos
            #Ademas de hacer una comparacion de tiempo para que no genere enemigos sin parar
            x, y = generar_posicion_valida(vacios, ancho, altura, p1, p2)
            if x is not None and y is not None:
                nuevo_enemigo = Enemigo(x, y, sprite_data, spritesheet, vel_ene)
                nuevo_enemigo.grid = grid
                nuevo_enemigo.vacios = vacios
                crear_estados_enemigo(nuevo_enemigo, p1, p2)
                enemigos.append(nuevo_enemigo)
                tiempo_spawn = ahora

        #Pedimos una matriz para permitir realizar una ruta para los enemigos y posteriormente comprobar sus estados
        grid = construir_grid(vacios, p1.rect)
        for enemigo in enemigos[:]:
            if hasattr(enemigo, "actualizar_estado"):
                enemigo.actualizar_estado(p1, p2)

            pos_actual = (enemigo.rect.centerx // 30, enemigo.rect.centery // 30)
            pos_jugador2 = (p2.rect.centerx // 30, p2.rect.centery // 30)

            if not (0 <= pos_actual[0] < 50 and 0 <= pos_actual[1] < 30):
                continue
            
            #Buscamos los estados de los enemigos para asignar el que le corresponda segun la situacion
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
            
            #Comprobamos si hay un enemigo en el limite dle grip y se calcula la ruta solo si paso suficiente 
            #tiempo o si el objetivo cambio de lugar
            if objetivo and 0 <= objetivo[0] < 50 and 0 <= objetivo[1] < 30:
                if (
                    ahora - enemigo.ultimo_recalculo > enemigo.recalculo_cada
                    or enemigo.ultimo_objetivo != objetivo
                ):
                    #Se actualiza la ruta llamando al A*, pero en caso de no encontrar camino se pasara una ruta vacia
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
                #Si el objetivo no es valido se limpia tambien la ruta
                enemigo.path = []
                enemigo.path_index = 1

            #Se ejecuta la ruta de los enemigos y se dibujan en pantalla
            enemigo.seguir_ruta()
            enemigo.dibujar(screen)

            #Si el enemigo toca al Player1 (O al reves) se elimina el enemigo
            if enemigo.tocar_jugador(p1.rect):
                enemigos.remove(enemigo)
                slash.play()
                crear_animacion_slash(enemigo.rect.centerx, enemigo.rect.centery, animaciones_slash)
            
            #Si el enemigo toca al Player2 se elimina y llama una funcion para reducir la vida en 1 y
            #Dar invulnerabilidad temporalmente a Player2, pero si las vidas pasan a 0 termina el while
            if enemigo.tocar_jugador(p2.rect):
                if p2.vidas > 0:
                    p2.recibir_atk(inv, hit)
                if p2.vidas == 0:
                    inv.stop
                    run = False

        #Limita el tiempo para que aparesca una fresa y la cantidad maxima de estas (siendo 20 el maximo)
        #Ademas de hacer que las mismas aparescan en un area posible con una cantidad de intentos maxima
        if ahora - ultimo_spawn_fresa > 6000 and len(fresas) < 20:
            intentos = 0
            while intentos < 100:
                x = random.randint(30, 1400)
                y = random.randint(300, 780)
                grid_x = x // 30
                grid_y = y // 30

                if grid[grid_y][grid_x] == 0:
                    rect = pygame.Rect(x, y, 30, 30)
                    #Se añadio un chequeo extra que habia olvidado para la generacion de fresas
                    if not any(rect.colliderect(v) for v in vacios):
                        fresas.append(rect)
                        ultimo_spawn_fresa = ahora
                        break
                intentos += 1

        #Comprobamos si el Player2 toca las fresas para eliminarlas, ademas de aumenta los puntos y de paso
        #Incrementar aumentar la velocidad base de los enemigos (jejeje...)
        for fresa in fresas[:]:
            if p2.rect.colliderect(fresa):
                fresas.remove(fresa)
                puntos += 1

            if puntos >= umbral_puntos + 3:
                umbral_puntos += 3

            if umbral_puntos >= umbral_anterior + 3:
                umbral_anterior = int(umbral_puntos)
                vel_ene += 0.5

        #Dibujamos las fresas y los puntos
        for fresa in fresas:
            screen.blit(fresa_sprite, (fresa.x, fresa.y))
        dibujar_puntos(screen, puntos, fresa_sprite)

        #Verificamos si el Player 1 y 2 se tocan para activar el boost de velocidad para el 2
        if p2.rect.colliderect(p1.rect):
            boost = True
        else:
            boost = False
        
        #Verificamos si hay un joystick 2 para enviar la direccion a la que se mueva el mismno
        #si es que se mueve, en todo caso se puede utilizar teclado
        if len(joysticks) >= 2:
            p2.mover(pygame.key.get_pressed(), boost, screen, vacios, joystick=joysticks[1])
        else:
            p2.mover(pygame.key.get_pressed(), boost, screen, vacios)

        #Lo mismo de arriba pero para el jugador 1 y sin mandar un boost
        if len(joysticks) >= 1:
            p1.mover(pygame.key.get_pressed(), screen, vacios, joystick=joysticks[0])
        else:
            p1.mover(pygame.key.get_pressed(), screen,  vacios)

        dibujar_vidas(screen, p2)

        for anim in animaciones_slash[:]:
            frame = anim["frame"]
            if frame < len(slash_frames):
                screen.blit(slash_frames[frame], anim["pos"])
                if pygame.time.get_ticks() - anim["tiempo"] > 50:
                    anim["frame"] += 1
                    anim["tiempo"] = pygame.time.get_ticks()
            else:
                animaciones_slash.remove(anim)

        pygame.display.flip()

    del p2, p1
    game_over(puntos)

#Nuestra pantala de Game Over
def game_over(puntos):
    pygame.init()
    font_titulo = pygame.font.SysFont(None, 72)
    font = pygame.font.SysFont(None, 46)
    input_font = pygame.font.SysFont(None, 40)

    nombre = ""

    escribiendo = True
    clock = pygame.time.Clock()

    pygame.mixer.music.stop()
    pygame.mixer.music.load("assets/music/Game-Over.ogg")
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play()

    while escribiendo:
        screen.fill((0, 0, 0))
        
        #Texto de Game Over
        titulo = font_titulo.render("¡Game Over!", True, (255, 0, 0))
        screen.blit(titulo, (ancho // 2 - titulo.get_width() // 2, 100))

        #Puntaje obtenidos en la partida
        texto_puntos = font.render(f"Tu puntaje: {puntos} pts", True, (255, 255, 255))
        screen.blit(texto_puntos, (ancho // 2 - texto_puntos.get_width() // 2, 200))

        #Pedimos el nombre
        screen.blit(font.render("Ingresa tu nombre:", True, (255, 255, 255)), (ancho // 2 - 150, 300))
        input_box = pygame.Rect(ancho // 2 - 150, 350, 300, 50)
        pygame.draw.rect(screen, (255, 255, 255), input_box, 2)
        texto_input = input_font.render(nombre, True, (255, 255, 255))
        screen.blit(texto_input, (input_box.x + 10, input_box.y + 10))

        #Le decimos que presione Enter o A para guardar
        texto = font.render("Presiona A (o Enter) para guardar", True, (180, 180, 180))
        texto_rect = texto.get_rect(center=(ancho // 2, 420))
        screen.blit(texto, texto_rect)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if nombre.strip():  #Asegura que no este vacio
                        agregar_record(nombre.strip(), puntos)
                    escribiendo = False  #Salimos al menu
                elif event.key == pygame.K_BACKSPACE:
                    nombre = nombre[:-1]
                elif len(nombre) < 15 and event.unicode.isprintable():
                    nombre += event.unicode
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    if nombre.strip():
                        agregar_record(nombre.strip(), puntos)
                    escribiendo = False
                elif event.button == 1:
                    nombre = nombre[:-1]
                elif len(nombre) < 15 and event.unicode.isprintable():
                    nombre += event.unicode

    #Volver al menu
    Menu()

Menu()
Play()
sys.exit()