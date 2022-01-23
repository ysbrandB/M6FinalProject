
import sys
sys.path.append("..") # Adds higher directory to python modules path.

from ghost import Ghost
from helpers import find_nearest_passage_to_vector, a_star_search
from settings import tile_size, vertical_tile_number, horizontal_tile_number
from ghosts.blinky import Blinky
from random import randrange
import math
import pygame


def find_scatter_position(passages):
    # scatters to the bottom_right corner
    x = (randrange(0, math.floor(horizontal_tile_number / 2 * tile_size)))
    y = (randrange(math.floor(vertical_tile_number / 2 * tile_size), 2 * math.floor(vertical_tile_number / 2 * tile_size)))
    return find_nearest_passage_to_vector(pygame.math.Vector2(x, y), passages)


class Inky(Ghost):
    def __init__(self, size, grid_position, frames, data, ghost_id):
        # initialize the super class Ghost
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
            target = find_nearest_passage_to_vector(self.position+(self.position-player.position), passages)
            self.path = a_star_search(target, passages, self.grid_position)
        else:
            # inky
            # pathfinds two tiles in front, then subtract blinkys position and multiplies by 2,
            # the adds that to blinkys position, 'sandwiching' the player
            for ghost in ghosts:
                if type(ghost) == Blinky:
                    target = find_nearest_passage_to_vector(
                        ((player.position + player.get_facing_direction() * 2 * tile_size) - ghost.position) * 2 +
                        ghost.position, passages)
                self.path = a_star_search(target, passages, self.grid_position)





