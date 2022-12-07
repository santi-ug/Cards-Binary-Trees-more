import abstract
from pygame.locals import *
import pygame 

class Button(abstract.AbstractObject) :
    # text is referred to as "self.name"
    def __init__(self, text, pos) :
        abstract.AbstractObject.__init__(self, text, pos)
        self.text_color = (255,255,255)
        self.box_color = (205, 92, 92)
        self.font = pygame.font.Font(None,24)
        self.visible = False

    def setDimensions(self, w, h) :
        self.rect.w, self.rect.h = w, h

    def draw(self, screen):
        if self.visible :
            pygame.draw.rect(screen, self.box_color, self.rect, border_radius = 12)
            text = self.font.render(self.name, True, self.text_color)
            screen.blit(text, (self.rect.centerx - text.get_width()/2, self.rect.centery - text.get_height()/2))
