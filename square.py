from math import sqrt
import pygame
from constants import *
from imagecache import singleton_image_cache

def productivity(num_workers):
    ''' A square produces resources proportunal to the sqrt of the number of
    workers on the square.''' 
    return sqrt(num_workers)

def fromString(abbrev):
    ''' Return the Square constructor associated with the given letter.'''
    return {
        'G': Grass,
        'T': Tree,
        'S': Stream,
        'F': Farm,
        'H': House,
        'M': Mine,
        'Gr': Grave,
    }[abbrev]()

class Square:
    def __init__(self):
        # squares are unworked by default.
        self.num_workers = 0   
        self.font = pygame.font.SysFont("arial", 28)
        

    def paint(self, x, y, width, height):
        screen = pygame.display.get_surface()
        grass = singleton_image_cache.get("grass.png")

        screen.blit(grass, (x, y))
        if self.get_img_name() is not None:
            image = singleton_image_cache.get(self.get_img_name())
            leftPadding = (width - image.get_width())/2
            topPadding = (height - image.get_height())/2
            screen.blit(image, (x + leftPadding, y + topPadding))
        
        # if the square is workable, display the number of workers on it.
        if self.workable() and self.num_workers > 0:
            worker_text = self.font.render(str(self.num_workers), True, (0,0,0))
            screen.blit(worker_text, (x,y))
            
    def get_img_name(self):
        abstract  # this isn't implemented for an abstract Square.

    def worked(self):
        return self.num_workers != 0

    def workable(self):    abstract
    def buildable(self):   abstract
    def produce(self):     abstract
    def destroyable(self): abstract

class Grave(Square):
    def workable(self):
        return False
    def buildable(self):
        return False
    def produce(self):
        return {}
    def destroyable(self):
        return False
    def get_img_name(self):
        return 'grave.png'

class Nature(Square):
    def workable(self):
        return True

    def destroyable(self):
        return False

class Grass(Nature):
    def buildable(self):
        return True
    
    def get_img_name(self):
        return None #'grass.png'
        
    def workable(self):
        return False

    def produce(self):
        return {}
    
class Tree(Nature):
    def buildable(self):
        return False

    def get_img_name(self):
        return 'tree.png'

    def produce(self):
        return {'Wood': 0.1*productivity(self.num_workers)}

class Stream(Nature):
    def buildable(self):
        return False

    def get_img_name(self):
        return 'stream.png'

    def produce(self):
        ''' Streams produce gold more slowly.'''
        return {'Gold': 0.07*productivity(self.num_workers)}

class Building(Square):
    def buildable(self):
        return False

    def workable(self):
        return True

    def destroyable(self):
        return True

class House(Building):
    def get_img_name(self):
        return 'house.png'

    def workable(self):
        return False

    def produce(self):
        return {}

class Farm(Building):
    def get_img_name(self):
        return 'farm.png'
        
    def workable(self):
        return True

    def produce(self):
        ''' A farm produces some food.'''
        return {'Food': 0.05*productivity(self.num_workers)}

class Mine(Building):
    def get_img_name(self):
        return 'mine.png'
        
    def workable(self):
        return True

    def produce(self):
        ''' Mines produce gold quickly.'''
        return {'Gold': 0.1*productivity(self.num_workers)}

