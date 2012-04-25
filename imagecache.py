import pygame

class ImageCache:
    ''' Make it so we only load images once.  Store previously loaded images in a map.'''

    prefix = 'img/'

    def __init__(self):
        self.image_map = {}

    def get(self, img_name):
        ''' Load an image by name. If it has been previously loaded, return the
        data.  If it hasn't, then load the file with that name.'''
        if img_name not in self.image_map:
            full_name = ImageCache.prefix + img_name
            self.image_map[img_name] = pygame.image.load(full_name)
        return self.image_map[img_name]

   # def remove(self, img_name):
   #     ''' this isn't needed right now.'''

singleton_image_cache = ImageCache()

