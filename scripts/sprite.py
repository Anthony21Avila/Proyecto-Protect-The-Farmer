#Nombre: Anthon Avila
#Matricula: 23-SISN-2-002
import pygame 

#Clase de Spritesheet para que se pueda usar las animaciones de sprites mas facil
class Spritesheet:
    #El inicializador
    def __init__(self, filename):
        self.sprite_sheet = pygame.image.load(filename).convert_alpha()

    #Funcion para buscar los sprites
    def get_sprite(self, x, y, w, h):
        sprite = pygame.Surface((w, h), pygame.SRCALPHA)
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, w, h))
        return sprite