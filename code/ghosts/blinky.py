import sys
sys.path.append("..") # Adds higher directory to python modules path.

from ghost import Ghost
from helpers import find_nearest_passage_to_vector, a_star_search
from settings import tile_size, vertical_tile_number, horizontal_tile_number
from random import randrange
import math
import pygame


def find_scatter_position(passages):
    # scatters to the top_left corner
    x = (randrange(0, math.floor(horizontal_tile_number / 2 * tile_size)))
    y = (randrange(0, math.floor(vertical_tile_number / 2 * tile_size)))
    return find_nearest_passage_to_vector(pygame.math.Vector2(x, y), passages)


class Blinky(Ghost):
    def __init__(self, size, grid_position, frames, data, ghost_id):
        # initialize the super class animatable tile
        super().__init__(size, grid_position, frames, data, ghost_id)

    def search_path(self, player, passages, ghosts):
        # decide the target based on the state of the ghost, and search the path to it.
        if self.state == self.DEAD:
            target = find_nearest_passage_to_vector(self.origin, passages)
            self.path = a_star_search(target, passages, self.grid_position)
        elif self.state == self.SPREADING:
            target = find_scatter_position(passages)
            self.path = a_star_search(target, passages, self.grid_position)
        elif self.state == self.SCARED:
            target = self.find_scare_position(passages, player)
            self.path = a_star_search(target, passages, self.grid_position)
        else:
            self.path = a_star_search(player, passages, self.grid_position)
