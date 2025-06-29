import pygame

class Player1:
    def __init__(self, sprite_data, spritesheet):
        self.posicionX = 100
        self.posicionY = 550
        self.velocidad = 6
        self.radio = 20
        self.rect = pygame.Rect(self.posicionX - 17, self.posicionY - 17, 35, 35)

        self.sprite_data = sprite_data["jugador1"]
        self.spritesheet = spritesheet
        self.direction = "abajo"
        self.frame_index = 0
        self.frame_delay = 10
        self.frame_counter = 0
    
    def crear(self, screen):
        self.draw(screen)
    
    def mover(self, keys, screen, vacios, joystick=None):
        eje_x, eje_y = 0, 0

        if joystick:
            eje_x = joystick.get_axis(0)
            eje_y = joystick.get_axis(1)

        movio = False
        old_x, old_y = self.posicionX, self.posicionY

        if keys[pygame.K_w] or eje_y < -0.5:
            self.posicionY -= self.velocidad
            self.direction = "arriba"
            movio = True
        elif keys[pygame.K_s] or eje_y > 0.5:
            self.posicionY += self.velocidad
            self.direction = "abajo"
            movio = True
        elif keys[pygame.K_a] or eje_x < -0.5:
            self.posicionX -= self.velocidad
            self.direction = "izquierda"
            movio = True
        elif keys[pygame.K_d] or eje_x > 0.5:
            self.posicionX += self.velocidad
            self.direction = "derecha"
            movio = True

        self.rect.left = self.posicionX - 17
        self.rect.top = self.posicionY - 17

        for v in vacios:
            if self.rect.colliderect(v):
                self.posicionX = old_x
                self.posicionY = old_y
                self.rect.topleft = (self.posicionX - 17, self.posicionY - 17)
                break

        if movio:
            self.animar()
        else:
            self.frame_index = 1

        self.draw(screen)
        self.limit()

    def draw(self, screen):
        frame = self.sprite_data[self.direction][self.frame_index]
        sprite = self.spritesheet.get_sprite(frame["x"], frame["y"], frame["w"], frame["h"])
        screen.blit(sprite, (self.rect.left, self.rect.top))

    def animar(self):
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_index = (self.frame_index + 1) % len(self.sprite_data[self.direction])
            self.frame_counter = 0

    def limit(self):
        self.posicionX = max(50, min(self.posicionX, 1420))
        self.posicionY = max(320, min(self.posicionY, 800))

class Player2(Player1):
    def __init__(self, sprite_data, spritesheet):
        super().__init__(sprite_data, spritesheet)
        self.vidas = 3
        self.posicionX = 60
        self.posicionY = 550
        self.radio = 20
        self.velocidad = 3
        self.ultimo_atk = 0
        self.cooldown_atk = 5000
        self.boost_speed = 5
        self.rect = pygame.Rect(self.posicionX - 17, self.posicionY - 17, 35, 35)
        self.sprite_data = sprite_data["jugador2"]


    def crear(self, screen):
        self.draw(screen)

    def mover(self, keys, boost_activo, screen, vacios, joystick=None):

        if joystick:
            eje_x = joystick.get_axis(0)
            eje_y = joystick.get_axis(1)
        else:
            eje_x = 0
            eje_y = 0

        velocidad_actual = self.boost_speed if boost_activo else self.velocidad
        movio = False
        old_x, old_y = self.posicionX, self.posicionY

        if keys[pygame.K_UP] or eje_y < -0.5:
            self.posicionY -= velocidad_actual
            self.direction = "arriba"
            movio = True
        elif keys[pygame.K_DOWN] or eje_y > 0.5:
            self.posicionY += velocidad_actual
            self.direction = "abajo"
            movio = True
        elif keys[pygame.K_LEFT] or eje_x < -0.5:
            self.posicionX -= velocidad_actual
            self.direction = "izquierda"
            movio = True
        elif keys[pygame.K_RIGHT] or eje_x > 0.5:
            self.posicionX += velocidad_actual
            self.direction = "derecha"
            movio = True
        
        self.rect.left = self.posicionX - 17
        self.rect.top = self.posicionY - 17

        for v in vacios:
            if self.rect.colliderect(v):
                self.posicionX = old_x
                self.posicionY = old_y
                self.rect.topleft = (self.posicionX - 17, self.posicionY - 17)
                break

        if movio:
            self.animar()
        else:
            self.frame_index = 1

        self.draw(screen)
        self.limit()

    def boost(self, objeto):
        return self.rect.colliderect(objeto)
    
    def puede_recibir_atk(self):
        return pygame.time.get_ticks() - self.ultimo_atk > self.cooldown_atk

    def recibir_atk(self):
        if self.puede_recibir_atk() and self.vidas > 0:
            self.vidas -= 1
            self.ultimo_danio = pygame.time.get_ticks()